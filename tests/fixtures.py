"""
The fixture file contains a helper function to automatically generate sample data for 
a period of four weeks. It loads the sample data in the database by making us of add_counter function.
"""

from datetime import datetime, timedelta
from db import get_db, add_counter

def load_sample_data(cur, db, user_id, habit_name, interval, start_date):
    """
    Load example tracking data for a habit over a 4‑week period.
    
    :param cur: sqlite3.Cursor 
        The database cursor object for executing SQL commands.
    :param db: sqlite3.Connection 
        The database connection object to commit changes in the database.
    :param user_id: str
        The ID of the test user; used as foreign key in the database.
    :param habit_name: str 
        The name of the predefined habit.
    :param interval: 'Daily' or 'Weekly'
        Periodicity of the predefined habit.
    :param start_date: datetime.date 
        Date from which to start the data sampling.
    """
    
    # 1. Set streak counter at 0
    streak = 0
    
    # 2. Collect a list of dates for the given period
    dates = []
    if interval == 'Daily':
        # 2.1 Create a list with 28 consecutive days
        for i in range(28):
            dates.append(start_date + timedelta(days=i))
    else:
        # 2.2 Create a list with 4 consecutive weeks
        for i in range(4):
            dates.append(start_date + timedelta(weeks=i))
    
    # 3. Insert one record per date
    for date in dates:
        # 3.1 Use right format for the date and a fixed time
        date_str = date.strftime('%Y-%m-%d')
        time_str = '18:00:00'
        
        # 3.2 For simplicity: Always 1 repetition each period
        rep = 1
        # --> Increase streak each time
        streak += 1
        
        # Use of add_counter function from db.py to insert data into the database
        add_counter(cur, db, user_id, habit_name, date_str, time_str, rep, streak)
