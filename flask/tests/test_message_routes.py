import pytest
from flask import json
import os
import sys
from flask_bcrypt import Bcrypt

# Allow importing app file functions
utils_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(utils_dir)

from app import create_app, TestingConfig  # Import create_app function
from models import db, User, Chat, Message  # Import models

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

def test_get_chats(client, auth_token):
    with client.application.app_context():
        user = User.query.filter_by(email='test@example.com').first()
        chat = Chat(title='Test Chat', user_id=user.id)
        db.session.add(chat)
        db.session.commit()

    response = client.get('/message/', headers={'Authorization': f'Bearer {auth_token}'})
    assert response.status_code == 200
    assert 'messagesDict' in response.get_json()
    assert 'chatPreviews' in response.get_json()

def test_load_older(client, auth_token):
    with client.application.app_context():
        user = User.query.filter_by(email='test@example.com').first()
        chat = Chat(title='Test Chat', user_id=user.id)
        db.session.add(chat)
        db.session.commit()
        
        for i in range(15):
            message = Message(content=f'Message {i}', chat_id=chat.id)
            db.session.add(message)
        db.session.commit()

        # Get chat object for query to client
        chat = db.session.query(Chat).get(chat.id)

    response = client.post(
        f'/message/older/{chat.id}',
        json={'before_timestamp': '2025-12-01'},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 200 

    # check that values of last 10 messages are correct, (i values are aligned to match content ids with addition)
    for i, msg in enumerate(response.get_json()):
        assert msg['id'] == i + 6
        assert msg['ai'] == False
        assert msg['content'] == f'Message {i+5}'
        assert msg['chat_id'] == chat.id

def test_send_response(client, auth_token):
    with client.application.app_context():
        user = User.query.filter_by(email='test@example.com').first()
        chat = Chat(title='Test Chat', user_id=user.id)
        db.session.add(chat)
        db.session.commit()

        message = Message(content='Original message', chat_id=chat.id)
        db.session.add(message)
        db.session.commit()

        # Get chat object for query to client
        message = db.session.query(Message).get(message.id)

    response = client.post(f'/message/response/{message.id}', json={
        'input': 'Response input',
        'reranker': 0,
        'graph': 1
    }, headers={'Authorization': f'Bearer {auth_token}'})
    
    assert response.status_code == 200
    assert response.content_type == 'text/event-stream'

def test_create_message(client, auth_token):
    with client.application.app_context():
        user = User.query.filter_by(email='test@example.com').first()
        chat = Chat(title='Test Chat', user_id=user.id)
        db.session.add(chat)
        db.session.commit()

        # Get chat object for query to client
        chat = db.session.query(Chat).get(chat.id)

    response = client.post(f'/message/{chat.id}', json={'content': 'New message', 'ai': False}, headers={'Authorization': f'Bearer {auth_token}'})
    assert response.status_code == 201
    assert 'id' in response.get_json()

def test_create_message_unauthorised(client, auth_token):
    with client.application.app_context():
        user = User.query.filter_by(email='test@example.com').first()
        chat = Chat(title='Test Chat', user_id=user.id)
        db.session.add(chat)
        db.session.commit()

        # Get chat object for query to client
        chat = db.session.query(Chat).get(chat.id)

    response = client.post(f'/message/{chat.id}', json={'content': 'New message', 'ai': False})
    assert response.status_code == 401

def test_delete_message(client, auth_token):
    with client.application.app_context():
        user = User.query.filter_by(email='test@example.com').first()
        chat = Chat(title='Test Chat', user_id=user.id)
        db.session.add(chat)
        db.session.commit()

        message = Message(content='Message to delete', chat_id=chat.id)
        db.session.add(message)
        db.session.commit()

        # Get message object for query to client
        message = db.session.query(Message).get(message.id)

    response = client.delete(f'/message/{message.id}', headers={'Authorization': f'Bearer {auth_token}'})
    assert response.status_code == 200
    assert response.get_json()['msg'] == "Message deleted successfully!"