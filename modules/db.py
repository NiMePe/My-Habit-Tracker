""" 
    In this file, a database will be created using the sqlite3 library. The database will consist of the following three tables:
    User - Habit - Counter. It is initialized in the main.py.
    The habit and the counter tables will make use of foreign keys to reference data of the other two respective tables. 
    The counter table uses a UNIQUE constraint. In combination with INSERT INTO... ON CONFLICT... DO UPDATE... in add_counter
    duplicates are avoided and automatic updates encouraged. Furthermore, there will be various functions that involve the database.
"""

import sqlite3
import logging
import os
from datetime import datetime

# Log configuration for error handling
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Central variable for database connection
db_connection = None  

# The database "main_db.db" will be created
def get_db(name="main_db.db"):
    """Function to create and return a database connection"""
    global db_connection
    if db_connection is None:
        try:
            if not os.path.exists(name):
                logging.info(f"Database '{name}' not found. Creating a new one.")
            # Set connection to database    
            db_connection = sqlite3.connect(name)
            # Activate use of foreign key constraints 
            db_connection.execute("PRAGMA foreign_keys = ON")
            logging.info(f"Database '{name}' connection was successful")
        except sqlite3.Error as e:
            logging.error(f"The database connection failed: {e}")
            return None
    return db_connection


def close_db():
    """Function to close the central database connection if it exists"""
    global db_connection
    if db_connection is not None:
        db_connection.close()
        db_connection = None
        logging.info("The database connection is now closed.")
        
        
def create_tables(cur, db):
    """
    Function to create all necessary tables in the database.
    Called in initialize_db.
    """
    try:
        # Create User Data Table
        cur.execute("""CREATE TABLE IF NOT EXISTS user (
                        user_id TEXT PRIMARY KEY,
                        user_name TEXT NOT NULL,
                        user_pwd TEXT NOT NULL)
                    """)

        # Create Habits Table
        cur.execute("""CREATE TABLE IF NOT EXISTS habits (
                        user_id TEXT,
                        habit_name TEXT NOT NULL,
                        habit_def TEXT,
                        habit_type TEXT,
                        habit_date TEXT,
                        habit_interval TEXT,
                        is_custom BOOLEAN DEFAULT 1,
                        max_streak   INTEGER DEFAULT 0,
                        PRIMARY KEY (user_id, habit_name),
                        FOREIGN KEY (user_id) REFERENCES user (user_id) ON DELETE CASCADE)
                    """)

        # Create Counter Table (UNIQUE-constraint used as target for ON CONFLICT queries)
        cur.execute("""CREATE TABLE IF NOT EXISTS counter (
                       user_id TEXT,
                       habit_name TEXT,
                       check_date TEXT,
                       check_time TEXT,
                       habit_rep INTEGER DEFAULT 0,
                       habit_streak INTEGER DEFAULT 0,
                       PRIMARY KEY (user_id, habit_name, check_date, check_time),
                       UNIQUE (user_id, habit_name, check_date),
                       FOREIGN KEY (user_id) REFERENCES user (user_id) ON DELETE CASCADE,
                       FOREIGN KEY (user_id, habit_name) REFERENCES habits (user_id, habit_name) ON DELETE CASCADE)
                   """)
        db.commit()
        logging.info("The tables were successfully created.")
    except sqlite3.Error as e:
        db.rollback()
        logging.error(f"An error occurred while creating tables: {e}")
        

def initialize_db(cur, db):
    """
    Function that initializes the database by creating tables and 
    inserting predefined habits
    """
    try:      
        # Create tables
        create_tables(cur, db)

        # Insert predefined habits
        from habit_manager import create_predef_habits
        create_predef_habits(cur, db)

        db.commit()
        logging.info("Database has been successfully created and initialized.")
    except sqlite3.Error as e:
        db.rollback()
        logging.error(f"Failed to initialize the database: {e}")     
        
        
def add_counter(cur, db, user_id, habit_name, check_date, check_time, habit_rep, habit_streak):
    """
    Function to increment the counter data. Used in counter_manager.py.

    :param cur: Cursor for database operations
    :param db: Database connection object
    :param user_id: ID of the user
    :param habit_name: Name of the habit
    :param check_date: Date of the check (format: YYYY-MM-DD)
    :param check_time: Time of the check (format: HH:MM:SS)
    :param habit_rep: Number of repetitions
    :param habit_streak: Current streak value
    """
    try:
        # Insert counter data into counter table using INSERT INTO... ON CONFLICT... DO UPDATE... clause
        cur.execute("""INSERT INTO counter 
            (user_id, habit_name, check_date, check_time, habit_rep, habit_streak) 
            VALUES (?, ?, ?, ?, ?, ?) ON CONFLICT(user_id, habit_name, check_date) DO UPDATE
            SET habit_rep = habit_rep + excluded.habit_rep,
            habit_streak = excluded.habit_streak
            """, (user_id, habit_name, check_date, check_time, habit_rep, habit_streak))
        db.commit()
        logging.info("Counter data was successfully inserted.")
    
    except sqlite3.Error as e:
        db.rollback()
        logging.error(f"An error occurred while inserting counter data: {e}")
