"""
    Test file for the habit.py module 
"""
    
import sqlite3
import pytest
from db import create_tables
from habit import Habit
from datetime import datetime

class TestHabit:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, tmp_path):
        # Setup and teardown of the test scenario
        db_file = tmp_path / "test_habit.db"
        self.db = sqlite3.connect(str(db_file))
        self.cur = self.db.cursor()
        create_tables(self.cur, self.db)
        # Insert a test user record since habits table depends on a user as foreign key
        self.cur.execute("INSERT INTO user (user_id, user_name, user_pwd) VALUES (?, ?, ?)",
                         ("test0123", "testuser", "pa$$word123"))
        self.db.commit()
        yield
        self.db.close()
    
    def test_create_predef_habits(self):
        # Test creation/insertion of predefined habits in database
        habit_instance = Habit(self.db, "test0123", "", "", "", datetime.now(), "Daily")
        habit_instance.create_predef_habits()
        self.cur.execute("SELECT COUNT(*) FROM habits")
        count = self.cur.fetchone()[0]
        # All 6 predefined habits should have been inserted
        assert count == 6
    
    def test_create_custom_habits(self, monkeypatch):
        # Test creation of custom habits
        # Simulate input for creating a custom habit with monkeypatch
        inputs = iter([
            "y",                     # proceed yes/no
            "CustomHabit",           # name
            "A test custom habit.",  # Definition
            "Cognitive",             # type
            "d"                      # interval ('d' = daily)
        ])
        monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))
        habit_instance = Habit(self.db, "test0123", "", "", "", datetime.now(), "Daily")
        habit_instance.create_custom_habits()
        
        # Verify that the custom habit "CustomHabit" was inserted into the database
        # Habit manager function calls .title(), so the saved name is "Customhabit"
        expected = "CustomHabit".title()
        self.cur.execute(
            "SELECT * FROM habits WHERE habit_name = ? AND is_custom = 1",
            (expected,)
        )
        result = self.cur.fetchone()
        assert result is not None
    
    def test_delete_habit(self, monkeypatch):
        # Test habit deletion
        # 1. Create a custom habit "DeleteHabit" using monkeypatch
        inputs_create = iter(["DeleteHabit", "A habit to delete", "Cognitive", "d"])
        monkeypatch.setattr("builtins.input", lambda prompt: next(inputs_create))
        habit_instance = Habit(self.db, "test0123", "", "", "", datetime.now(), "Daily")
        habit_instance.create_custom_habits()
        
        # 2. Check that DeleteHabit was inserted into the database (.title() -> "Deletehabit")
        expected = "DeleteHabit".title()
        self.cur.execute("SELECT * FROM habits WHERE habit_name = ?", (expected,))
        result = self.cur.fetchone()
        assert result is None
        
        # 3. Simulate user's confirmation input for deletion
        inputs = iter(["y", "deletehabit", "y"])
        monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))
        habit_instance.delete_habit()
        
        # 4. After deletion should be no more "DeleteHabit"
        self.cur.execute("SELECT COUNT(*) FROM habits WHERE is_custom = 1")
        count = self.cur.fetchone()[0]
        # 5. Database is now empty where "DeleteHabit" was
        assert count == 0 

    def test_edit_habit(self, monkeypatch):
        # Test change of periodicity (daily vs. weekly)
        # 1. Create a custom habit "EditHabit" with monkeypatch
        inputs_create = iter([
            "y",                  # proceed yes/no
            "EditHabit",          # habit name
            "A habit to edit",    # definition
            "Cognitive",          # type
            "d"                   # initial interval 'daily'
        ])
        monkeypatch.setattr("builtins.input", lambda prompt: next(inputs_create))
        habit_instance = Habit(self.db, "test0123", "", "", "", datetime.now(), "Daily")
        habit_instance.create_custom_habits()
        
        # 2. Check if EditHabit was correctly inserted into database (.title() -> "Edithabit")
        expected = "EditHabit".title()
        self.cur.execute(
            "SELECT habit_interval FROM habits WHERE habit_name = ? AND user_id = ?",
            (expected, "test0123")
        )
        result = self.cur.fetchone()
                # Initially, the interval is "Daily" --> Check interval == Daily
        assert result is not None and result[0] == "Daily"

        # 3. Now simulate input for editing:
        inputs_edit = iter([
            "EditHabit",          # habit name
            "y",                  # confirmation
            "w"                   # new interval 'weekly'
        ])
        monkeypatch.setattr("builtins.input", lambda prompt: next(inputs_edit))
        habit_instance.edit_habit()

        # 4. Verify that the habit's interval is now updated
        self.cur.execute(
            "SELECT habit_interval FROM habits WHERE habit_name = ? AND user_id = ?",
            (expected, "test0123")
        )
        result = self.cur.fetchone()
        # 5. Interval should now be changed to "weekly"
        assert result is not None and result[0] == "Weekly"
