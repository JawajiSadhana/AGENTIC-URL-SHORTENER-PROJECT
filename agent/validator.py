import re
def validate_prompt(prompt: str) -> bool:
    if re.search(r'sk-[a-zA-Z0-9]{20,}|password\s*=|api_key\s*=|token\s*=', prompt, re.IGNORECASE): return False
    if "rm -rf" in prompt.lower(): return False
    return True
def validate_code(path: str) -> bool:
    try:
        content = open(path).read()
        if "sk-" in content or "password" in content or "rm -rf" in content: return False
        if "main.py" in path and "FastAPI" not in content: return False
        if "db.py" in path and "sqlite3" not in content: return False
        return True
    except: return False