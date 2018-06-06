# api.py
from flask import Flask, request, jsonify

import uuid
from werkzeug.security import generate_password_hash, check_password_hash

from flask_sqlachemy import SQLAlchemy
import psycopg2

from pprint import pprint

app = Flask(__name__)

app.config['SECRET_KEY'] = 'thisissecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/todo_db'
#SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/test_db'



db = SQLAlchemy(app)

class User(db.Model):
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
def create_user(self):
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(public_id=str(uuid.uuid4), name=data['name'], password=hashed_password, admin=False)
    self.user.session.add(new_user)
    self.user.session.commit()
    
    return jsonify({"message": "New user has been created!"})

@app.route('/user', methods=['GET'])
def get_all_users():
    return ''

@app.route('/user/<int:id>', methods=['GET'])
def get_a_user(id):
    return ''

@app.route('/user/<int:id>', methods=['PUT'])
def edit_user(id):
    return ''

@app.route('/user/<int:id>', methods=['DELETE'])
def delete_user(id):
    return ''

if __name__ =='__main__':
    app.run(debug=True)
    database_connection = DatabaseConnection()