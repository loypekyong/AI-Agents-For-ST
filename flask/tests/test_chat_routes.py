import pytest
from flask import json
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

def test_create_chat(client, auth_token):
    response = client.post(
        '/chat/',
        json={'title': 'Test Chat'},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 201
    assert response.get_json()['msg'] == "Chat created successfully!"
    assert 'id' in response.get_json()

def test_create_chat_unauthorized(client):
    response = client.post('/chat/', json={'title': 'Unauthorized Chat'})
    assert response.status_code == 401  # Unauthorized access

def test_delete_chat(client, auth_token):
    # First create a chat to delete
    create_response = client.post(
        '/chat/',
        json={'title': 'Chat to Delete'},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    chat_id = create_response.get_json()['id']

    # Delete the chat
    delete_response = client.delete(f'/chat/{chat_id}', headers={'Authorization': f'Bearer {auth_token}'})
    
    assert delete_response.status_code == 200
    assert delete_response.get_json()['msg'] == "Chat deleted successfully!"

def test_delete_chat_not_found(client, auth_token):
    response = client.delete('/chat/99999', headers={'Authorization': f'Bearer {auth_token}'})
    assert response.status_code == 404  # Not Found

def test_delete_chat_unauthorized(client):
    response = client.delete('/chat/1') 
    assert response.status_code == 401  # Unauthorized access