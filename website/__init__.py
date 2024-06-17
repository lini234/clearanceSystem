from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from werkzeug.security import generate_password_hash
from flask_login import LoginManager
import sqlite3
db = SQLAlchemy()
DB_NAME = "database.db"
UPLOAD_FOLDER = 'website/static/uploads'

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'PWRBMB'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    db.init_app(app)

    from .auth import auth
    from .views import views


    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')


    from .models import User, Department
    with app.app_context():

        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app
