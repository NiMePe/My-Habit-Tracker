"""
    Test file for db.py module
"""

import sqlite3
import pytest
import datetime
import db

class TestDB:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, tmp_path):
        # Setup and teardown the test scenario
        # Create a temporary database for testing db module functions
        self.db_file = tmp_path / "test_db.db"
        self.db = sqlite3.connect(str(self.db_file))
        self.cur = self.db.cursor()
        yield
        self.db.close()
    
    def test_create_tables(self):
        # Test if creation of tables works
        db.create_tables(self.cur, self.db)
        self.cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in self.cur.fetchall()]
        # Check if user, habits and counter table were created
        assert 'user' in tables
        assert 'habits' in tables
        assert 'counter' in tables

    def test_initialize_db(self):
        # Test if database initialization works
        db.create_tables(self.cur, self.db)
        db.initialize_db(self.cur, self.db)
        # Check if there are 6 predefined habits
        self.cur.execute("SELECT COUNT(*) FROM habits WHERE is_custom = 0")
        count = self.cur.fetchone()[0]
        assert count == 6
        
    def test_insert_user(self):
        # Test if user data gets inserted into database
        # Prepare test: Create tables and test user data
        db.create_tables(self.cur, self.db)
        self.cur.execute(
            "INSERT OR IGNORE INTO user (user_id, user_name, user_pwd) VALUES (?, ?, ?)",
            ("test0101", "testuser", "pwd123!")
        )
        self.db.commit()
        self.cur.execute("SELECT * FROM user WHERE user_id = 'test0101'")
        result = self.cur.fetchone()
        # Check that user table is not empty
        assert result is not None        

    def test_add_counter(self):
        # Test insertion of counter entries in database
        # 1. Prepare test: Create tables, a test user and a test habit
        db.create_tables(self.cur, self.db)
        self.cur.execute("INSERT INTO user (user_id, user_name, user_pwd) VALUES (?, ?, ?)",
                         ("test0123", "testuser", "pa$$word123"))
        self.cur.execute(
            """INSERT INTO habits (user_id, habit_name, habit_def, habit_type, habit_date, habit_interval, is_custom) 
               VALUES (?, ?, ?, ?, date('now'), ?, 1)""",
            ("test0123", "TestHabit", "desc", "type", "Daily")
        )
        self.db.commit()

        # 2. Define test parameters
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        current_time = datetime.datetime.now().strftime('%H:%M:%S')
        
        # 3. Call add_counter for the first time –> should insert a record
        db.add_counter(self.cur, self.db, "test0123", "TestHabit", today, current_time, 1, 1)
        self.cur.execute(
            """SELECT habit_rep, habit_streak FROM counter 
               WHERE user_id = ? AND habit_name = ? AND check_date = ?""",
            ("test0123", "TestHabit", today)
        )
        result = self.cur.fetchone()
        assert result is not None # Make sure, an entry was inserted
        assert result[0] == 1 and result[1] == 1 # Make sure habit_rep = 1 and habit_streak = 1

        # 4. Calling add_counter a second time with the same parameters 
        # Due to ON CONFLICT... DO UPDATE... clause in add_counter 
        # --> there should be no duplicate and no second line but an updated entry
        db.add_counter(self.cur, self.db, "test0123", "TestHabit", today, current_time, 1, 1)
        self.cur.execute(
            """SELECT COUNT(*) FROM counter 
               WHERE user_id = ? AND habit_name = ? AND check_date = ?""",
            ("test0123", "TestHabit", today)
        )
        count = self.cur.fetchone()[0]
        assert count == 1 # Make sure, no second entry was inserted (only update of 1st entry intended)
