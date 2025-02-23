# routes/message_routes.py
from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt, exceptions
from models import db, Chat, Message
import time
import datetime
from reynard_react import response

message_bp = Blueprint('message', __name__)

@message_bp.route('/', methods=['GET'])
@jwt_required()
def get_chats():
    try:
        # get user id
        payload = get_jwt()
        user_id = payload['sub']

        # get all chats for logged in user
        chats = Chat.query.filter_by(user_id=user_id).all()
        messagesDict = {}
        chatPreviews = []
        for chat in chats:
            # Get the messages for each chat (retrieve only latest 10 messages, but reorder to ascending timestamps)
            messages = Message.query.filter_by(chat_id=chat.id).order_by(Message.timestamp.desc()).limit(10).all()
            messages.sort(key=lambda msg: msg.timestamp)
            
            # add messages for each chat id key to messagesDict
            currentMessages = [{'id': message.id, 'ai': message.ai, 'content': message.content, 'timestamp': message.timestamp, 'chat_id' : message.chat_id} for message in messages]
            messagesDict[chat.id] = currentMessages
            # add left panel preview values for each chat id to chatPreviews
            chatPreviews.append({'id':chat.id, 'lastMessage': messages[-1].content, 'title': chat.title, 'timeStamp': messages[-1].timestamp} if len(messages)!= 0 else {'id':chat.id, 'title': chat.title})
        
        return jsonify({"messagesDict": messagesDict, "chatPreviews": chatPreviews}), 200

    except exceptions.ExpiredSignatureError:
        return jsonify({"msg": "Token has expired."}), 401
    except exceptions.InvalidTokenError:
        return jsonify({"msg": "Invalid token."}), 401
    except Exception as e:
        return jsonify({"msg": "An error occurred: " + str(e)}), 500
    
@message_bp.route('/older/<int:chat_id>', methods=['POST'])
@jwt_required()
def load_older(chat_id):
    data = request.get_json()
    before_timestamp = data['before_timestamp']
    print(before_timestamp)
    
    older_messages = (
        db.session.query(Message)
        .filter(Message.chat_id == chat_id)
        .filter(Message.timestamp < before_timestamp)  # Filter messages older than the given timestamp
        .order_by(Message.timestamp.desc())  # Sort in descending order
        .limit(10)
        .all()
    )
    older_messages.sort(key=lambda msg: msg.timestamp)
    older_messages = [{'id': message.id, 'ai': message.ai, 'content': message.content, 'timestamp': message.timestamp, 'chat_id' : message.chat_id} for message in older_messages]
    return older_messages


@message_bp.route('/response', methods=['POST'])
@jwt_required()
def send_response():
    data = request.get_json()['input']

    # dummy response to test streaming
    # def generate():
    #     for i in range(len(data)):
    #         time.sleep(0.1)  # Simulate processing time
    #         yield data[i]  # Yield each character for streaming


    return Response(response(data), content_type='text/event-stream')

@message_bp.route('/<int:chat_id>', methods=['POST'])
@jwt_required()
def create_message(chat_id):
    data = request.get_json()
    new_message = Message(content=data['content'], chat_id=chat_id, ai=data['ai'])
    db.session.add(new_message)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        return jsonify({"msg": "Failed to create message: " + str(e)}), 500
    return jsonify({'id': new_message.id, 'ai': new_message.ai, 'content': new_message.content, 'timestamp': new_message.timestamp, 'chat_id':new_message.chat_id}), 201

@message_bp.route('/edit/<int:message_id>', methods=['POST'])
@jwt_required()
def modify_message(message_id):
    message = Message.query.get_or_404(message_id)
    content = request.get_json()['content']
    if content != None:
        message.content = content
        db.session.commit()
        return jsonify({'id': message.id, 'ai': message.ai, 'content': message.content, 'timestamp': message.timestamp, 'chat_id':message.chat_id}), 200
    else:
        return 400

@message_bp.route('/<int:message_id>', methods=['DELETE'])
@jwt_required()
def delete_message(message_id):
    message = Message.query.get_or_404(message_id)
    db.session.delete(message)
    db.session.commit()
    return jsonify({"msg": "Message deleted successfully!"}), 200