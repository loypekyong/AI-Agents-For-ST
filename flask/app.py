# app.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS 
from flask_jwt_extended import JWTManager
import os
from dotenv import load_dotenv
from models import db

# Load environment variables from .env file
load_dotenv()

# Configuration classes
class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    

class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Use in-memory database for testing
    TESTING = True
    CORS_HEADERS = 'Content-Type' 

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # initialise upload folder variable
    app.config['UPLOAD_FOLDER'] = './uploads'

    # Enable CORS for the React frontend
    CORS(app, supports_credentials=True)

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt = JWTManager(app)

    # Import routes
    with app.app_context():
        from routes.auth import auth_bp
        from routes.message import message_bp
        from routes.chat import chat_bp
        from routes.upload import upload_bp
        
        # Register blueprints
        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(chat_bp, url_prefix='/chat')
        app.register_blueprint(message_bp, url_prefix='/message')
        app.register_blueprint(upload_bp, url_prefix='/upload')

    return app

if __name__ == '__main__':
    app = create_app()  # Default to the normal config
    app.run(host='0.0.0.0', port=3001, debug=True)