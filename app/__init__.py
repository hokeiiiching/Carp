"""Flask application factory for CARP."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS

from config import config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'warning'


def create_app(config_name: str = 'default') -> Flask:
    """
    Create and configure the Flask application.
    
    Args:
        config_name: Configuration environment name ('development', 'production', 'default')
    
    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Enable CORS - allows all origins in production since frontend and API share domain
    # In development, allows localhost:5173 for Vite dev server
    CORS(app, supports_credentials=True)
    
    # Register blueprints
    from app.routes import main_bp
    from app.api import api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

