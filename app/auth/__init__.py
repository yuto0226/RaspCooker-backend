# -*- encoding: utf-8 -*-
import os
from datetime import datetime, timezone, timedelta
from flask import Blueprint, request, jsonify
import jwt

blueprint = Blueprint(
    'auth',
    __name__,
)

# hardcoded account
users = {
    'admin': {
        'password': 'password',
        'role': 'admin'
    }
}

secret_key = os.environ.get('SECRET_KEY', 'ttussc')


def token_required(f, role=""):
    def valid_auth(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(
                token.split(" ")[1],
                secret_key,
                algorithms=["HS256"]
            )
        except:
            return jsonify({'message': 'Invalid token!'}), 401

        if datetime.fromtimestamp(data.get('exp'), tz=timezone.utc) < datetime.now(timezone.utc):
            return jsonify({'message': 'Token expired!'}), 401

        if role != "" and data.get('role') != role:
            return jsonify({'message': 'Role not authorized!'}), 403

        return f(*args, **kwargs)
    return valid_auth
