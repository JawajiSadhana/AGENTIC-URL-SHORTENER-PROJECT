import sqlite3, json
from pathlib import Path
Path("agent_state.db")
conn = sqlite3.connect("agent_state.db", check_same_thread=False)
conn.execute("CREATE TABLE IF NOT EXISTS memory(id INTEGER PRIMARY KEY, step TEXT, data TEXT, status TEXT, parent_id TEXT, retry_count INTEGER DEFAULT 0, ts DATETIME DEFAULT CURRENT_TIMESTAMP)")
conn.commit()

def add_memory(step, data_dict, status="pending", parent_id=None):
    conn.execute("INSERT INTO memory(step,data,status,parent_id) VALUES(?,?,?,?)", (step, json.dumps(data_dict), status, parent_id))
    conn.commit()

def update_memory_status(step, status):
    conn.execute("UPDATE memory SET status=? WHERE step=? AND status='pending'", (status, step))
    conn.commit()

def add_retry(step):
    conn.execute("UPDATE memory SET retry_count=retry_count+1 WHERE step=?", (step,))
    conn.commit()

def get_retry_count(step):
    row = conn.execute("SELECT retry_count FROM memory WHERE step=?", (step,)).fetchone()
    return row[0] if row else 0