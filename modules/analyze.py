"""
    This file contains functions for the logged-in user to analyze their data.
    The user will be able to view all, all custom, and all predefined habits.
    They can filter for daily and for weekly habits.
    The user can also view their streaks and the repetition counter.
    The analyze file makes use of the pandas and sqlite libraries.
"""

import sqlite3
import pandas as pd

#### Functions to show habits according to creator and periodicity

## Functions to display habits depending on their creator (predefined vs. custom vs. all)
def show_predef_habits(cur):
    """Function to display all predefined habits"""
    try:
        # Select predefined habits
        cur.execute("SELECT habit_name, habit_def, habit_type, habit_interval FROM habits WHERE is_custom = 0")
        habits = cur.fetchall()

        if not habits:
            print("\nThere are currently no predefined habits.")
            return pd.DataFrame(columns=["Name","Description","Type","Interval"])

        # Create and return DataFrame
        habits_df = pd.DataFrame(habits, columns=["Name", "Description", "Type", "Interval"])
        print("\n=========================Predefined Habits==============================")
        print(habits_df.to_string(index=False))
        return habits_df
    except sqlite3.Error as e:
        print(f"An error occurred while displaying predefined habits: {e}")
        
        
def show_custom_habits(cur, user_id):
    """Function to display all custom habits for a specific user"""
    try:
        # Select custom habits
        cur.execute(
            "SELECT habit_name, habit_def, habit_type, habit_interval FROM habits WHERE user_id = ? AND is_custom = 1",
            (user_id,)
        )
        habits = cur.fetchall()

        if not habits:
            print("\nThere are currently no custom habits.")
            return pd.DataFrame(columns=["Name","Description","Type","Interval"])

        # Create and return DataFrame
        habits_df = pd.DataFrame(habits, columns=["Name", "Description", "Type", "Interval"])
        print("\n===========================Custom Habits================================")
        print(habits_df.to_string(index=False))
        return habits_df
    except sqlite3.Error as e:
        print(f"An error occurred while retrieving your habits: {e}")
       
    
def show_all_habits(cur, user_id):
    """Function to display all habits (custom and predefined)"""
    try:
        # 1. Show predefined habits
        predef_df = show_predef_habits(cur)
        # Add a Custom column: False for predefined habits
        if not predef_df.empty:
            predef_df["Custom"] = False        
        # 2. Show custom habits
        custom_df = show_custom_habits(cur, user_id)
        # Add a Custom column: True for custom habits
        if not custom_df.empty:
            custom_df["Custom"] = True
        # 3. Return of both DataFrames for further processing if needed
        return custom_df, predef_df 
    except sqlite3.Error as e:
        print(f"An error occurred while displaying all habits: {e}")
        empty = pd.DataFrame(columns=["Name", "Description", "Type", "Interval"])
        return empty, empty
        
        
        
##Functions to display habits depending on their interval (daily vs. weekly)
def show_daily_habits(cur, user_id):
    """Function to return all daily habits (custom and predefined)"""
    try:
        # Select daily habits
        cur.execute(
            """SELECT habit_name, habit_def, habit_type, habit_interval, is_custom FROM habits WHERE 
            (user_id = ? OR is_custom = 0) AND habit_interval = 'Daily'""",
            (user_id,)
        )
        habits = cur.fetchall()
        if not habits:
            print("\nNo daily habits found.")
            return pd.DataFrame(columns=["Name", "Description", "Type", "Interval", "Custom"])
        
        # Display DataFrame
        df = pd.DataFrame(habits, columns=["Name", "Description", "Type", "Interval", "Custom"])
        print("\nHere are your current daily habits:")
        print(df.to_string(index=False))
        return df
    except sqlite3.Error as e:
        print(f"An error occurred while retrieving daily habits: {e}")
        return pd.DataFrame()


def show_weekly_habits(cur, user_id):
    """Function to return all weekly habits (custom and predefined)"""
    try:
        # Select weekly habits
        cur.execute(
            """SELECT habit_name, habit_def, habit_type, habit_interval, is_custom FROM habits WHERE 
            (user_id = ? OR is_custom = 0) AND habit_interval = 'Weekly'""",
            (user_id,)
        )
        habits = cur.fetchall()
        if not habits:
            print("\nNo weekly habits found.")
            return pd.DataFrame(columns=["Name", "Description", "Type", "Interval", "Custom"])
        
        # Display DataFrame
        df = pd.DataFrame(habits, columns=["Name", "Description", "Type", "Interval", "Custom"])
        print("\nHere are your current weekly habits:")
        print(df.to_string(index=False))
        return df
    except sqlite3.Error as e:
        print(f"An error occurred while retrieving weekly habits: {e}")
        return pd.DataFrame()



####Functions to analyze counter data

def show_longest_streak(cur, user_id):
    """Function to display the longest streaks ever of all habits in descending order"""
    try:
        # Select maximum streak
        cur.execute("""SELECT habit_name AS Habit, MAX(habit_streak) AS Streak
                    FROM counter WHERE user_id = ? AND habit_streak > 0
                    AND check_date <= date('now') GROUP BY habit_name
                    ORDER BY Streak DESC""", (user_id,)
                    )
        streaks = cur.fetchall()
        if not streaks:
            print("\nNo streak data available.")
            return pd.DataFrame(columns=["Habit:", "Longest Streak:"])
        
        # Create and return DataFrame
        df = pd.DataFrame(streaks, columns=["Habit:", "Longest Streak:"])
        print("\nHere are your longest streaks ever:")
        print(df.to_string(index=False))
        return df
    except sqlite3.Error as e:
        print(f"An error occurred while retrieving longest streaks: {e}")
        return pd.DataFrame(columns=["Habit:", "Longest Streak:"])

    
def show_streak_break(cur, user_id):
    """Function to display habits with current zero streak"""
    try:        
        # Select zero streak, join habit with counter table
        cur.execute("""SELECT c.habit_name, c.habit_streak FROM counter AS c
                    JOIN (SELECT habit_name, MAX(check_date) AS last_date
                    FROM counter WHERE user_id = ? AND check_date <= date('now')
                    GROUP BY habit_name ) AS ld ON c.habit_name = ld.habit_name
                    AND c.check_date = ld.last_date WHERE c.user_id = ?
                    AND c.habit_streak = 0 """, (user_id, user_id)
                   )
        rows = cur.fetchall()
        if not rows:
            print("\nNo broken streaks found.")
            return pd.DataFrame(columns=["Habit:", "Current Streak:"])
        
        # Build and return DataFrame
        df = pd.DataFrame(rows, columns=["Habit:", "Current Streak:"])
        print("\nHere are the habits with currently broken streaks:")
        print(df.to_string(index=False))
        return df
    except Exception as e:
        print(f"An error occurred while retrieving streak breaks: {e}")
        return pd.DataFrame(columns=["Habit:", "Current Streak:"])

    
def show_streak_for_specific_habit(cur, user_id):
    """Function to display streak data for a specific habit"""
    try:
        # Display all habits
        predef_df = show_predef_habits(cur)           
        custom_df = show_custom_habits(cur, user_id) 
        if predef_df.empty and custom_df.empty:
            print("\nNo habits were found to display a streak for.")
            return
        
        # Make habit names in lower-case for comparisons with lower-case user input
        names = list(custom_df["Name"].values) + list(predef_df["Name"].values)
        names_lower = [n.lower() for n in names]        
        
        # Now user selects a specific habit
        while True:
            user_input = input(
                "\nEnter the name of the habit to see its streak or type 'x' to cancel: "
            ).strip()
            if user_input.lower() == "x":
                print("Action was cancelled. Returning to menu.")
                return None
            if user_input.lower() in names_lower:
                idx = names_lower.index(user_input.lower())
                habit_name = names[idx]
                break
            print("Habit does not exist. Please try again.")
        
        # Get current streak, limit to 1 entry
        cur.execute("""SELECT habit_streak FROM counter WHERE user_id = ?
                    AND habit_name = ? AND check_date <= date('now')
                    ORDER BY check_date DESC, check_time DESC LIMIT 1""",
                    (user_id, habit_name)
                   )            
        result = cur.fetchone()
        if result:
            streak = result[0]
            print(f"The current streak for '{habit_name}' is: {streak}")
            return streak
        else:
            print(f"No streak data was found for '{habit_name}'.")
            return None

    except sqlite3.Error as e:
        print(f"An error occurred while retrieving the streak for '{habit_name}': {e}")
        return None

def show_rep_number(cur, user_id):
    """Function to display the total number of repetitions of a given habit"""
    try:
        # Select sum of habit repetitions, order descending
        cur.execute("""SELECT habit_name, SUM(habit_rep) AS Repetitions
                    FROM counter WHERE user_id = ? GROUP BY habit_name ORDER BY Repetitions DESC""",
                    (user_id,)
                   )
        repetitions = cur.fetchall()
        if not repetitions:
            print("\nNo repetition numbers available.")
            return pd.DataFrame(columns=["Habit", "Repetitions"])
        
        # Create and return DataFrame
        df = pd.DataFrame(repetitions, columns=["Habit", "Repetitions"])
        print("\nHere are your total repetition numbers:")
        print(df.to_string(index=False))
        return df
    except sqlite3.Error as e:
        print(f"An error occurred while retrieving the number of repetitions: {e}")
        return pd.DataFrame()
    
