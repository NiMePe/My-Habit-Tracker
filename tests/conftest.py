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
from .fixtures      import load_sample_data
from datetime      import date
from db            import create_tables

@pytest.fixture
def db_and_cursor(tmp_path):
    # Create temporary SQLite file and connection
    db_file = tmp_path / "test_full.db"
    conn = sqlite3.connect(str(db_file))
    cur  = conn.cursor()
    create_tables(cur, conn)
    yield conn, cur
    conn.close()

@pytest.fixture
def sample_data(db_and_cursor):
    # Get db and cur
    db, cur = db_and_cursor
    
    # Insert the six predefined habits into habits table
    from habit_manager import create_predef_habits
    create_predef_habits(cur, db)
    
    # Define start date 2025-04-01
    start = date(2025, 4, 1)
    for habit, interval in [
        ("PMR", "Daily"),
        ("Meditation", "Weekly"),
        ("Journaling", "Daily"),
        ("Week Planning","Weekly"),
        ("Yoga", "Daily"),
        ("Jogging", "Weekly"),
    ]:
        # Call load_sample_data from fixtures.py
        load_sample_data(
            cur, 
            db,
            user_id    = "test0123",
            habit_name = habit,
            interval   = interval,
            start_date = start
        )