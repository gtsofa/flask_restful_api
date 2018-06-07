# api.py
import os
from flask import Flask, request, jsonify

import uuid
from werkzeug.security import generate_password_hash, check_password_hash

from instance.config import app_config

#from flask_sqlachemy import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
import psycopg2

from pprint import pprint

app = Flask(__name__)

config_name = os.getenv('APP_SETTINGS')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'thisissecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///todo_db'
#SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/test_db'



db = SQLAlchemy(app)

class Users(db.Model):
    """
    Will store users 
    """
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean)

class Todo(db.Model):
    """
    Will store todos
    """
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(50))
    complete = db.Column(db.Boolean)
    user_id = db.Column(db.Integer)


@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = Users(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, admin=False)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "New user has been created!"})

@app.route('/user', methods=['GET'])
def get_all_users():
    users = Users.query.all()

    output = [] # store results in this list from json
    for user in users:
        user_data = {} # dict to be populated with the iterations
        user_data['public_id'] = user.public_id
        user_data['name'] = user.name
        user_data['password'] = user.password
        user_data['admin'] = user.admin
        output.append(user_data)


    return jsonify({'users': output})

@app.route('/user/<string:public_id>', methods=['GET'])
def get_a_user(public_id):
    user = Users.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({'message' : 'No user found!'})
    user_data = {}
    user_data['public_id'] = user.public_id
    user_data['name'] = user.name
    user_data['password'] = user.password
    user_data['admin'] = user.admin

    return jsonify({'user': user_data})

@app.route('/user/<int:id>', methods=['PUT'])
def edit_user(id):
    return ''

@app.route('/user/<int:id>', methods=['DELETE'])
def delete_user(id):
    return ''

if __name__ =='__main__':
    app.run(debug=True)
    