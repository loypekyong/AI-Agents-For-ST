import pytest
import tempfile
from flask import json
from werkzeug.datastructures import FileStorage
import os
import sys
from flask_bcrypt import Bcrypt

# Allow importing app file functions
utils_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(utils_dir)

from app import create_app, TestingConfig  # Import create_app function
from models import db, User # Import models

bcrypt = Bcrypt()

@pytest.fixture
def client():
    app = create_app(TestingConfig)  # Configure app for testing
    app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()  # Use a temporary directory for uploads
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Create the database tables
        yield client
        with app.app_context():
            db.drop_all()  # Cleanup after tests

@pytest.fixture
def auth_token(client):
    hashed_password = bcrypt.generate_password_hash('testpass').decode('utf-8')
    user = User(email='test@example.com', password=hashed_password)
    with client.application.app_context():
        db.session.add(user)
        db.session.commit()

    response = client.post('/auth/login', json={'email': 'test@example.com', 'password': 'testpass'})
    return response.json['token']

def test_upload_and_delete_file(client, auth_token):
    # Test uploading a PDF file
    data = {
        'sector': 'test_sector',
        'pdf': [FileStorage(stream=open('tests/test.pdf', 'rb'), filename='test.pdf')]
    }
    
    # request to upload file
    response = client.post('/upload/', headers={'Authorization': f'Bearer {auth_token}'}, data=data)
    
    assert response.status_code == 200
    # verify filenames added
    assert response.get_json() == {"filenames":[{'sector':'test_sector', 'file': 'test.pdf'}]}

    # request to delete file
    response = client.delete('/upload/test_sector/test.pdf', headers={'Authorization': f'Bearer {auth_token}'})
    
    assert response.status_code == 200
    assert response.get_data(as_text=True) == 'test.pdf removed'

def test_upload_invalid_file_type(client, auth_token):
    # Test uploading a non-PDF file
    data = {
        'sector': 'test_sector',
        'pdf': [FileStorage(stream=open('tests/test.txt', 'rb'), filename='test.txt')]
    }
    
    response = client.post('/upload/', headers={'Authorization': f'Bearer {auth_token}'}, data=data)
    
    assert response.status_code == 400
    assert response.get_data(as_text=True) == "Invalid file type"

def test_get_files_and_sectors(client, auth_token):
    # Uploading a PDF file to test getting files and sectors
    data = {
        'sector': 'test_sector',
        'pdf': [FileStorage(stream=open('tests/test.pdf', 'rb'), filename='test.pdf')]
    }
    
    # request to upload file
    response = client.post('/upload/', headers={'Authorization': f'Bearer {auth_token}'}, data=data)
    
    # Test getting the list of uploaded files
    response = client.get('/upload/', headers={'Authorization': f'Bearer {auth_token}'})
    
    # verify existing files and sectors
    assert response.status_code == 200
    assert response.get_json() == [{'sector':'test_sector', 'file':'test.pdf'}]

    # Test getting the list of sectors
    response = client.get('/upload/sectors', headers={'Authorization': f'Bearer {auth_token}'})
    
    # verify name of existing sector
    assert response.status_code == 200
    assert response.get_json() == ['test_sector']

    # request to delete file
    response = client.delete('/upload/test_sector/test.pdf', headers={'Authorization': f'Bearer {auth_token}'})
    
    assert response.status_code == 200
    assert response.get_data(as_text=True) == 'test.pdf removed'


def test_get_sectors_unauthorised(client):
    # Test getting the list of sectors
    response = client.get('/upload/sectors')
    
    assert response.status_code == 401

def test_delete_non_existent_file(client, auth_token):
    # Attempt to delete a file that does not exist
    response = client.delete('/upload/test_sector/non_existent.pdf', headers={'Authorization': f'Bearer {auth_token}'})
    
    assert response.status_code == 404
    assert 'not found' in response.get_data(as_text=True)