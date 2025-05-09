"""
This file contains the main program to guide a user through the habit tracker backend system. 
It makes use of several modules such as:
- counter (for updating habit counters and streaks),
- analyze (for data analysis),
- db (for database operations),
- habit (for habit-related actions),
- user (for user profile management).

The code is organized into separate functions for the different menus and operations.
"""

from counter import Counter
import analyze
from db import get_db, close_db, initialize_db
from habit import Habit
from user import User

# ----------------------------------------
# Step 1: Welcome Screen
# ----------------------------------------
def welcome_menu():
    """Display the welcome screen to the user."""
    print("""
    ****************************************************************************
                           WELCOME TO 'MY HABIT TRACKER'
    ****************************************************************************
    """)
    print("""
    A habit tracker is a tool to help you achieve a personal goal by monitoring 
    the implementation of a new habit.

    My habit tracker is a backend program without a graphical user interface.
    You will be guided through menus by multiple-choice questions.

    The program provides predefined habits from the stress reduction field which 
    you can use for tracking. In addition, you can define your own custom habits.

    Your data will be stored in a local database file, which will then be used to
    analyze your habit tracking data.
    """)

# ----------------------------------------
# Step 2: Database Setup
# ----------------------------------------
def database_needed():
    """
    Check if a database exists and initialize it if necessary.
    Prompts the user to create a new database or exit the program.
    Returns:
        db: database connection object, or None if the user exits.
        cur: database cursor, or None if the user exits.
    """
    print("To use the program, a local database file must be created.")
    print("The program will now check whether a database exists.")
    
    db = get_db() # Connect to the central database
    if not db:
        print("No database connection could be established.")
        while True:
            print("What would you like to do?")
            print("1 = Create a new database")
            print("2 = Exit program")
            db_input = input("Please enter your choice (1 or 2): ").strip()
            if db_input == "1":
                print("Attempting to create a new database...")
                try:
                    db = get_db()
                    if not db:
                        raise Exception("Database creation failed.")
                    cur = db.cursor()
                    # Initialize database
                    initialize_db(cur, db)
                    break
                except Exception as e:
                    print(f"An error occurred while creating a new database: {e}")
                    continue
            elif db_input == "2":
                print("Thanks for participating.\nYou will now exit the program.")
                return None, None
            else:
                print("Invalid input. Please enter '1' or '2'.")
    
    cur = db.cursor()
    try:
        # Check whether the tables already exist
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cur.fetchall()
        if not tables:  # If tables are missing, initialize the database
            print("No tables were found. Initializing database...")
            initialize_db(cur, db)
            print("Database has been successfully created and initialized.")
    except Exception as e:
        print(f"An error occurred while checking the database: {e}. Exiting program.")
        return None, None
    return db, cur

# ----------------------------------------
# Step 3: Login Menu
# ----------------------------------------
def login_user_menu(cur, db):
    """
    Display the login menu where the user can choose to log in,
    create a new profile, or exit the program.
    Returns the user identifier (username or ID) upon successful authentication.
    """
    print("Do you already have a user profile?")
    log_input = input("Yes = 1, No = 2, Exit = 3: ").strip()
    user = User(db)
    if log_input == "1":
        print("""
        **************************************
              LOGIN TO YOUR USER PROFILE
        **************************************
        """)
        user_id = user.user_auth()
        return user_id
    elif log_input == "2":
        print("""
        **************************************
                CREATE A USER PROFILE
        **************************************
        """)
        # 1. Create the profile
        user.create_profile()
        user_id = user.user_id
        return user_id

        # 2. Verify that profile is in database
        cur_db = db.cursor()
        cur_db.execute("SELECT user_id, user_name FROM user WHERE user_id = ?", (user.user_id,))
        saved = cur_db.fetchone()
        if saved:
            print(f"Profile '{saved[1]}' (ID: {saved[0]}) was successfully created and saved.")
        else:
            print("Something went wrong — Profile was not found in the database.")
        return user.user_id
    elif log_input == "3":
        return "Thanks for participating.\nYou will now exit the program."
    else:
        print("Invalid input. Exiting program.")
        return None

# -----------------------------------------------
# Step 4: Main User Menu (after successful login)
# ------------------------------------------------
def main_user_menu():
    """
    Display the main menu with options to view, change, 
    update habits, or change profile.
    """
    
    print("""
    *****************************************
            WELCOME TO THE MAIN MENU
    *****************************************
    """)
    print("""
    Within this menu, you can view, change, or update your habits.
    You can also edit your user profile or exit the program.
    """)
    print("What do you want to do?")
    print("""
    ****************************
      1 VIEW HABITS & STREAKS
    ****************************
    """)
    print("""
    ****************************
          2 CHANGE HABITS
    ****************************
    """)
    print("""
    ****************************
     3 UPDATE HABITS & STREAKS
    ****************************
    """)
    print("""
    ****************************
         4 CHANGE PROFILE
    ****************************
    """)
    print("""
    ****************************
               5 EXIT
    ****************************    
    """)

# ----------------------------------------
# Step 4.1: VIEW HABITS & STREAKS Menu
# ----------------------------------------
def view_habits(cur, user_id):
    """
    Display a submenu for viewing habits and streaks.
    The user can choose which data to display.
    """
    while True:
        print("""
        ******************************************
                  1 VIEW HABITS & STREAKS
        ******************************************
        1. Predefined Habits
        2. Custom Habits
        3. All Habits
        4. Current Daily Habits
        5. Current Weekly Habits
        6. Longest Streak Ever
        7. Current Streak Breaks
        8. Streak for Specific Habit
        9. Total Number of Repetitions
        10. Return to Main Menu
        *****************************************
        """)
        choice = input("Please select an option (1-10): ").strip()
        if choice == "1":
            analyze.show_predef_habits(cur)
        elif choice == "2":
            analyze.show_custom_habits(cur, user_id)
        elif choice == "3":
            analyze.show_all_habits(cur, user_id)
        elif choice == "4":
            analyze.show_daily_habits(cur, user_id)
        elif choice == "5":
            analyze.show_weekly_habits(cur, user_id)
        elif choice == "6":
            analyze.show_longest_streak(cur, user_id)
        elif choice == "7":
            analyze.show_streak_break(cur, user_id)            
        elif choice == "8":
            analyze.show_streak_for_specific_habit(cur, user_id)          
        elif choice == "9":
            analyze.show_rep_number(cur, user_id)
        elif choice == "10":
            print("Returning to the main menu.")
            break
        else:
            print("Invalid input. Please select a number between 1 and 10.")

# ----------------------------------------
# Step 4.2: CHANGE HABITS Menu
# ----------------------------------------
def change_habits(cur, db, user_id):
    """
    Display a submenu for changing habits.
    Options include creating, deleting, or editing habits.
    """
    while True:
        print("""
        *****************************************
                    2 CHANGE HABITS
        *****************************************
        1. Create Custom Habit
        2. Delete Habit
        3. Edit Habit Interval
        4. Return to Main Menu
        *****************************************
        """)
        choice = input("Please select an option (1-4): ").strip()
        if choice == "1":           
            habit_instance = Habit(db, user_id, "", "", "", None, "")
            habit_instance.create_custom_habits()

        elif choice == "2":
            habit_instance = Habit(db, user_id, "", "", "", None, "")
            habit_instance.delete_habit()
        
        elif choice == "3":
            habit_instance = Habit(db, user_id, "", "", "", None, "")
            habit_instance.edit_habit()

        elif choice == "4":
            print("Returning to the main menu.")
            break
            
        else:
            print("Invalid input. Please select a number between 1 and 4.")

# ----------------------------------------
# Step 4.3: UPDATE HABITS & STREAKS Menu
# ----------------------------------------
def update_habits(cur, db, user_id):
    """
    Display a submenu for updating habit data.
    The options include checking a habit, resetting counters, and manually updating streaks.
    """
    while True:
        print("""
        ******************************************
                 3 UPDATE HABITS & STREAKS
        ******************************************
        1. Check a Habit
        2. Reset a Streak
        3. Reset a Repetition Counter
        4. Manually Increment a Streak
        5. Manually Increment a Counter
        6. Return to Main Menu
        *****************************************
        """)
        choice = input("Please select an option (1-6): ").strip()
        counter = Counter(db, user_id)
        
        if choice == "1":
            counter_instance = Counter(db, user_id)
            counter_instance.check_habit()
        
        elif choice == "2":
            counter_instance = Counter(db, user_id)
            counter_instance.reset_streak()
        
        elif choice == "3":
            counter_instance = Counter(db, user_id)
            counter_instance.reset_rep()
        
        elif choice == "4":
            counter_instance = Counter(db, user_id)
            counter_instance.increment_streak()
        
        elif choice == "5":
            counter_instance = Counter(db, user_id)
            counter_instance.increment_counter()

        elif choice == "6":
            print("Returning to the main menu.")
            break
        
        else:
            print("Invalid input. Please select a number between 1 and 6.")

# ----------------------------------------
# Step 4.4: CHANGE PROFILE Menu
# ----------------------------------------
def change_profile(cur, db, user_id):
    """
    Display a submenu for profile management.
    This menu allows the user to edit or delete their profile data.
    """
    while True:
        print("""
        *****************************************
                    4 CHANGE PROFILE
        *****************************************
        1. Edit or Delete Profile Data
        2. Return to Main Menu
        *****************************************
        """)
        choice = input("Please select option 1 or 2: ").strip()
        if choice == "1":
            print("\nEditing profile information...")
            # Import User locally to avoid circular dependency
            from user import User
            user_instance = User(db, user_id=user_id)
            user_instance.change_profile()
            
        elif choice == "2":
            print("Returning to the main menu.")
            break
        
        else:
            print("Invalid input. Please select a valid option.")

# ----------------------------------------
# Main function
# ----------------------------------------
def main():
    """Main function to run the habit tracker program."""
    try:
        # Step 1: Display Welcome Screen
        welcome_menu()

        # Step 2: Database Setup
        db, cur = database_needed()  # Get connection and cursor from db.py
        if not db or not cur:
            print("Failed to connect to the database. Exiting program.")
            return

        # Step 3: User Authentication
        db, cur = database_needed()
        user_id = login_user_menu(cur, db)
        if not user_id:
            print("Failed to authenticate the user. Exiting program.")
            return

        #Step 4: Main User Menu
        while True:
            main_user_menu()
            input_main_menu = input("Please choose option 1, 2, 3, 4, or 5: ").strip()

            #4.1 VIEW HABITS & STREAKS
            if input_main_menu == "1":
                view_habits(cur, user_id)

            #4.2 CHANGE HABITS
            elif input_main_menu == "2":    
                change_habits(cur, db, user_id)

            #4.3 UPDATE HABITS & STREAKS
            elif input_main_menu == "3":
                update_habits(cur, db, user_id)

            #4.4 CHANGE PROFILE
            elif input_main_menu == "4":
                change_profile(cur, db, user_id)

            #4.5 EXIT
            elif input_main_menu == "5":
                print("Thanks for participating.\nYou will now be logged out.")
                break
            else:
                print("Invalid input. Please choose a valid option.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if cur:
            cur.close()
        close_db()

# Standard Python entry point
if __name__ == "__main__":
    main()
