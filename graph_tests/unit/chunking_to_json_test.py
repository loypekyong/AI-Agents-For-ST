import sys
import os
import unittest
from unittest.mock import patch, MagicMock, mock_open
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../flask')))
from chunking_to_json import create_kb, chunk_documents, get_folder_paths

from dotenv import load_dotenv
load_dotenv(dotenv_path="../../.env")

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API")

class TestChunkingToJson(unittest.TestCase):

    @patch('os.path.exists')
    @patch('os.getcwd', return_value='/mock/path/')
    def test_get_folder_paths_exists(self, mock_getcwd, mock_exists):
        # Arrange
        mock_exists.return_value = True
        base_folder = 'flask/uploads/'
        folder_name = 'sample'
        
        # Act
        result = get_folder_paths(base_folder, folder_name)
        
        # Assert
        expected = '/mock/path/flask/uploads/sample'
        self.assertEqual(result, expected)

    @patch('os.path.exists')
    @patch('os.getcwd', return_value='/mock/path')
    def test_get_folder_paths_not_exists(self, mock_getcwd, mock_exists):
        # Arrange
        mock_exists.return_value = False
        base_folder = 'flask/uploads'
        folder_name = 'sample'

        # Act & Assert
        with self.assertRaises(SystemExit):
            get_folder_paths(base_folder, folder_name)

    @patch('os.listdir', return_value=['doc1.pdf', 'doc2.pdf'])
    @patch('chunking_to_json.extract_text_from_pdf', return_value=["text from pdf"])
    @patch('chunking_to_json.KnowledgeBase')
    def test_create_kb(self, mock_kb, mock_extract_text, mock_listdir):
        # Arrange
        kb = mock_kb.return_value
        kb.add_document = MagicMock()
        folder_path = '/mock/path'

        # Act
        doc_ids = create_kb(kb, folder_path)

        # Assert
        self.assertEqual(doc_ids, ['doc1.pdf', 'doc2.pdf'])
        kb.add_document.assert_called_with(doc_id='doc2.pdf', text="text from pdf")  # Check last call

    # @patch('chunking_to_json.KnowledgeBase')
    # @patch('chunking_to_json.json.dump')
    # @patch('builtins.open', new_callable=mock_open)
    # @patch('os.listdir', return_value=['doc1.pdf', 'doc2.pdf'])  # Mocking os.listdir
    # @patch('os.path.exists', return_value=True)  # Ensure the directory exists
    # @patch('chunking_to_json.extract_text_from_pdf', return_value=["text from pdf"])  # Mock extraction
    # def test_chunk_documents(self, mock_extract_text, mock_open, mock_json_dump, mock_kb, mock_listdir, mock_exists):
    #     # Arrange
    #     kb = mock_kb.return_value
    #     kb.chunk_db.data = {
    #         'doc1.pdf': ['chunk1', 'chunk2'],
    #         'doc2.pdf': ['chunk3']
    #     }
        
    #     # Mock methods to return expected values
    #     kb.chunk_db.get_section_title = MagicMock(side_effect=lambda file, i: f'section {i}')
    #     kb.chunk_db.get_chunk_text = MagicMock(side_effect=lambda file, i: f'text {i}')
    #     kb.chunk_db.get_document_title = MagicMock(return_value='Document Title')
    #     kb.chunk_db.get_document_summary = MagicMock(return_value='Document Summary')

    #     # Act
    #     chunk_documents('test_kb', '/mock/path/', 'data_new/', '/mock/storage/')

    #     # Debug output to check if files are being opened
    #     print(mock_open.call_args_list)

    #     # Assert that the open call was made for both expected JSON files
    #     mock_open.assert_any_call(os.path.join('data_new', 'doc1.json'), 'w')
    #     mock_open.assert_any_call(os.path.join('data_new', 'doc2.json'), 'w')

    #     # Check if json.dump was called correctly
    #     self.assertTrue(mock_json_dump.called)

    #     # Ensure that json.dump was called with the correct data structure
    #     self.assertEqual(mock_json_dump.call_count, 2)  # Expecting two calls for two documents

if __name__ == "__main__":
    unittest.main()