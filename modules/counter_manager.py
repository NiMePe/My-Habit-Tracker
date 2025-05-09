"""
    File that contains helper functions to manage the database connection and
    user interaction with the counter of the habit tracker.
    Functions will be called in the counter class.
"""

import sqlite3
from datetime import datetime, timedelta
from analyze import show_predef_habits, show_custom_habits
from db import add_counter

### Functions defining the update of the repetition and the streak counters
def increment_streak(cur, db, habit_name, user_id, manual=True):
    """
        Function that increments the streak counter of a habit with 
        respect to manual vs automatic increment
    """
    # Only prompt when called manually
    if manual:
        print("\nWith this option you can manually increment a streak.")
        print("Note: Use this option only if a habit check was forgotten.")
       
        # Display all habits
        predef_df = show_predef_habits(cur)           
        custom_df = show_custom_habits(cur, user_id) 
        if predef_df.empty and custom_df.empty:
            print("\nNo habits were found.")
            return

        # Make habit names in lower-case for comparisons with lower-case user input
        names = list(predef_df["Name"].values) + list(custom_df["Name"].values)
        names_lower = [n.lower() for n in names]        

        # User input: Enter habit name
        while True:
            user_input = input("\nEnter the name of the habit you want to increment the streak for or type 'x' to cancel: ").strip()
            if user_input.lower() == 'x':
                print("Action was cancelled. Returning to menu.")
                return
            # Map input back to original-cased habit name
            if user_input.lower() in names_lower:
                habit_name = names[names_lower.index(user_input.lower())]
                break
            print("Invalid habit name. Please enter a valid habit name from the list.")

    # Setup current date   
    now = datetime.now()
    check_date = now.strftime('%Y-%m-%d')  # Current date
    check_time = now.strftime('%H:%M:%S')  # Current time

    # Get last streak value for manual=TRUE (incl. today), else: date < today
    if manual:
        cur.execute("""SELECT habit_streak, check_date FROM counter WHERE habit_name = ? AND user_id = ?
                    AND check_date <= date('now') ORDER BY check_date DESC LIMIT 1""", 
                    (habit_name, user_id)
                    )
    else:
        cur.execute("""SELECT habit_streak, check_date FROM counter WHERE habit_name = ? 
                    AND user_id = ? AND check_date < ? ORDER BY check_date DESC LIMIT 1""",
                    (habit_name, user_id, check_date)
                    )

    last_record = cur.fetchone()

    if last_record:
        last_streak, last_date = last_record
        last_date = datetime.strptime(last_date, "%Y-%m-%d").date()
    else:
        last_streak, last_date = 0, None

    # Find out the habit's interval
    cur.execute("SELECT habit_interval FROM habits WHERE habit_name = ? AND (user_id = ? OR is_custom = 0)", (habit_name, user_id))
    interval = cur.fetchone()

    # Update streak counter according to the habit's interval
    # Manual: Multiple streak increments at the same day possible:
    if manual:
         new_streak = last_streak + 1
    # Automatic increment: Interval (daily vs. weekly) check:
    elif interval and interval[0] == "Weekly" and last_date and last_date >= now.date() - timedelta(days=7):
        new_streak = last_streak + 1
    elif interval and interval[0] == "Daily"  and last_date and last_date >= now.date() - timedelta(days=1):
        new_streak = last_streak + 1
    else:
        new_streak = 1
    
    # Update streak counter directly if manual or call add_counter function from db.py if automatic
    try:
        if manual:
            # Manual Increment: streak +=1
            cur.execute(
                """
                INSERT INTO counter (user_id, habit_name, check_date, check_time, habit_rep, habit_streak) 
                VALUES (?, ?, ?, ?, 0, ?) ON CONFLICT(user_id, habit_name, check_date) DO UPDATE
                SET habit_streak = excluded.habit_streak
                """, (user_id, habit_name, check_date, check_time, new_streak)
            )
            db.commit()
            print(f"***The streak for '{habit_name}' has been manually set to {new_streak}.***")
            
            # Manual Increment: Update max streak
            cur.execute(
                "UPDATE habits "
                "   SET max_streak = CASE WHEN max_streak < ? THEN ? ELSE max_streak END "
                " WHERE user_id = ? AND habit_name = ?",
                (new_streak, new_streak, user_id, habit_name)
            )
            db.commit()            
            
        else:
            # Automatic Increment: Called in check_habit and in increment_counter
            add_counter(cur, db, user_id, habit_name, check_date, check_time, 0, new_streak)
            print(f"***The streak for '{habit_name}' has been incremented to {new_streak}.***")
            
            # Automatic Increment: Update max streak
            cur.execute(
                "UPDATE habits "
                "   SET max_streak = CASE WHEN max_streak < ? THEN ? ELSE max_streak END "
                " WHERE user_id = ? AND habit_name = ?",
                (new_streak, new_streak, user_id, habit_name)
            )
            db.commit()
            
    except sqlite3.Error as e:
        db.rollback()
        print(f"An error occurred while incrementing streak for '{habit_name}': {e}")

def increment_counter(cur, db, habit_name, user_id, manual=True):
    """
        Function that increments the streak counter and the number of repetions in case
        of automatic incrementing
    """
    # Only prompt when called manually
    if manual:    
        print("\nWith this option you can manually increment a counter.")
        print("Note: Use this option only if a habit check was forgotten.")

        #Display all habits
        predef_df = show_predef_habits(cur)           
        custom_df = show_custom_habits(cur, user_id) 
        if predef_df.empty and custom_df.empty:
            print("\nNo habits were found.")
            return

        # Make habit names in lower-case for comparisons with lower-case user input
        names = list(predef_df["Name"].values) + list(custom_df["Name"].values)
        names_lower = [n.lower() for n in names]        

        # User input: Enter habit name
        while True:
            user_input = input("\nEnter the name of the habit you want to increment the counter for or type 'x' to cancel: ").strip()
            if user_input.lower() == 'x':
                print("Action was cancelled. Returning to menu.")
                return
            # Map input back to original-cased habit name
            if user_input.lower() in names_lower:
                habit_name = names[names_lower.index(user_input.lower())]
                break
            print("Invalid habit name. Please enter a valid habit name from the list.")

    # Setup current date   
    now = datetime.now()
    check_date = now.strftime('%Y-%m-%d')  # Current date
    check_time = now.strftime('%H:%M:%S')  # Current time

    # Validate if the habit exists in habits table
    cur.execute(
        "SELECT 1 FROM habits WHERE habit_name = ? AND (user_id = ? OR is_custom = 0)",
        (habit_name, user_id)
    )  
    if not cur.fetchone():
        print(f"The habit '{habit_name}' does not exist.")
        return  

    # Check the last repetition value from today
    cur.execute("""
        SELECT habit_rep, check_date FROM counter WHERE habit_name = ? AND user_id = ? 
        ORDER BY check_date DESC LIMIT 1""",
        (habit_name, user_id)
        )
    last_rep = cur.fetchone()

    if last_rep and last_rep[1] == check_date:
        new_rep = last_rep[0] + 1
    else:
        new_rep = 1

    # Update repetition counter directly if manual or call add_counter function from db.py if automatic
    try:
        if manual:
            # Manual Increment: repetition counter +=1
            cur.execute("""
                INSERT INTO counter (user_id, habit_name, check_date, check_time, habit_rep, habit_streak) 
                VALUES (?, ?, ?, ?, ?, 0) ON CONFLICT(user_id, habit_name, check_date) DO UPDATE
                SET habit_rep = excluded.habit_rep
                """,(user_id, habit_name, check_date, check_time, new_rep)
            )
            db.commit()
            print(f"***The number of repetitions of '{habit_name}' has been manually set to {new_rep}.***")
        else:
            # Automatic Increment: Call add_counter from db.py and increment_streak
            add_counter(cur, db, user_id, habit_name, check_date, check_time, new_rep, 0)
            print(f"***The number of repetitions of '{habit_name}' has been successfully incremented to {new_rep}.***")
            increment_streak(cur, db, habit_name, user_id, manual=False)
            
    except sqlite3.Error as e:
        db.rollback()
        print(f"Error while incrementing counter for '{habit_name}': {e}")


### Function to mark a habit as checked & automatically update counters
def check_habit(cur, db, user_id):
    """
        Function that lets the user check a given habit. 
        It detects a possible streak break, automatically 
        increments the repetition counter and the streak counter.
    """
    print("\nWith this option you can mark a habit as checked.")
    print("\nNote: The repetition counter and the streak will be updated automatically.")

    try:
        # 1. Display all habits
        predef_df = show_predef_habits(cur)           
        custom_df = show_custom_habits(cur, user_id) 
        if predef_df.empty and custom_df.empty:
            print("\nNo habits were found to check.")
            return

        # 2. Make habit names in lower-case for comparison with lower-cased user input
        names = list(predef_df["Name"].values) + list(custom_df["Name"].values)
        names_lower = [n.lower() for n in names]        

        # 3. Ask user for habit name
        while True:
            user_input = input("\nEnter the name of the habit you want to check or type 'x' to cancel: ").strip()
            if user_input.lower() == 'x':
                print("Action was cancelled. Returning to menu.")
                return
            # Map input back to original-cased habit name
            if user_input.lower() in names_lower:
                habit_name = names[names_lower.index(user_input.lower())]
                break
            print("Invalid habit name. Please enter a valid habit name from the list.")

        # 4. Fetch habit interval from database
        cur.execute(
            "SELECT habit_interval FROM habits WHERE habit_name = ? AND (user_id = ? OR is_custom = 0)",
            (habit_name, user_id)
        )
        row = cur.fetchone()
        if not row:
            print(f"Habit '{habit_name}' not found in database.")
            return
        habit_interval = row[0]

        # 5. Setup current date
        now = datetime.now()
        check_date = now.strftime('%Y-%m-%d')  # Current date
        check_time = now.strftime('%H:%M:%S')  # Current time
        
        # 6. Make counter entry only when habit entry exists (foreign key check)
        cur.execute(
            "SELECT 1 FROM habits WHERE user_id = ? AND habit_name = ?",
            (user_id, habit_name)
        )
        if not cur.fetchone():
            cur.execute(       
                """
                INSERT INTO habits (
                    user_id, habit_name, habit_def,
                    habit_type, habit_interval, is_custom
                )
                SELECT ?, habit_name, habit_def,
                       habit_type, habit_interval, 0
                  FROM habits
                 WHERE is_custom = 0
                   AND habit_name = ?
                """,
                (user_id, habit_name)
            )
            db.commit()

        # 7. Ask user for confirmation of habit period
        if habit_interval == "Daily":
            print(f"Did you practice '{habit_name}' today ({check_date})?") 
            check_input = input("Please type 'Y' for yes or 'N' for no: ").lower()
        elif habit_interval == "Weekly":
            print(f"Did you practice '{habit_name}' in the past week or today ({check_date})?")
            check_input = input("Please type 'Y' for yes or 'N' for no: ").lower()
        else:
            raise ValueError("Invalid periodicity. Neither 'Daily' nor 'Weekly'.")


        if check_input == "y": 
        # 8. Make sure: Only 1 check per day/week
            cur.execute(
            "SELECT check_date FROM counter WHERE user_id = ? AND habit_name = ? "
            "ORDER BY check_date DESC LIMIT 1",
            (user_id, habit_name)
            )
            last = cur.fetchone()
            if last:
                last_date = datetime.strptime(last[0], "%Y-%m-%d").date()
                if habit_interval == "Daily" and last_date == now.date():
                    print(f"You've already checked '{habit_name}' today. "
                          "It is not possible to check it more than once per day.")
                    return
                if habit_interval == "Weekly" and last_date >= now.date() - timedelta(days=7):
                    print(f"You've already checked '{habit_name}' this week. "
                          "If you need more granularity, please change the habit interval in menu 2-3.")
                    return

        # 9. Automatic streak‑break detection with eventual streak reset to 0
            cur.execute(
                "SELECT check_date FROM counter WHERE habit_name = ? AND user_id = ? "
                "ORDER BY check_date DESC LIMIT 1",
                (habit_name, user_id)
            )
            last = cur.fetchone()
            if last:
                last_date = datetime.strptime(last[0], '%Y-%m-%d').date()
                if ((habit_interval == "Daily" and last_date < now.date() - timedelta(days=1)) or
                    (habit_interval == "Weekly" and last_date < now.date() - timedelta(days=7))):
                    print(f"The streak for '{habit_name}' was broken. Resetting streak counter to 0.")
                    cur.execute(
                        "UPDATE counter SET habit_streak = 0 "
                        "WHERE habit_name = ? AND user_id = ? AND check_date = ?",
                        (habit_name, user_id, last[0])
                    )
                    db.commit()

        # 10. Call increment_counter function to increment counter & streak
            increment_counter(cur, db, habit_name, user_id, manual=False)
            print(f"***The habit '{habit_name}' was successfully marked as checked.***")

        else:
            print(f"The habit '{habit_name}' was not marked as checked.")

    except sqlite3.Error as e:
        db.rollback()
        print(f"An error occurred while checking a habit: {e}")


### Functions to manually reset the streak or repetion counter of a given habit
def reset_streak(cur, db, habit_name, user_id):
    """
        Function to allow manual reset of the streak of a given habit by the user
    """
    print("\nWith this option you can reset a habit's streak counter to 0")
    try:
        # Display habits
        predef_df = show_predef_habits(cur)           
        custom_df = show_custom_habits(cur, user_id) 
        if predef_df.empty and custom_df.empty:
            print("\nNo habits were found to reset the streak.")
            return

        # Make habit names in lower-case for comparisons with lower-case user input
        names = list(predef_df["Name"].values) + list(custom_df["Name"].values)
        names_lower = [n.lower() for n in names]

        # Ask user if they want to reset streak manually
        while True:
            print("\nWould you like to manually reset a streak?") 
            manual_reset = input("Please type 'Y' for yes and 'N' for no: ").strip().lower()
            if manual_reset == 'y':
                user_input = input("\nPlease enter the name of the habit you want to reset the streak for or type 'x' to cancel: ").strip()
                if user_input.lower() == 'x':
                    print("Action was cancelled. Returning to menu.")
                    return
                if user_input.lower() in names_lower:
                    # Map back to original casing
                    idx = names_lower.index(user_input.lower())
                    habit_name = names[idx] 
                    
                    # Reset the most recent record, keep history
                    cur.execute(
                        """
                        UPDATE counter
                           SET habit_streak = 0
                         WHERE rowid = (
                             SELECT rowid
                               FROM counter
                              WHERE user_id = ? AND habit_name = ?
                              ORDER BY check_date DESC, check_time DESC
                              LIMIT 1
                         )
                        """, (user_id, habit_name)
                    )
                    db.commit()                   
                    
                    print(f"***The streak for '{habit_name}' has been successfully reset to 0.***")
                    return
                else:
                    print("Invalid habit name. Please choose a habit from the list.")
            elif manual_reset == 'n':
                print("No streaks were reset.")
                return
            else:
                print("Please enter 'Y' or 'N'.")

    except sqlite3.Error as e:
        db.rollback()
        print(f"An error occurred while resetting streak for '{habit_name}': {e}")

        
def reset_rep(cur, db, user_id):
    """
        Function to allow manual reset of the repetition counter of a given habit by the user
    """
    print("\nWith this option you can reset a habit's repetition counter to 0.")
    try:
        # Display habits
        predef_df = show_predef_habits(cur)           
        custom_df = show_custom_habits(cur, user_id) 
        if predef_df.empty and custom_df.empty:
            print("\nNo habits were found to manually reset the repetition counter.")
            return

        # Make habit names in lower-case for comparisons with lower-case user input
        names = list(predef_df["Name"].values) + list(custom_df["Name"].values)
        names_lower = [n.lower() for n in names]        

        # Ask the user if they want to reset the repetition counter manually
        while True:
            print("\nWould you like to manually reset the repetition counter?")
            manual_reset = input("Please type 'Y' for yes and 'N' for no: ").strip().lower()
            if manual_reset == 'y':
                user_input = input(
                    "\nPlease enter the name of the habit for which you want to reset the repetition counter"
                    " or type 'x' to cancel: "
                ).strip()
                if user_input.lower() == 'x':
                    print("Action was cancelled. Returning to menu.")
                    return
                if user_input.lower() in names_lower:
                    # Map back to original casing
                    idx = names_lower.index(user_input.lower())
                    habit_name = names[idx]
                    
                    # Reset Counter
                    cur.execute(
                        "UPDATE counter SET habit_rep = 0 WHERE habit_name = ? AND user_id = ?",
                        (habit_name, user_id)
                    )
                    db.commit()
                    print(f"***The repetition counter for '{habit_name}' has been successfully reset to 0.***")
                    return
                else:
                    print("Invalid habit name. Please choose a habit from the list.")
            elif manual_reset == 'n':
                print("The repetition counter was not reset.")
                return
            else:
                print("Please enter 'Y' or 'N'.")
    except sqlite3.Error as e:
        db.rollback()
        print(f"An error occurred while resetting repetition counter for '{habit_name}': {e}")
