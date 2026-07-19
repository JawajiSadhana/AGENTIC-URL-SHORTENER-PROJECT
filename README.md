# Agentic URL Shortener Engineer

Generates REAL FastAPI + SQLite URL Shortener with Persistent DAG Memory

## Setup
pip install -r requirements.txt

## Generate App
python -m agent.eval scenarios/greenfield.txt

## Run App
uvicorn app.main:app --reload

## Test
POST http://localhost:8000/shorten?long_url=https://google.com
GET http://localhost:8000/{short_id}

## Evaluation
pytest -v

## Replay Traces
python -m agent.replay

## Check DAG in Memory
sqlite3 agent_state.db "SELECT step, parent_id, status FROM memory"