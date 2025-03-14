from flask import Flask

import app.auth.routes as auth
import app.file.routes as file
import app.shell.routes as shell
import app.task.routes as task


def create_app():
    app = Flask(__name__)

    app.register_blueprint(auth.blueprint, url_prefix='/auth')
    app.register_blueprint(file.blueprint, url_prefix='/file')
    app.register_blueprint(shell.blueprint, url_prefix='/shell')
    app.register_blueprint(task.blueprint, url_prefix='/task')

    @app.route('/')
    def home():
        return "Hello, world"

    return app
