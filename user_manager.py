"""
    This file contains helper functions for the user class to create, change and authenticate a user profile.
    The library sys is used for program termination. The library pwinput is used to cover a password while typing.
    All functions are called in the user class.
"""

import sys
import pwinput
import sqlite3


def create_name(cur, db):
    """Function to create a user name"""
    while True:
        try:
            print("\nLet's create a user name... ")
            user_name = input("\nPlease enter a user name you can easily memorize (type 'x' to cancel): ").strip()
            cur.execute("SELECT user_id FROM user WHERE user_name = ?", (user_name,))
            
            if user_name.lower() == 'x':
                print("Action was cancelled. Exiting program.")
                sys.exit()  # Terminate entire program
            
            # Check for duplicate
            if cur.fetchone():
                print("This user name is already taken. Please choose a different one.")
                continue
            
            # Confirm with user
            name_correct = input(f"Is '{user_name}' correct? Type 'Y' for yes, 'N' for no, or 'x' to cancel: ").strip().lower()
            if name_correct == "n":
                print("Let's try entering the name again.")
                continue
            elif name_correct != "y":
                print("Invalid input. Please type 'Y' for yes or 'N' for no.")
                continue
            elif name_correct == 'x':
                print("Action was cancelled. Exiting program.")
                sys.exit()  # Terminate entire program

            return user_name
        except sqlite3.Error as e:
            db.rollback()
            print(f"An error occurred while creating user name: {e}")

            
def create_id(cur, db):
    """Function to create a user ID"""
    while True:
        try:
            print("\nNow let's create your unique user ID... ")
            
            id_part1 = input("\nPlease type the first two letters of your first name (or 'x' to cancel): ").strip()[:2]
            if id_part1.lower() == 'x':
                print("Action was cancelled. Exiting program.")
                sys.exit()  # Terminate entire program
            id_part2 = input("Please type the first two letters of your last name (or 'x' to cancel): ").strip()[:2]
            if id_part2.lower() == 'x':
                print("Action was cancelled. Exiting program.")
                sys.exit()  # Terminate entire program
            id_part3 = input("Please type the month of your birth as number (e.g. 08) or 'x' to cancel: ").strip().zfill(2)
            if id_part3.lower() == 'x':
                print("Action was cancelled. Exiting program.")
                sys.exit()  # Terminate entire program
            id_part4 = input("Please type the day of your birth (e.g. 24) or 'x' to cancel: ").strip().zfill(2)
            if id_part4.lower() == 'x':
                print("Action was cancelled. Exiting program.")
                sys.exit()  # Terminate entire program

            user_id = f"{id_part1}{id_part2}{id_part3}{id_part4}"

            # Ensure ID is exactly 8 characters
            if len(user_id) != 8:
                print("An error occurred: Generated ID must be exactly 8 characters long.")
                print("Please make sure you entered two characters for each part of the ID.")
                continue

            # Confirm with the user
            id_correct = input(f"Is this your ID: '{user_id}'? Type 'Y' for yes and 'N' for no: ").lower()
            if id_correct == "n":
                print("Let's try entering the ID again.")
                continue
            elif id_correct != "y":
                print("Invalid input. Please type 'Y' for yes or 'N' for no.")
                continue

            return user_id
        except sqlite3.Error as e:
            db.rollback()
            print(f"An error occurred while creating user ID: {e}")

            
def create_pwd(cur, db):
    """Function to create a user password"""
    while True:
        try:
            print("\nAnd now let's set up your user password...")
            user_pwd = pwinput.pwinput("\nPlease enter a secure password with at least 6 characters using numbers,"
                               " letters, and special characters. Press enter to proceed or type 'x' to cancel: ")
            if user_pwd.lower() == 'x':
                print("Action was cancelled. Exiting program.")
                sys.exit()  # Terminate entire program            
           
            # Ensure password lenght >= 6
            if len(user_pwd) < 6:
                print("Your password is too short. Please try again.")
                continue
            
            # Confirm with user
            confirm_pwd = pwinput.pwinput("Please confirm your password: ")
            if confirm_pwd == user_pwd:
                return user_pwd
            else:
                print("Passwords do not match. Try again.")
        except sqlite3.Error as e:
            db.rollback()
            print(f"An error occurred while creating user password: {e}")


def create_profile(cur, db):
    """Function to create a new user with name, ID, and password"""
    try:
        user_name = create_name(cur, db)
        user_id = create_id(cur, db)
        user_pwd = create_pwd(cur, db)

        cur.execute("INSERT INTO user (user_id, user_name, user_pwd) VALUES (?, ?, ?)",
                    (user_id, user_name, user_pwd))
        db.commit()
        print("User created successfully!")
        return user_id, user_name, user_pwd
    except sqlite3.Error as e:
        db.rollback()
        print(f"Error creating user: {e}")

        
def change_profile(cur, db, user):
    """Function to allow a registered user to change their profile"""
    while True:
        try:
            print("\nWhat do you want to change?")
            print("1 = User Name")
            print("2 = Password")
            print("3 = User ID")
            print("4 = Delete Account")
            print("5 = Close Menu")

            #Prompt valid user input
            user_input = input("\nPlease enter a number (1, 2, 3, 4, or 5): ").strip()

            if user_input == "1":
                new_user_name = create_name(cur, db)
                cur.execute("UPDATE user SET user_name = ? WHERE user_id = ?", (new_user_name, user.user_id))
                db.commit()
                print(f"Your user name was successfully changed to '{new_user_name}'.")
            
            elif user_input == "2":
                new_user_pwd = create_pwd(cur, db)
                cur.execute("UPDATE user SET user_pwd = ? WHERE user_id = ?", (new_user_pwd, user.user_id))
                db.commit()
                print("Password changed successfully.")
            
            elif user_input == "3":
                old_user_id = user.user_id # Save old ID
                new_user_id = create_id(cur, db) # Create new ID
                
                # Update user table
                cur.execute("UPDATE user SET user_id = ? WHERE user_id = ?", (new_user_id, old_user_id))
                
                # Update counter table
                cur.execute("UPDATE counter SET user_id = ? WHERE user_id = ?",(new_user_id, old_user_id))
                
                # Commit and inform user
                db.commit()
                user.user_id = new_user_id
                print(f"Your user ID was successfully changed from '{old_user_id}' to '{new_user_id}'.")
                
            elif user_input == "4":
                print("\nDo you want to delete your user account?")
                confirm_delete = input("Please enter 'Y' for yes and 'N' for no: ").strip().lower()
                if confirm_delete == "y":
                    # Prompt the user for password and ID to confirm deletion
                    confirm_input1 = pwinput.pwinput("Please enter your password: ").strip()
                    confirm_input2 = input("To confirm deletion, enter your user ID: ").strip().lower()
                    # Fetch actual credentials from database
                    cur.execute(
                        "SELECT user_id, user_pwd FROM user WHERE user_id = ? OR user_name = ?",
                        (user.user_id, user.user_id)
                    )
                    result = cur.fetchone()
                    if not result:
                        print("User not found in database. Cannot delete.")
                        return
                    real_id, stored_pwd = result
                    real_id_lower = real_id.lower()
                                       
                    if confirm_input1 == stored_pwd and confirm_input2 == real_id_lower:
                        # Deletion of Counter data
                        cur.execute("DELETE FROM counter WHERE user_id = ?", (real_id,))
                        # Deletion of Habit data
                        cur.execute("DELETE FROM habits WHERE user_id = ?", (real_id,))
                        # Deletion of User data
                        cur.execute("DELETE FROM user WHERE user_id = ?", (real_id,))
                        db.commit()
                        print("All your account data (user, habits & counters) has been successfully deleted.")
                        sys.exit(0)  # Cancel program --> log-off
                    else:
                        print("Password or user ID were incorrect. Account deletion was canceled.")
                else:
                    print("Account deletion was canceled.")
            
            elif user_input == "5":
                print("Exiting profile management.")
                break
            
            else:
                print("Invalid input. Please enter a number between 1 and 5.")

        except sqlite3.Error as e:
            db.rollback()
            print(f"An error occurred when changing profile: {e}")
  
            
def user_auth(cur, db):
    """
    Function to authenticate a user in login process by verifying their username 
    or user ID and password. After 3 failed login attempts password reset possible.
    """
    
    attempts = 0 # Define attempts number for authetication process   
    while True:
        try:
            print("\n***User Authentication***")
            identifier = input("Please enter your username or user ID: ").strip()
            cur.execute(
                "SELECT user_pwd FROM user WHERE user_name = ? OR user_id = ?", 
                (identifier, identifier)
            )
            result = cur.fetchone()            
            if result:
                stored_pwd = result[0]
                input_pwd = pwinput.pwinput("Please enter your password: ")
                if input_pwd == stored_pwd:
                    print("Authentication successful!")
                    return identifier
                else:
                    attempts += 1
                    print("Incorrect password. Please try again.")
                    if attempts >= 3:
                        choice = input("Too many failed attempts. Do you want to reset your password? "
                                       " Type 'Y' for Yes and 'N' for No: ").strip().lower()
                        if choice == "y":
                            # Use create_pwd function to get a new password
                            new_pwd = create_pwd(cur, db)
                            cur.execute(
                                "UPDATE user SET user_pwd = ? WHERE user_name = ? OR user_id = ?",
                                (new_pwd, identifier, identifier)
                            )
                            db.commit()
                            print("Password has been reset. Please log in again.")
                            attempts = 0
                        else:
                            print("Exiting authentication.")
                            return None
                    continue                        
            else:
                print("No user found with the provided username or user ID.")
                print("Do you want to create a new profile?")
                create_choice = input("Please enter 'Y' for yes and 'N' for no: ").strip().lower()
                if create_choice == "y":
                    create_profile(cur, db)
                    print("A new profile was created successfully! Please log in again.")
                elif create_choice == "n":
                    print("Exiting program. Thanks and good bye!")
                    exit()
                else:
                    print("Invalid input. Please enter 'Y' or 'N'.")
        except sqlite3.Error as e:
            db.rollback()
            print(f"An error occurred during authentication: {e}")
