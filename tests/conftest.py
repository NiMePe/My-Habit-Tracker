"""
File used to indicate the correct test folder and to load the sample data.
"""

import sys
import os

# Add modules folder to sys.path to find all non-test modules
modules_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'modules'))
if os.path.isdir(modules_path) and modules_path not in sys.path:
    sys.path.insert(0, modules_path)
    
### Fixture for Sample data (4 week period)

import sqlite3
import pytest
from .fixtures     import load_sample_data
from datetime      import date
from db            import get_db, create_tables, close_db

@pytest.fixture
def db_and_cursor(tmp_path):
    # Create temporary db file and connection
    test_db = tmp_path / "test_db.db"
    conn = sqlite3.connect(str(test_db))
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    create_tables(cur, conn)
    
    # Ensure max_streak column exists
    try:
        cur.execute("ALTER TABLE habits ADD COLUMN max_streak INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        # Column already present
        pass
    conn.commit()

    yield conn, cur
    close_db()

@pytest.fixture
def sample_data(db_and_cursor):
    # Get db and cur
    conn, cur = db_and_cursor
    
    # Insert test user
    cur.execute(
        "INSERT OR IGNORE INTO user (user_id, user_name, user_pwd) VALUES (?, ?, ?)",
        ("test0123", "testuser", "pa$$word123")
    )
    conn.commit()

    # Insert predefined habits
    from habit_manager import create_predef_habits
    create_predef_habits(cur, conn)

    # Bind predefined habits to test user
    cur.execute(
        "UPDATE habits SET user_id = ? WHERE is_custom = 0",
        ("test0123",)
    )
    conn.commit()

    # Load 4 weeks of sample data
    start = date(2025, 4, 1)
    for habit, interval in [
        ("PMR", "Daily"),
        ("Meditation", "Weekly"),
        ("Journaling", "Daily"),
        ("Week Planning", "Weekly"),
        ("Yoga", "Daily"),
        ("Jogging", "Weekly"),
    ]:
        load_sample_data(
            cur,
            conn,
            user_id="test0123",
            habit_name=habit,
            interval=interval,
            start_date=start
        )

    # Populate max_streak for each habit
    for habit in ["PMR", "Meditation", "Journaling", "Week Planning", "Yoga", "Jogging"]:
        cur.execute("""
            UPDATE habits
               SET max_streak = (
                   SELECT MAX(habit_streak)
                     FROM counter
                    WHERE user_id = ? AND habit_name = ?
               )
             WHERE user_id = ? AND habit_name = ?
        """, ("test0123", habit, "test0123", habit))
    conn.commit()

    return conn, cur
