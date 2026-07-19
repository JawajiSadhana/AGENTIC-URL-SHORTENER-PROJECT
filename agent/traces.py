import json, time, uuid
from pathlib import Path
Path("logs").mkdir(exist_ok=True)
def log(step, data, parent_id=None):
    trace_id = str(uuid.uuid4())
    open("logs/traces.jsonl","a").write(json.dumps({"id": trace_id, "parent_id": parent_id, "ts": time.time(), "step": step, "data": data})+"\n")
    return trace_id