from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from flask_cors import CORS
from .. import app  # Import the app for config

api_blueprint = Blueprint('api', __name__)

# Configure CORS for the blueprint
cors = CORS(api_blueprint, resources={r"/*": {"origins": "http://localhost:3000"}})

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@api_blueprint.route('/upload', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['resume']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)
        return jsonify({"message": "File uploaded successfully", "filename": filename}), 200
    
    return jsonify({"error": "File type not allowed"}), 400
