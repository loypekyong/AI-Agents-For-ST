# routes/chat_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from models import db, Chat

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/', methods=['POST'])
@jwt_required()
def create_chat():
    payload = get_jwt()
    user_id = payload['sub']

    data = request.get_json()
    new_chat = Chat(title=data['title'], user_id=user_id)
    db.session.add(new_chat)
    db.session.commit()
    return jsonify({"msg": "Chat created successfully!", "id": new_chat.id}), 201

@chat_bp.route('/<int:chat_id>', methods=['DELETE'])
@jwt_required()
def delete_chat(chat_id):
    chat = Chat.query.get_or_404(chat_id)
    # Delete associated messages first
    for message in chat.messages:
        db.session.delete(message)
    db.session.delete(chat)
    db.session.commit()
    return jsonify({"msg": "Chat deleted successfully!"}), 200