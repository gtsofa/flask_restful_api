# app/v2/auth/__init__.py
from flask import Blueprint

# blueprint object
auth = Blueprint('auth', __name__)

from . import views