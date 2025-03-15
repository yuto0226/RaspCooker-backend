from datetime import datetime, timezone, timedelta
from flask import request, jsonify, current_app
import jwt
from app.auth import blueprint, users, secret_key


@blueprint.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No auth data provided'})
    username = data.get('username')
    password = data.get('password')

    if username in users and users[username].get('password') == password:
        payload = {
            # Registered Claim
            'iat': datetime.now(timezone.utc),
            'exp': datetime.now(timezone.utc) + timedelta(hours=24),

            # Private Claim
            'username': username,
            'role': users[username].get('role')
        }

        token = jwt.encode(
            payload,
            secret_key,
            algorithm='HS256'
        )

        return jsonify({'token': token})
    return jsonify({'message': 'Invalid credentials'}), 401
