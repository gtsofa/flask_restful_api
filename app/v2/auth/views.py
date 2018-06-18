# app/auth/views.py
from flask import Flask, request, jsonify, make_response

from werkzeug.security import generate_password_hash, check_password_hash

import os
from pprint import pprint
from functools import wraps
import datetime
import uuid

from . import auth

from app.v2.models import Users

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


@auth.route('/user', methods=['POST'])
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

@auth.route('/user', methods=['GET'])
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

@auth.route('/user/<string:public_id>', methods=['GET'])
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

@auth.route('/user/<string:public_id>', methods=['PUT'])
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

@auth.route('/user/<string:public_id>', methods=['DELETE'])
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

@auth.route('/login')
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