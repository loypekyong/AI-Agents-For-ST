import sys
import os
import unittest
from unittest.mock import patch, mock_open
import shutil

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../flask')))
from create_graph import Neo4jConnection

class TestNeo4jConnection(unittest.TestCase):

    @patch('os.walk')
    @patch('builtins.open', new_callable=mock_open, read_data='{"kb_id": [{"kb_id": "kb id", "doc_id": "doc.pdf", "section_title": "section title", "chunk_text": "chunk", "document_title": "doc title", "document_summary": "doc summary"}]}')
    def test_load_json_files_from_directory(self, mock_file, mock_walk):
        mock_walk.return_value = [("data_new", [], ["file1.json"])]
        connection = Neo4jConnection("bolt://localhost:7687", "user", "password")
        result = connection.load_json_files_from_directory("data_new")
        expected = {'doc.pdf': [{"kb_id": "kb id", "doc_id": "doc.pdf", "section_title": "section title", "chunk_text": "chunk", "document_title": "doc title", "document_summary": "doc summary"}]}
        self.assertEqual(dict(result), expected)

    @patch('os.walk')
    def test_load_json_files_no_files(self, mock_walk):
        mock_walk.return_value = [("data_new", [], [])]
        connection = Neo4jConnection("bolt://localhost:7687", "user", "password")
        result = connection.load_json_files_from_directory("data_new")
        self.assertEqual(result, {})

    @patch('shutil.move')
    @patch('os.listdir', return_value=["file1.json"])
    @patch('os.path.join', side_effect=lambda *args: ''.join(args))
    def test_move_completed_files(self, mock_join, mock_listdir, mock_move):
        connection = Neo4jConnection("bolt://localhost:7687", "user", "password")
        directory_path = 'data_new/'
        completed_directory = 'data_completed/'
        for filename in os.listdir(directory_path):
            if filename.endswith('.json'):
                src_path = os.path.join(directory_path, filename)
                dst_path = os.path.join(completed_directory, filename)
                shutil.move(src_path, dst_path)
        mock_move.assert_called_once_with('data_new/file1.json', 'data_completed/file1.json')

if __name__ == "__main__":
    unittest.main()