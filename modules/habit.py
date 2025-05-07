""" 
    This file contains the habit class.
    It is used to insert the predefined habits and custom habits into the database.
    Plus, it allows the user to delete and edit habits.
    For this purpose, the functions from "habit_manager.py" are called.
"""

from habit_manager import create_predef_habits, create_custom_habits, delete_custom_habit, edit_custom_habit
from datetime import datetime

class Habit:
    def __init__(self, db_connection, user_id, habit_name: str, habit_def: str, habit_type: str, 
                 habit_date: datetime, habit_interval: str):
    
        """ 
        A class that represents a habit that will be tracked.

        :param db_connection: sqlite3.Connection 
            The database connection object used to interact with the database.
        :param user_id: str
            A unique identification of the user.
        :param habit_name: str
            The name of the habit being tracked.
        :param habit_def: str
            A detailed description of the habit.
        :param habit_type: str
            The category of the habit (e.g., relaxing, cognitive, physical).
        :param habit_date: datetime
            The date when the habit was created.
        :param habit_interval: str
            The practice interval of the habit (daily or weekly).
        """   
        
        self.habit_name = habit_name
        self.habit_def = habit_def
        self.habit_type = habit_type
        self.habit_date = habit_date
        self.habit_interval = habit_interval
        self.user_id = user_id
        #Database connection
        self.db = db_connection
        self.cur = self.db.cursor()

    
    def create_predef_habits(self):
        """Method to insert predefined habits into database"""
        create_predef_habits(self.cur, self.db)

        
    def create_custom_habits(self):
        """Method for creating custom habits"""
        create_custom_habits(self.cur, self.db, self.user_id)

        
    def delete_habit(self, habit_name=None):
        """Method for deleting custom habits: Asks for confirmation, then delegates to the manager."""
        delete_custom_habit(self.cur, self.db, self.user_id, habit_name)

        
    def edit_habit(self, habit_name=None):
        """Method for editing custom habits: Asks for confirmation, then delegates to the manager."""
        edit_custom_habit(self.cur, self.db, self.user_id, habit_name)
