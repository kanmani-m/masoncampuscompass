import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = 'your-secret-key-change-this'
    
    # Use SQLite for local development, PostgreSQL for Docker
    if os.getenv('DATABASE_URL'):
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    else:
        # Local development with SQLite
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///campus_compass.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Register blueprints
    from webapp.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    from webapp.main import main_bp
    app.register_blueprint(main_bp)
    init_db(app)
    
    return app

def init_db(app):
    # Create database tables
    with app.app_context():
            try:
                db.create_all()
            except Exception as e:
                print(f"Warning: Could not initialize database: {e}")
                print("Continuing without database. Some features may not work.")