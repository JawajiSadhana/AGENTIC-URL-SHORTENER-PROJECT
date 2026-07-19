import json, os
from openai import OpenAI
from dotenv import load_dotenv
from agent.cost import cost_tracker, BUDGET_LIMIT

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PLANNER_PROMPT = """
You are a senior software engineering planner.
Output ONLY valid JSON: {"intent": str, "requirement": str, "tasks": [{"tool": str, "args": {}}], "risks": [str], "questions": [str]}
Tools: file_write, code_edit, code_search, shell, test_runner, llm_query
Rules:
1. If requirement mentions "already have" or "modify" or "migrate", FIRST ask 2-3 clarifying questions in "questions" field and leave "tasks" empty.
2. Use llm_query with task_type="search" for codebase search. Uses gpt-4o-mini cheap.
3. Use llm_query with task_type="reasoning" for design, architecture + code generation. Uses gpt-4o expensive.
4. When creating file_write or code_edit tasks, "args" MUST include full working code in "content" field. No placeholders.
5. For URL shortener: Generate FastAPI + sqlite3 + slowapi rate limiting + analytics. 3 files: app/main.py, app/db.py, requirements.txt
Respond ONLY JSON.
"""

class LLM:
    def call(self, prompt: str, task_type="reasoning") -> dict:
        if cost_tracker.total_cost >= BUDGET_LIMIT:
            return {"intent": "budget_exceeded", "tasks": [], "risks": ["Budget limit hit"], "questions": []}

        model = "gpt-4o" if task_type == "reasoning" else "gpt-4o-mini"

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "system", "content": PLANNER_PROMPT}, {"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.2
            )
            usage = response.usage
            cost_tracker.log(f"llm_call_{task_type}", model, usage.prompt_tokens, usage.completion_tokens)

            plan = json.loads(response.choices[0].message.content)
            plan["requirement"] = prompt
            if "questions" not in plan: plan["questions"] = []
            return plan
        except Exception as e:
            return {"intent": "error", "tasks": [], "risks": [str(e)], "questions": []}

llm = LLM()