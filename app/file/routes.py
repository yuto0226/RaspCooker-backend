import os
from flask import request, jsonify
from app.file import blueprint, uploads_dir, allowed_file
from app.auth import token_required

@blueprint.route('/', methods=['GET'])
@token_required
def list_file():
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
    
    files = []
    for filename in os.listdir(uploads_dir):
        file_path = os.path.join(uploads_dir, filename)
        if os.path.isfile(file_path):
            files.append({
                'filename': filename,
                'size': os.path.getsize(file_path),
                'created_time': os.path.getctime(file_path)
            })
    
    return jsonify({
        'files': files,
        'total': len(files)
    })

@blueprint.route('/upload', methods=['POST'])
@token_required
def upload():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    if not allowed_file(file.filename):
        return jsonify({'message': 'File type not allowed'}), 400

    file_path = os.path.join(uploads_dir, file.filename)

    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)

    file.save(file_path)
    return jsonify({'message': 'File uploaded successfully'})
