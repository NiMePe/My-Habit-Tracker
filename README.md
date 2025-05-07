# My Habit Tracker 
The My Habit Tracker app is a CLI‑based habit tracker backend built in Python 3.7+.  
It is a tool to help you achieve a personal goal by monitoring the implementation of a new habit.  
Your data will be stored in a local database file, which will then be used to analyze your tracking data.  
To use the program, a local database file must be created and certain external libraries must be installed  
(see prerequisites.txt).

## Table of Contents
1. [Features](#features)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Testing](#testing)
6. [Project Structure](#project-structure)
7. [Contributing](#contributing)
8. [License](#license)

## Features
**1. User Management**
- Creation of a user profile
- Login / Authentication  
- Profile editing and deletion 

**2. Habit Management**
- Use of predefined habits  
- Creation of custom habit  
- Habit deletion
- Change of habit interval  

**3. Habit Tracking**
- Checking a habit   
- Manual reset opportunity  
- Manual increment opportunity    

**4. Analysis Module**
- View of predefined and custom habits  
- Filter by interval (Daily / Weekly)  
- View of longest streaks ever  
- View of current streak or currently broken streaks 
- View of total number of repetitions per habit  

**5. Interactive CLI**
- Main Menu with options to  
    1. View Habits & Streaks  
    2. Change Habits  
    3. Update Tracking & Counters  
    4. Manage Profile  
    5. Exit  
- Contextual Submenus for each action, fully driven via input() prompts  

## Prerequisites
- **Python 3.7** or later  
- **pip** (included with Python)  
- *(Optional but recommended)* A virtual environment tool (`venv`)
- Or use of an **IDE** (e. g. Jupyter Lab, PyCharm, etc.) with virtual environment  

## Installation
How to install the project:

1. **Clone the repository**
    - Download from **GitHub**:
      Go to URL https://github.com/NiMePe/My-Habit-Tracker.git<br>
      Click " <> Code" button<br>
      Click "Download ZIP"

2. **Create and activate a virtual environment**
    - Windows open Terminal (type "cmd" into search bar):
        - python -m venv venv
        - venv\Scripts\activate.bat
    - Linux & macOS:
        - python3 -m venv venv
        - source .venv/bin/activate
    - Via IDE  

3. **Install dependencies (first use)**
    - pip install --upgrade pip 
    - pip install -r requirements.txt
     

## Usage
1. **Open a terminal in your project root (where main.py is)**
    - cd <repository_folder> (e. g. C:\Users\Your_Name\Desktop\My_Habit_Tracker\modules)  

2. **Start the program**
    - Open your virtual environment
    - Start with: python main.py  
    
3. **Follow the menus**
    - The program checks for an account and an existing database: main_db.db
    - If they do not exist, you will be asked if you want to create an account
    - The database will be initialized automatically
    - After login, use the main menu to analyze, change, and update habits or to change your profile.<br>
3.1 **How to create a new habit**<br>
&emsp;- Log in > Navigate to 2 CHANGE HABITS >  1. Create Custom Habit > Enter user input or cancel<br>
3.2 **How to complete a task within a given period**<br>
&emsp;- Log in > Navigate to 3 UPDATE HABITS & STREAKS > 1. Check a Habit > Enter the name of the habit > Confirm

## Test
**How to run tests for the project:**  
- Open your virtual environment  
- Change directory to test folder: cd <tests_folder> (e.g. C:\Users\Your_Name\Desktop\My_Habit_Tracker\tests)  
- For testing all test files enter: pytest tests -vv  
- For testing only one test file enter: pytest 'name_of_test_file'.py -vv 

## Project Structure
modules/  
├── main.py  # Entry point for the CLI  
├── db.py  # Database connection & schema  
├── habit.py  # Habit class  
├── user.py  # User class & auth  
├── counter.py  # Counter class  
├── analyze.py  # Analytics functions (pandas)  
├── habit_manager.py  # Helper functions for Habit  
├── counter_manager.py  # Helper functions for Counter  
├── user_manager.py  # Helper functions for User  
├── fixtures.py  # Script to load 4‑week sample data  
├── requirements.txt  # (pandas, pytest)  
├── README.md  # This file  
└── tests/  # pytest test suite  
&emsp;&emsp;├── __init__.py  
&emsp;&emsp;├── test_user.py  
&emsp;&emsp;├── test_analyze.py  
&emsp;&emsp;├── test_db.py  
&emsp;&emsp;├── test_main.py  
&emsp;&emsp;├── test_habit.py  
&emsp;&emsp;├── test_counter.py  
&emsp;&emsp;├── fixtures.py  
&emsp;&emsp;└── conftest.py

## Notes
- Database file: main_db.db is created in the working directory.
- Reset data: Delete your account in menu 4 and delete main_db.db
- Sample data: Test fixtures load 4‑week tracking data automatically via fixtures.py.   
