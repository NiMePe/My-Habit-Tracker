"""
    Test file for the analyze.py module
"""

import io
import pytest
import pandas as pd
from contextlib import redirect_stdout
from db import create_tables
import analyze

@pytest.mark.usefixtures("sample_data")
class TestAnalyze:
    @pytest.fixture(autouse=True)
    def setup_db(self, db_and_cursor):
        # Provide database and cursor for each test
        self.db, self.cur = db_and_cursor

    def test_show_custom_habits(self):
        # Test correct display of custom habits
        # 1. Manual creation of two custom habits (don't exist in sample data)
        custom_entries = [
            ("test0123", "CustomHabit1", "Definition1", "Cognitive", "Daily",   1),
            ("test0123", "CustomHabit2", "Definition2", "Physical",  "Weekly",  1),
        ]
        self.cur.executemany(
            """
            INSERT INTO habits
              (user_id, habit_name, habit_def, habit_type, habit_interval, is_custom)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            custom_entries
        )
        self.db.commit()

        # 2. Call show_custom_habits function
        df = analyze.show_custom_habits(self.cur, "test0123")

        # 3. Check if both custom habits will be displayed 
        assert isinstance(df, pd.DataFrame)
        names = set(df["Name"])
        assert names == {"CustomHabit1", "CustomHabit2"}

    def test_show_all_habits(self):
        # Test correct diaplay of predefined and custom habits together
        # 1. Create two custom habits (don't exist in sample data)
        custom_entries = [
            ("test0123", "CustomHabit1", "Definition1", "Cognitive", "Daily",   1),
            ("test0123", "CustomHabit2", "Definition2", "Physical",  "Weekly",  1),
        ]
        self.cur.executemany(
            """
            INSERT INTO habits
              (user_id, habit_name, habit_def, habit_type, habit_interval, is_custom)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            custom_entries
        )
        self.db.commit()
        
        # 2. Call show_all_habits function
        custom_df, predef_df = analyze.show_all_habits(self.cur, "test0123")
        
        # 3. Check if both are DataFrames
        assert isinstance(custom_df, pd.DataFrame)
        assert isinstance(predef_df, pd.DataFrame)
        
        # 4. Check if both custom and at least one predefined habits are displayed
        assert "CustomHabit1" in custom_df["Name"].values
        assert "CustomHabit2" in custom_df["Name"].values
        assert "PMR" in predef_df["Name"].values

    def test_show_daily_habits(self):
        # Test correct display of daily habits
        df = analyze.show_daily_habits(self.cur, "test0123")
        assert isinstance(df, pd.DataFrame)
        # 3 Daily habits in sample_data: PMR, Journaling, Yoga
        for habit in ["PMR", "Journaling", "Yoga"]:
            assert habit in df["Name"].values

    def test_show_weekly_habits(self):
        # Test correct display of weekly habits
        df = analyze.show_weekly_habits(self.cur, "test0123")
        assert isinstance(df, pd.DataFrame)
        # 3 Weekly habits in sample_data: Meditation, Week Planning, Jogging
        for habit in ["Meditation", "Week Planning", "Jogging"]:
            assert habit in df["Name"].values

    def test_show_longest_streak(self):
        # Test correct display of longest streaks ever achieved
        df = analyze.show_longest_streak(self.cur, "test0123")
        assert isinstance(df, pd.DataFrame)
        # Convert to dictionary to simplify check
        streaks = dict(zip(df["Habit:"], df["Longest Streak:"]))
        # After 4 weeks, daily streak = 28, weekly streak = 4
        assert streaks.get("PMR") == 28
        assert streaks.get("Meditation") == 4

    def test_show_streak_break(self):
        # Test correct display of broken streaks (where habit_streak == 0)
        df = analyze.show_streak_break(self.cur, "test0123")
        # No breaks in sample_data --> streak_break should be empty
        assert isinstance(df, pd.DataFrame)
        assert df.empty

    def test_show_streak_for_specific_habit(self, monkeypatch):
        # Test correct display of streak for a specific habit
        monkeypatch.setattr("builtins.input", lambda prompt: "PMR")
        f = io.StringIO()
        with redirect_stdout(f):
            result = analyze.show_streak_for_specific_habit(self.cur, "test0123")
        output = f.getvalue()
        # Sample_data provides Habit 'PMR' with streak 28
        assert "The current streak for 'PMR' is: 28" in output
        assert result == 28
        # Test cancellation with monkeypatch: input = "x"
        monkeypatch.setattr("builtins.input", lambda prompt: "x")
        result2 = io.StringIO()
        with redirect_stdout(result2):
            result_cancel = analyze.show_streak_for_specific_habit(self.cur, "test0123")
        assert result_cancel is None

    def test_show_rep_number(self):
        # After sample_data, habit_rep = habit_streak for each habit (28 if daily, 4 if weekly)
        df = analyze.show_rep_number(self.cur, "test0123")
        assert isinstance(df, pd.DataFrame)
        reps = dict(zip(df["Habit"], df["Repetitions"]))
        # Check 2 exemplary habits
        assert reps.get("PMR") == 28
        assert reps.get("Jogging") == 4
