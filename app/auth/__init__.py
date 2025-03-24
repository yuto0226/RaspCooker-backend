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


def token_required(f):
    def valid_jwt_token(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            if not token.startswith('Bearer '):
                return jsonify({'message': 'Invalid token format! Must start with "Bearer "'}), 401
        
            token = token.split('Bearer ')[1].strip()
        
            data = jwt.decode(
                token,
                secret_key,
                algorithms=["HS256"]
            )
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401
        except Exception:
            return jsonify({'message': 'Invalid token format!'}), 401

        return f(*args, **kwargs)
    return valid_jwt_token
