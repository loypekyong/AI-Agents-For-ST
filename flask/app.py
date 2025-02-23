# app.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS 
from flask_jwt_extended import JWTManager
import os
from dotenv import load_dotenv
from models import db
from routes.auth import auth_bp
from routes.message import message_bp
from routes.chat import chat_bp
from routes.upload import upload_bp

# Load environment variables from .env file
load_dotenv()

# Initialize Flask application
app = Flask(__name__)

# Enable CORS for the React frontend
CORS(app, supports_credentials=True)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(chat_bp, url_prefix='/chat')
app.register_blueprint(message_bp, url_prefix='/message')
app.register_blueprint(upload_bp, url_prefix='/upload')

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=3001, debug=True)