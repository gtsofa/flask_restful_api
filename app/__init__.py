# app/__init__.py
from flask import Flask
from config import app_config


from flask_sqlalchemy import SQLAlchemy

# initialize sql-alchemy
db = SQLAlchemy()

# initialize the app

def create_app(config_name):
    app = Flask(__name__)

    #config_name = os.getenv('APP_SETTINGS')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'thisissecret'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///todo_db'
    db.init_app(app)

    

    return app