"""
Test file for counter.py module
"""

import sqlite3
import pytest
from db import create_tables
from counter import Counter
# Avoiding simulation of user input by direct import of manager functions (instead of class methods)
from counter_manager import increment_streak as mgr_inc_streak, increment_counter as mgr_inc_counter 

class TestCounter:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, tmp_path):
        # Setup and teardown the test scenario
        db_file = tmp_path / "test_counter.db"
        self.db = sqlite3.connect(str(db_file))
        self.cur = self.db.cursor()
        create_tables(self.cur, self.db)
        # Insert a test user and a test habit into the database for counter tests
        self.cur.execute("INSERT INTO user (user_id, user_name, user_pwd) VALUES (?, ?, ?)",
                         ("test0123", "testuser", "pa$$word123"))
        self.cur.execute("INSERT INTO habits (user_id, habit_name, habit_def, habit_type, habit_date, habit_interval, is_custom) VALUES (?, ?, ?, ?, date('now'), ?, 1)",
                         ("test0123", "TestHabit", "TestDefinition", "TestType", "Daily"))
        self.db.commit()
        yield
        self.db.close()
    
    def test_increment_streak(self):
        # Test if streak incrementation works
        mgr_inc_streak(self.cur, self.db, "TestHabit", "test0123", manual=False)
        self.cur.execute("SELECT habit_streak FROM counter WHERE user_id = ? AND habit_name = ?", ("test0123", "TestHabit"))
        result = self.cur.fetchone()
        # Make sure an entry was inserted
        assert result is not None

    def test_increment_counter(self):
        # Test if repetition counter incrementation works
        mgr_inc_counter(self.cur, self.db, "TestHabit", "test0123", manual=False)
        self.cur.execute("SELECT habit_rep FROM counter WHERE user_id = ? AND habit_name = ?", ("test0123", "TestHabit"))
        result = self.cur.fetchone()
        # Make sure an entry was inserted
        assert result is not None

    def test_reset_streak(self, monkeypatch):
        # Test if streak reset works
        # 1. Insert a data record with streak != 0 --> habit_streak = 3
        self.cur.execute("INSERT INTO counter (user_id, habit_name, check_date, check_time, habit_rep, habit_streak) VALUES (?, ?, date('now'), '12:00:00', 5, 3)",
                         ("test0123", "TestHabit"))
        self.db.commit()
        # 2. Test streak reset to 0
        counter_instance = Counter(self.db, "test0123")
        # 2.1 Simulate Y/N prompt and the habit name prompt with monkeypatch
        monkeypatch.setattr(
            "builtins.input",
            lambda prompt: "y" if "type 'Y'" in prompt or "Type 'Y'" in prompt else "TestHabit"
        )
        counter_instance.reset_streak()
        self.cur.execute("SELECT habit_streak FROM counter WHERE user_id = ? AND habit_name = ?", ("test0123", "TestHabit"))
        result = self.cur.fetchone()
        # 2.2 Check if reset worked --> habit_streak = 0
        assert result[0] == 0

    def test_reset_rep(self, monkeypatch):
        # Test if repetition coutner reset works
        # 1. Insert a data record with repetition counter != 0 --> habit_rep = 5
        self.cur.execute("INSERT INTO counter (user_id, habit_name, check_date, check_time, habit_rep, habit_streak) VALUES (?, ?, date('now'), '12:00:00', 5, 3)",
                         ("test0123", "TestHabit"))
        self.db.commit()
        # 2. Test repetition counter reset to 0
        counter_instance = Counter(self.db, "test0123")
        # 2.1 Simulate Y/N prompt and the habit name prompt with monkeypatch
        monkeypatch.setattr(
            "builtins.input",
            lambda prompt: "y" if "type 'Y'" in prompt or "Type 'Y'" in prompt else "TestHabit"
        )
        counter_instance.reset_rep()
        self.cur.execute("SELECT habit_rep FROM counter WHERE user_id = ? AND habit_name = ?", ("test0123", "TestHabit"))
        result = self.cur.fetchone()
        # 2.2 Check if reset worked
        assert result[0] == 0
