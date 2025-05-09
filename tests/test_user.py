"""
Test file for user.py module
"""

import sqlite3
import pytest
import pwinput
from db import create_tables
from user import User

class TestUser:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, tmp_path, monkeypatch):
        # Setup and teardown the test scenario
        # Create a temporary database
        db_file = tmp_path / "test_user.db"
        self.db = sqlite3.connect(str(db_file))
        self.cur = self.db.cursor()
        create_tables(self.cur, self.db)
        yield
        self.db.close()
    
    def test_create_profile(self, monkeypatch):
        # Test if profile creation (user ID, username and password) works
        # 1. Simulate input for create_name, create_id functions with monkeypatch
        inputs = iter([
            "testuser", "Y",             # create_name: Name and confirmation 
            "Jo", "Do", "08", "24", "Y"  # create_id: First two letters of surname and familiy name, month, year, and confirmation
        ])
        monkeypatch.setattr('builtins.input', lambda prompt: next(inputs))
        # 2. Simulate password input via pwinput in monkeypatch
        pw_inputs = iter(["pa$$word123", "pa$$word123"])
        monkeypatch.setattr(pwinput, 'pwinput', lambda prompt: next(pw_inputs))
        
        user_instance = User(self.db)
        user_instance.create_profile()
        # 3. Verify that the user attributes have been set
        assert user_instance.user_name == "testuser"
        assert user_instance.user_id is not None and len(user_instance.user_id) == 8
        assert user_instance.user_pwd == "pa$$word123"

    def test_change_profile(self, monkeypatch):
        # Test if the change of a profile by simulating the change of the username from "olduser" to "newuser" works
        # 1. Insert a test user into the database
        self.cur.execute("INSERT INTO user (user_id, user_name, user_pwd) VALUES (?, ?, ?)",
                         ("test0123", "olduser", "pa$$word123"))
        self.db.commit()
        # 2. Create a User instance for testing change_profile
        user_instance = User(self.db, user_name="olduser", user_id="test0123", user_pwd="pa$$word123")
        # 3. Simulate interactive inputs with monkeypatch:
        inputs = iter([
            "1",           # 3.1 Menu for change_profile: Choose option "1" to change the user name
            "newuser",     # 3.2 Enter a new name "newuser" 
            "Y",           # 3.3 confirm with "Y"
            "5"            # 3.4 Prompt option "5" to close the menu
        ])                                                     
        monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))
        
        # 4. Call method change_profile to update the username
        user_instance.change_profile()
        
        # 5. Verify that the user name has been updated in the database
        self.cur.execute("SELECT user_name FROM user WHERE user_id = ?", ("test0123",))
        result = self.cur.fetchone()
        # New username should be "newuser" now
        assert result is not None and result[0] == "newuser"

    def test_user_auth(self, monkeypatch):
        # Testing user authentication for login when username and password are valid
        # 1. Insert a test user for authentication
        self.cur.execute("INSERT INTO user (user_id, user_name, user_pwd) VALUES (?, ?, ?)",
                         ("test0123", "authuser", "pa$$word123"))
        self.db.commit()
        # 2.1 Simulate user input for the authentication process: username
        auth_inputs = iter(["authuser"])
        monkeypatch.setattr("builtins.input", lambda prompt: next(auth_inputs))
        # 2.2 Simulate user input for the authentication process: pwinput for password
        monkeypatch.setattr(pwinput, 'pwinput', lambda prompt: "pa$$word123")
        # 3. Create a User instance
        user_instance = User(self.db)
        auth_result = user_instance.user_auth()
        # 4. Check that the authentication was successful by returning the username
        assert auth_result == "test0123"
