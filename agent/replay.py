import json
from pathlib import Path
def replay():
    if not Path("logs/traces.jsonl").exists(): return print("No traces")
    traces = [json.loads(l) for l in open("logs/traces.jsonl")]
    def print_tree(node_id, indent=0):
        node = next(t for t in traces if t["id"]==node_id)
        print(" "*indent + f"[{node['step']}] {str(node['data'])[:80]}")
        for child in [t for t in traces if t.get("parent_id")==node_id]: print_tree(child["id"], indent+1)
    for r in [t for t in traces if t.get("parent_id") is None]: print_tree(r["id"])
if __name__ == "__main__": replay()