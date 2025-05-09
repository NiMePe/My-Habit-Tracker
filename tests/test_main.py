"""
Test file for the main.py module
"""

import io
from contextlib import redirect_stdout
import pytest
from main import main

class TestMain:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, monkeypatch):
        # Setup and teardown of the test scenario
        # Simulate user inputs for the run of main() with monkeypatch:               
        inputs = iter([
            "3", # In login_user_menu --> Type "3" to exit (returns an exit message)
            "5"  # In main menu loop --> Type "5" to exit the main loop
        ])
        monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))
        yield
            
    def test_main_exit(self):
        # Check the output of main() with redirect_stdout
        output = io.StringIO()
        with redirect_stdout(output):
            main()
        printed = output.getvalue()
        # Check for existence of an exit message
        assert "Thanks for participating" in printed.lower() or "exit" in printed.lower()
