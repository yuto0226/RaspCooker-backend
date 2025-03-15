# -*- encoding: utf-8 -*-
import os
from flask import Blueprint

blueprint = Blueprint(
    'file',
    __name__,
)

uploads_dir = os.environ.get('UPLOADS_DIR', 'uploads')
os.makedirs(uploads_dir, exist_ok=True)


def allowed_file(filename):
    allowed_extensions = {'py'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
