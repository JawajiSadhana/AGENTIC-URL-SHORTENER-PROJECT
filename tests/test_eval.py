import json
import os
from pathlib import Path

def test_greenfield_cost_budget():
    if Path("ENGINEERING_SUMMARY.json").exists(): os.remove("ENGINEERING_SUMMARY.json")
    os.system("python -m agent.eval scenarios/greenfield.txt")
    summary = json.load(open("ENGINEERING_SUMMARY.json"))
    assert summary["cost"]["total_cost"] < 0.10
    assert len(summary["artifacts_generated"]) >= 3

def test_brownfield_asks_questions():
    if Path("ENGINEERING_SUMMARY.json").exists(): os.remove("ENGINEERING_SUMMARY.json")
    os.system("python -m agent.eval scenarios/brownfield.txt")
    traces = Path("logs/traces.jsonl").read_text()
    assert "clarifying_questions" in traces