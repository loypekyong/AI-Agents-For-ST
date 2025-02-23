from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
from add_doc import Kb_add_doc, get_kb, get_file_as_id
import os
upload_bp = Blueprint('upload', __name__)

UPLOAD_FOLDER = './uploads'

# Function to check if file is of pdf format
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() =='pdf'

@upload_bp.route('/', methods=['GET'])
@jwt_required()
def get_files():
    # create upload folder if it doesn't exist
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    files_list = []
    for root, dirs, files in os.walk(UPLOAD_FOLDER):
        for file in files:
            files_list.append({'sector':root[10:], 'file':file})
    
    return jsonify(files_list), 200

@upload_bp.route('/sectors', methods=['GET'])
@jwt_required()
def get_sectors():
    # create upload folder if it doesn't exist
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    sectors = [sector for sector in os.listdir(UPLOAD_FOLDER) ]
    
    return jsonify(sectors), 200

@upload_bp.route('/scan', methods=['POST'])
@jwt_required()
def upload_file():
    
    sector = request.form.get('sector')
    # create or get knowledge base
    kb = get_kb(sector)
    print('created kb')

    # get path of specific kb file folder
    sector_path = os.path.join(UPLOAD_FOLDER, sector)
    
    # create new kb and file folder if not present
    if not os.path.exists(sector_path):
        os.makedirs(sector_path)
        
    if 'pdf' not in request.files:
        return jsonify({"error": "No file part"}), 400

    files = request.files.getlist('pdf')  # Get all files with the key 'pdf'
    uploaded_filenames = []

    # loop through and add all files in request to database backend
    for file in files:
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        if file and allowed_file(file.filename):
            try:
                # ensure filename is secure
                filename = secure_filename(file.filename)
                # save file to local storage
                file.save(os.path.join(sector_path, filename))
                # add file to knowledge base
                print('adding doc')
                Kb_add_doc(kb, os.path.join(sector_path, filename))
                uploaded_filenames.append({'sector':sector, 'file': filename})
            
            except:
                # remove file if kb failed to add
                os.remove(os.path.join(sector_path, filename))
                return f'{filename} could not be added', 500

    return jsonify({"filenames": uploaded_filenames}), 200

@upload_bp.route('/<sector>/<file>', methods=['DELETE'])
@jwt_required()
def delete_file(sector, file):
    if os.path.exists(os.path.join(UPLOAD_FOLDER, sector, file)):
        print(sector, file)
        kb = get_kb(sector)
        # remove .pdf from file name and pass file id to be deleted from kb
        kb.delete_document(file.split('.')[0])
        # remove pdf from local storage
        os.remove(os.path.join(UPLOAD_FOLDER, sector, file))
    else:
        return f'{file} not found', 404
    return f'{file} removed', 200