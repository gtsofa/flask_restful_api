# api.py
import os
from pprint import pprint
from functools import wraps
import datetime
import uuid
from flask import Flask, request, jsonify, make_response

from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import jwt

#from instance.config import app_config

#from flask_sqlachemy import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy

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

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message' : 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = Users.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message' : 'Token is invalid'}), 401
        return f(current_user, *args, **kwargs)
    return decorated


@app.route('/user', methods=['POST'])
@token_required
def create_user(create_user):
    if not create_user.admin:
        return jsonify({'message' : 'Cannot perform that function!'})
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = Users(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, admin=False)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "New user has been created!"})

@app.route('/user', methods=['GET'])
@token_required
def get_all_users(create_user):
    if not create_user.admin:
        return jsonify({'message' : 'Cannot perform that function!'})
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
@token_required
def get_a_user(create_user, public_id):
    if not create_user.admin:
        return jsonify({'message' : 'Cannot perform that function!'})
    user = Users.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({'message' : 'No user found!'})
    user_data = {}
    user_data['public_id'] = user.public_id
    user_data['name'] = user.name
    user_data['password'] = user.password
    user_data['admin'] = user.admin

    return jsonify({'user': user_data})

@app.route('/user/<string:public_id>', methods=['PUT'])
@token_required
def edit_user(create_user, public_id):
    if not create_user.admin:
        return jsonify({'message' : 'Cannot perform that function!'})
    user = Users.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({'message' : 'No user found!'})
    user.admin = True
    db.session.commit()
    return jsonify({'message': 'User has been promoted!'})

@app.route('/user/<string:public_id>', methods=['DELETE'])
@token_required
def delete_user(create_user, public_id):
    if not create_user.admin:
        return jsonify({'message' : 'Cannot perform that function!'})
    user = Users.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({'message' : 'No user found!'})
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'The user has been deleted!'})

@app.route('/login')
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'www-Authenticate': 'Basic realm="Login required!"'})

    user = Users.query.filter_by(name=auth.username).first()
    if not user:
        return make_response('Could not verify', 401, {'www-Authenticate': 'Basic realm="Login required!"'})
    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'public_id' : user.public_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
        return jsonify({'token' : token.decode('UTF-8')})
    return make_response('Could not verify', 401, {'www-Authenticate': 'Basic realm="Login required!"'})


# create a todo
@app.route('/todo', methods=['POST'])
@token_required
def create_todo(create_user):
    data = request.get_json()

    new_todo = Todo(text=data['text'], complete=False, user_id=create_user.id)
    db.session.add(new_todo)
    db.session.commit()

    return jsonify({'message' : 'A new todo has been created!'})
#list all todos
@app.route('/todo', methods=['GET'])
@token_required
def list_all_todo(create_user):
    todos = Todo.query.filter_by(user_id=create_user.id).all()

    output = []
    for todo in todos:
        todo_data = {}
        todo_data['id'] = todo.id
        todo_data['text'] = todo.text
        todo_data['complete'] = todo.complete
        todo_data['user_id'] = todo.user_id
        output.append(todo_data)

    return jsonify({'todos' : output})


# list a single todo
@app.route('/todo/<todo_id>', methods=['GET'])
@token_required
def list_single_todo(create_user, todo_id):
    todo = Todo.query.filter_by(id=todo_id, user_id=create_user.id).first()
    if not todo:
        return jsonify({'message' : 'No todo found!'})

    todo_data = {}    
    todo_data['id'] = todo.id
    todo_data['text'] = todo.text
    todo_data['complete'] = todo.complete
    todo_data['user_id'] = todo.user_id

    return jsonify(todo_data)

# edit a todo
@app.route('/todo/<todo_id>', methods=['PUT'])
@token_required
def edit_a_todo(create_user, todo_id):
    todo = Todo.query.filter_by(id=todo_id, user_id=create_user.id).first()
    if not todo:
        return jsonify({'message' : 'No todo found!'})
    todo.complete = True
    db.session.commit()
    return jsonify({'message' : 'Todo item has been completed!'})

# delete a todo
@app.route('/todo/<todo_id>', methods=['DELETE'])
@token_required
def delete_a_todo(create_user, todo_id):
    todo = Todo.query.filter_by(id=todo_id, user_id=create_user.id).first()
    if not todo:
        return jsonify({'message' : 'No todo found!'})
    db.session.delete(todo)
    db.session.commit()
    return jsonify({'message' : 'Todo item has been deleted!'})
    



if __name__=='__main__':
    app.run(debug=True)
    