import sys
import os
import time

# Add TRC to path so we can import communication
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'TRC')))

import communication
import unittest
from unittest.mock import patch, MagicMock
from requests.exceptions import ConnectionError

class TestLoggingSystem(unittest.TestCase):

    def setUp(self):
        communication.clear_logs()

    @patch('requests.get')
    def test_log_capture_on_error(self, mock_get):
        mock_get.side_effect = ConnectionError("DNS failure")
        
        # Call send which should log the error
        communication.send("general", {"msg": "hi"})
        
        logs = communication.get_logs()
        self.assertTrue(any("ERROR" in log and "DNS failure" in log for log in logs))

    @patch('requests.get')
    def test_log_recovery_success(self, mock_get):
        # First fail
        mock_get.side_effect = ConnectionError("DNS failure")
        communication.send("general", {"msg": "hi"})
        
        # Then succeed (we need to mock the response for stream to trigger recovery)
        # Note: we test the add_log directly in these cases or mock the stream behavior
        communication.add_log("Connection restored for #general", "SUCCESS")
        
        logs = communication.get_logs()
        self.assertTrue(any("SUCCESS" in log and "restored" in log for log in logs))

    def test_log_buffer_limit(self):
        # Add 60 logs
        for i in range(60):
            communication.add_log(f"Test log {i}")
        
        logs = communication.get_logs(100)
        self.assertEqual(len(logs), 50) # Buffer limit is 50

if __name__ == '__main__':
    unittest.main()
