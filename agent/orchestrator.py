from agent.llm import llm
from agent.executor import TOOLS
from agent.validator import validate_code, validate_prompt
from agent.memory import add_memory, update_memory_status, add_retry, get_retry_count
from agent.traces import log
from agent.guardrails import check_safe
from agent.cost import cost_tracker, MAX_RETRIES, BUDGET_LIMIT
import json, datetime

def write_summary(plan, artifacts):
    summary = {"timestamp": str(datetime.datetime.now()), "requirement": plan.get("requirement"), "plan": plan["tasks"],
               "artifacts_generated": artifacts, "risks": plan["risks"], "cost": cost_tracker.summary(), "budget_limit": BUDGET_LIMIT}
    json.dump(summary, open("ENGINEERING_SUMMARY.json","w"), indent=2)

def run(requirement: str, auto_approve=False):
    run_id = log("run_start", {"req": requirement})
    if not validate_prompt(requirement): return print("BLOCKED")

    log("input", {"req": requirement}, parent_id=run_id)
    plan = llm.call(requirement, task_type="reasoning")
    llm_id = log("llm_call", plan, parent_id=run_id)

    if plan["intent"] == "budget_exceeded": return print("ABORTED: Budget")

    if plan.get("questions"):
        print("\n[CLARIFYING QUESTIONS]")
        for i, q in enumerate(plan["questions"], 1): print(f"{i}. {q}")
        print("Answer these and re-run with updated requirement.\n")
        log("clarifying_questions", {"questions": plan["questions"]}, parent_id=llm_id)
        write_summary(plan, [])
        return

    if not auto_approve:
        print("Approve plan?", [t['tool'] for t in plan["tasks"]], "[y/n]:")
        if input().lower()!= 'y': return

    artifacts = []
    for i, task in enumerate(plan["tasks"]):
        tool, args = task["tool"], task["args"]
        step_id = f"{tool}_{i}"
        add_memory(step_id, {"decision": f"Using {tool}", "args": args}, "pending", parent_id=llm_id)

        if not check_safe(tool, args):
            update_memory_status(step_id, "blocked"); log("blocked", {"tool": tool}, parent_id=llm_id); continue

        tool_id = log("tool_call", {"tool": tool, "args": args}, parent_id=llm_id)
        result = TOOLS[tool](**args)

        if result.get("status") == "failed":
            if get_retry_count(step_id) >= MAX_RETRIES: update_memory_status(step_id, "permanently_failed"); log("max_retry_exceeded", {}, parent_id=tool_id); continue
            add_retry(step_id); update_memory_status(step_id, "failed"); log("tool_failed", result, parent_id=tool_id); continue

        if tool in ["file_write", "code_edit"]:
            is_valid = validate_code(result["path"])
            log("validation", {"path": result["path"], "result": is_valid}, parent_id=tool_id)
            update_memory_status(step_id, "done" if is_valid else "failed")
            if is_valid: artifacts.append(result["path"])
        else:
            update_memory_status(step_id, "done")

    write_summary(plan, artifacts)
    log("run_done", {"artifacts": artifacts, "cost": cost_tracker.total_cost}, parent_id=run_id)
    print(f"Done. Total Cost: ${cost_tracker.total_cost:.5f}")