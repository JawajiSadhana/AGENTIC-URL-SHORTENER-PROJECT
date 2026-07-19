from pathlib import Path
import subprocess, os
from agent.llm import llm

def file_write(path: str, content: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(content)
    return {"status": "ok", "path": path}

def code_edit(path: str, content: str):
    """Overwrite or create file with new content. Used for code generation and edits."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(content)
    return {"status": "ok", "path": path, "action": "edited"}

def code_search(query: str):
    """Search codebase for a query string"""
    result = []
    if not Path("app").exists(): return {"status": "ok", "result": "no matches"}
    for root, dirs, files in os.walk("app"):
        for f in files:
            try:
                if query.lower() in open(os.path.join(root,f)).read().lower():
                    result.append(os.path.join(root,f))
            except: pass
    return {"status": "ok", "result": result if result else "no matches"}

def shell(cmd: str):
    output = subprocess.getoutput(cmd)
    return {"status": "ok", "output": output}

def run_tests():
    """Run pytest and return results"""
    result = subprocess.run(["pytest", "-q"], capture_output=True)
    status = "passed" if result.returncode==0 else "failed"
    return {"status": status, "output": result.stdout.decode()}

def llm_query(prompt: str, task_type: str = "search"):
    result = llm.call(prompt, task_type=task_type)
    return {"status": "ok", "result": result}

TOOLS = {
    "file_write": file_write,
    "code_edit": code_edit,
    "code_search": code_search,
    "shell": shell,
    "test_runner": run_tests,
    "llm_query": llm_query
}