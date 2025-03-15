import os
from flask import request, jsonify
from app.file import blueprint, uploads_dir, allowed_file
from app.auth import token_required


@blueprint.route('/upload', methods=['POST'])
@token_required
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400

    file_path = os.path.join(uploads_dir, file.filename)

    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)

    file.save(file_path)
    return jsonify({'message': 'File uploaded successfully'})
