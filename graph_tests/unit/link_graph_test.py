import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add path of the component files to system
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../flask')))
from link_graph import Neo4jConnection

class TestNeo4jConnection(unittest.TestCase):
    @patch('link_graph.GraphDatabase.driver')  # Mock the Neo4j driver
    def setUp(self, mock_driver):
        # Setup the mock driver and session
        self.mock_session = MagicMock()
        mock_driver.return_value.session.return_value.__enter__.return_value = self.mock_session
        self.connection = Neo4jConnection("bolt://localhost:1234", "user", "password")

    def test_link_sections_success(self):
        # Arrange: Set up the mock to not raise any exceptions
        self.mock_session.run.return_value = None  # Simulate successful run
        
        # Act: Call the method
        try:
            self.connection.link_sections(self.mock_session)
            success = True
        except Exception:
            success = False

        # Assert: Check that no exceptions were raised
        self.assertTrue(success)
    
    def test_link_sections_failure(self):
        # Arrange: Set up the mock to raise an exception
        self.mock_session.run.side_effect = Exception("Linking failed")
        
        # Act: Call the method and capture the exception
        with self.assertRaises(Exception) as context:
            self.connection.link_sections(self.mock_session)

        # Assert: Check that the exception message is correct
        self.assertEqual(str(context.exception), "Linking failed")
    
    def test_close_connection(self):
        # Act: Call the close method
        self.connection.close()

        # Assert: Check that the driver's close method was called
        self.connection.driver.close.assert_called_once()

if __name__ == "__main__":
    unittest.main()