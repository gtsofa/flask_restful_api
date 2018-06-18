# app/v2/todos/views.py
from flask import Flask, request, jsonify, make_response

from werkzeug.security import generate_password_hash, check_password_hash

import os
from pprint import pprint
from functools import wraps
import datetime
import uuid

from app.v2.models import Users
from app import create_app, db

from app.v2.models import Todo

import psycopg2
import jwt

from app import create_app

app = create_app('development')


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