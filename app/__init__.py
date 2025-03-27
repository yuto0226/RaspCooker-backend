from flask import Flask, request, make_response
from flask_cors import CORS

import app.auth.routes as auth
import app.file.routes as file
import app.shell.routes as shell
import app.task.routes as task


def create_app():
    app = Flask(__name__)
    CORS(app, resources={
        r"/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"], "allow_headers": "*"}
    })

    app.register_blueprint(auth.blueprint, url_prefix='/auth')
    app.register_blueprint(file.blueprint, url_prefix='/file')
    app.register_blueprint(shell.blueprint, url_prefix='/shell')
    app.register_blueprint(task.blueprint, url_prefix='/task')

    @app.before_request
    def handle_options_request():
        if request.method == 'OPTIONS':
            response = make_response()
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
            return response

    @app.route('/')
    def home():
        return "Hello, world"

    return app
