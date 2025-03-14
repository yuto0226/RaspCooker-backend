# -*- encoding: utf-8 -*-
from flask import Blueprint

blueprint = Blueprint(
    'auth',
    __name__,
)

# hardcoded account
users = {
    'admin': 'password'
}
