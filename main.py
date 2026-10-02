#!/usr/bin/env python3
"""
Hermes Agent Runner
Handles persistent memory, state cycles, task execution, and automatic backups.
"""

import os
import sys
import time
import json
import sqlite3
from datetime import datetime

DATA_DIR = os.getenv("HERMES_DATA_PATH", "./hermes-data")
STATE_FILE = os.path.join(DATA_DIR, "state.json")
LOG_FILE = os.path.join(DATA_DIR, "activity.log")
DB_FILE = os.path.join(DATA_DIR, "memory.db")


def init_environment():
    """Ensure data directory and database structure exist."""
    os.makedirs(DATA_DIR, exist_ok=True)

    # Initialize SQLite database for memory items if needed
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            category TEXT NOT NULL,
            content TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def load_state():
    """Load agent state from JSON file."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[Warning] Failed to load state: {e}")

    return {
        "cycle_count": 0,
        "last_run": None,
        "status": "initialized",
        "memories_count": 0
    }


def save_state(state):
    """Save agent state to JSON file."""
    state["last_run"] = datetime.now().isoformat()
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def log_activity(message):
    """Log activity with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}\n"
    print(log_line, end="")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_line)


def record_memory(category, content):
    """Record a memory item into SQLite and log file."""
    timestamp = datetime.now().isoformat()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO memories (timestamp, category, content) VALUES (?, ?, ?)",
        (timestamp, category, content)
    )
    conn.commit()
    conn.close()
    log_activity(f"Memory recorded [{category}]: {content}")


def run_agent():
    """Execute Hermes agent tasks."""
    init_environment()
    state = load_state()

    state["cycle_count"] += 1
    log_activity(f"Starting Hermes Agent Run - Cycle #{state['cycle_count']}")

    # Record cycle memory
    record_memory("SYSTEM", f"Started cycle #{state['cycle_count']}")

    # Agent tasks execution simulation
    print("Hermes Agent is processing tasks...")
    time.sleep(1)

    # Update memory count
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM memories")
    state["memories_count"] = cursor.fetchone()[0]
    conn.close()

    state["status"] = "idle"
    save_state(state)
    log_activity(f"Cycle #{state['cycle_count']} completed successfully. Total memories: {state['memories_count']}")


if __name__ == "__main__":
    run_agent()
