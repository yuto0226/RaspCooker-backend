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

@blueprint.route('/<file_name>', methods=['DELETE'])
@token_required
def remove_file(file_name):
    file_path = os.path.join(uploads_dir, file_name)
    
    if not os.path.exists(file_path):
        return jsonify({'message': 'File not found'}), 404
    
    if not os.path.isfile(file_path):
        return jsonify({'message': 'The specified path is not a file'}), 400
    
    try:
        os.remove(file_path)
        return jsonify({'message': 'File deleted successfully'})
    except Exception as e:
        return jsonify({'message': f'Error deleting file: {str(e)}'}), 500
