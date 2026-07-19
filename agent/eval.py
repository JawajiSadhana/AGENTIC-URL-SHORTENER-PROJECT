from agent.orchestrator import run
import sys
req = open(sys.argv[1]).read().strip()
print(f"Running scenario: {req}")
run(req, auto_approve=True)