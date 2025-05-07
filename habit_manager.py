"""
    File that contains helper functions for the habit class to
    - insert predefined habits into database
    - create custom habits
    - delete habits
    - edit habits
    Functions will be called in the habit class.
"""

import sqlite3
from datetime import datetime
from analyze import show_custom_habits

### Functions to create habits
def create_predef_habits(cur, db):
    """Function to insert predefined habits into the database"""
    predef_habits = [
        ('PMR', 'Progressive Muscle Relaxation: Relaxing each muscle group.', 'Relaxing', '2025-04-01', 'Daily', 0),
        ('Meditation', 'Reduce stress by observing one\'s body, thoughts, and feelings without judging them.', 'Relaxing', '2025-04-01', 'Weekly', 0),
        ('Journaling', 'It is a method to channel negative thoughts by positively reviewing the day.', 'Cognitive', '2025-04-01', 'Daily', 0),
        ('Week Planning', 'Reduce stress by carefully planning appointments for the next week.', 'Cognitive', '2025-04-01', 'Weekly', 0),
        ('Yoga', 'Combining movement with mindfulness and breathing techniques.', 'Physical', '2025-04-01', 'Daily', 0),
        ('Jogging', 'Physical activity by running.', 'Physical', '2025-04-01', 'Weekly', 0)
    ]
    try:
        for habit in predef_habits:
            cur.execute(
                "INSERT INTO habits (habit_name, habit_def, habit_type, habit_date, habit_interval, is_custom) VALUES (?, ?, ?, ?, ?, ?)", habit
            )
        db.commit()
        print("Predefined habits have been successfully inserted.")
    except sqlite3.Error as e:
        db.rollback()
        print(f"An error occurred while inserting predefined habits: {e}")

    
def create_custom_habits(cur, db, user_id):
    """Function to allow a user to create custom habits"""
    print("\nIn this menu, you can create your own custom habits.")
    print("\nFor creating your custom habit you have answer the following questions: \n"
          "\n - What is the name of the habit you want to create?\n"
          "\n - What would be a short definition of your habit?\n"
          "\n - What could be the generic term of your habit (e.g., 'Relaxing', 'Cognitive', 'Physical', etc.)?\n"
          "\n - Do you want to practice your habit daily or weekly? \n"
         )
    create_input = input("Do you want to proceed? If not, process will be cancelled. Type 'Y' for Yes or 'N' for No: ").lower()    
    if create_input != "y":
        print("Action was cancelled. Returning to menu.")
        return 
    try:
        habit_name = input("\nWhat is the name of the habit you want to create?\n")
        # Normalize case
        raw = habit_name.strip()
        habit_name = raw.title()
        # Check for duplicates
        cur.execute("SELECT habit_name FROM habits WHERE user_id = ? AND LOWER(habit_name)=?", 
                    (user_id, habit_name.lower()))
        if cur.fetchone():
            print(f"A habit called '{habit_name}' already exists.")
            return
        habit_def = input("\nPlease write a short definition of your habit.\n")
        habit_type = input("\nWhat could be the generic term of your habit (e.g., 'Relaxing', 'Cognitive', 'Physical', etc.)?\n")
        habit_date = datetime.now().strftime('%Y-%m-%d')

        while True:
            habit_interval = input("\nDo you want to practice your habit daily or weekly? (Type 'd' for daily and 'w' for weekly):\n").lower()
            if habit_interval == 'd':
                habit_interval = 'Daily'
                break
            elif habit_interval == 'w':
                habit_interval = 'Weekly'
                break
            else:
                print("Invalid input. Please type 'd' for daily or 'w' for weekly.")

        # Insert custom habit into the database
        cur.execute("INSERT INTO habits (user_id, habit_name, habit_def, habit_type, habit_date, habit_interval, is_custom) VALUES (?, ?, ?, ?, ?, ?, 1)",
                    (user_id, habit_name, habit_def, habit_type, habit_date, habit_interval))
        db.commit()
        print(f"The habit '{habit_name}' has been successfully saved.")
        print("Custom habit was successfully created!")
    except sqlite3.Error as e:
        db.rollback()
        print(f"An error occurred while creating your custom habit: {e}")
            

        
### Functions to change habits        
def delete_custom_habit(cur, db, user_id, habit_name=None):
    """Function to delete a custom habit"""    
    print("\nHere you can delete a custom habit.")
    print("\nThese are your custom habits: ")
    # Show custom habits
    custom_df = show_custom_habits(cur, user_id)
    if custom_df.empty:
        print("No custom habits available to delete.")
        return
    delete_input = input("Do you want to delete one of your custom habits? Type 'Y' for yes and 'N' for no: ").strip()
    if delete_input != "y":
        print("Action was cancelled. Returning to menu.")
        return 

    # Make it possible to enter lower-case habit name
    names = list(custom_df["Name"].values)
    names_lower = [n.lower() for n in names]

    # Prompt for habit name (or cancel)
    while True:
        del_name_input = input("\nPlease enter the habit name you want to delete "
                   "or type 'x' to cancel: ").strip().lower()
        if del_name_input == "x":
            print("Action was cancelled. Returning to menu.")
            return
        if del_name_input in names_lower:
            habit_name = names[names_lower.index(del_name_input)]
            break
        print("Habit does not exist. Please try again.")
    
    # Prompt for deletion
    delete_confirm = input(f"Are you sure you want to delete the habit '{habit_name}' ('Y' = Yes, 'N' = No)?: ").strip().lower()
    if delete_confirm == "y":                           
        # Deletion
        try:
            cur.execute("DELETE FROM habits WHERE habit_name = ? AND user_id = ?", 
                        (habit_name, user_id))
            db.commit()
            print(f"The habit '{del_name_input}' was successfully deleted.")
        except sqlite3.Error as e:
            db.rollback()
            print(f"An error occurred while deleting your habit: {e}. Returning to menu.")
        return
    else:
        print("Action was cancelled. Returning to menu.")
        return                            

        
def edit_custom_habit(cur, db, user_id, habit_name=None):
    """Function to edit the periodicity of a habit"""    
    print("\nHere you can change the interval of a custom habit to Weekly or Daily.")
    print("\nThese are your custom habits: ")
    custom_df = show_custom_habits(cur, user_id)
    if custom_df.empty:
        print("No custom habits available to edit.")
        return

    # Make it possible to enter lower-case habit name
    names = list(custom_df["Name"].values)
    names_lower = [n.lower() for n in names]

    # Prompt for habit name (or cancel)
    while True:
        edit_habit_name = input("\nPlease enter the name of the habit you want to edit "
                                "or type 'x' to cancel: ").strip().lower()
        if edit_habit_name == "x":
            print("Action was cancelled. Returning to menu.")
            return
        if edit_habit_name in names_lower:
            habit_name = names[names_lower.index(edit_habit_name)]
            break
        print("Habit does not exist. Please try again.")

    # Prompt for change of periodicity
    while True:
        try:
            edit_input = input(f"Are you sure you want to edit the periodicity of the habit? '{habit_name}'"
                               "('Y' = Yes, 'N' = No)?: "
                              ).strip().lower()
            if edit_input == "x" or edit_input != "y":
                print("Action was cancelled. Returning to menu.")
                return                
            periodicity_input = input(
                f"\nDo you want to set the periodicity of '{habit_name}' to 'Weekly' or 'Daily'? "
                "\nPlease enter 'w' or 'd' to change the periodicity or type 'x' to cancel): "
            ).strip().lower()
            if periodicity_input == "d":
                new_interval = "Daily"
            elif periodicity_input == "w":
                new_interval = "Weekly"   
            elif periodicity_input == "x":
                print("Action was cancelled. Returning to menu.")
                return
            else:
                print("Invalid input. Please enter 'w', 'd' or 'x'.")
                continue

            # Update database    
            cur.execute(
                "UPDATE habits SET habit_interval = ? WHERE habit_name = ? AND user_id = ?",
                (new_interval, habit_name, user_id)
            )
            db.commit()
            print(f"The periodicity of '{habit_name}' was successfully updated to '{new_interval}'.")
            return
        except sqlite3.Error as e:
            db.rollback()
            print(f"An error occurred while editing your habit: {e}. Please try again.")
        else:
            print("No habits were edited.")    
    
