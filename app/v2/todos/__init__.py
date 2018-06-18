# app/v1/todos/__init__.py
from flask import Blueprint

# blueprint object
todo = Blueprint('todos', __name__)

from . import views


    