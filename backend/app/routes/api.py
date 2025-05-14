from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import re
from flask_cors import CORS
import traceback
from .. import app  # Import the app for config
from ..services.parser import ResumeParser
from ..services.hf_deepseek_analyzer import analyzer  # Using the HF-enabled analyzer

api_blueprint = Blueprint('api', __name__)

# Configure CORS for the blueprint
cors = CORS(api_blueprint, resources={r"/*": {"origins": "http://localhost:3000"}})

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@api_blueprint.route('/analyze', methods=['POST'])
def upload_and_analyze_resume():
    try:
        if 'resume' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['resume']
        job_desc = request.form.get('job_desc', None)

        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        if file and allowed_file(file.filename):
            # Step 1: Save the file - make sure directory exists
            upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            
            filename = secure_filename(file.filename)
            save_path = os.path.join(upload_folder, filename)
            file.save(save_path)

            try:
                # Step 2: Extract text - create a copy of the file first
                # This ensures we have a file object with a proper stream
                file.seek(0)  # Reset file pointer to beginning
                
                # Extract text
                text = analyzer.extract_text(file)
                
                # Check if we have the ResumeParser - if not, use a simple fallback
                parsed_data = {}
                try:
                    parsed_data = ResumeParser.parse_resume(text)
                except (NameError, AttributeError):
                    # If ResumeParser isn't properly defined, use a simple dict
                    parsed_data = {"raw_text": text}

                # Step 3: AI Suggestions using Hugging Face API
                suggestions = None
                api_key = request.form.get('api_key', os.environ.get('HF_API_KEY', ''))
                
                if api_key:
                    # Update the API key if provided in the request
                    analyzer.set_api_key(api_key)
                
                try:
                    suggestions = analyzer.analyze_resume(text, job_desc)
                    parsed_data["suggestions"] = suggestions
                except Exception as e:
                    app.logger.error(f"Error during AI analysis: {str(e)}")
                    parsed_data["suggestions"] = f"Error during analysis: {str(e)}"

                # Include truncated text for debugging
                parsed_data["truncated_text"] = text[:500] + "..." if len(text) > 500 else text

                return jsonify({
                    "message": "File uploaded and analyzed successfully", 
                    "data": parsed_data
                }), 200

            except Exception as e:
                app.logger.error(f"Error processing file: {str(e)}")
                app.logger.error(traceback.format_exc())
                return jsonify({
                    "error": f"Error processing file: {str(e)}",
                    "traceback": traceback.format_exc()
                }), 500

        return jsonify({"error": "File type not allowed"}), 400
        
    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({
            "error": f"Unexpected error: {str(e)}",
            "traceback": traceback.format_exc()
        }), 500
@api_blueprint.route('/describe-and-rate', methods=['POST'])
def describe_and_rate_resume():
    try:
        if 'resume' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['resume']
        job_desc = request.form.get('job_desc', None)

        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        if file and allowed_file(file.filename):
            # Extract text
            file.seek(0)  # Reset file pointer to beginning
            text = analyzer.extract_text(file)
            
            # Set API key if provided
            api_key = request.form.get('api_key', os.environ.get('HF_API_KEY', ''))
            if api_key:
                analyzer.set_api_key(api_key)
            
            # Get description and rating
            try:
                description_and_rating = analyzer.describe_and_rate_resume(text, job_desc)
                
                return jsonify({
                    "message": "Resume described and rated successfully",
                    "description_and_rating": description_and_rating,
                    "truncated_text": text[:500] + "..." if len(text) > 500 else text
                }), 200
                
            except Exception as e:
                app.logger.error(f"Error during description and rating: {str(e)}")
                return jsonify({
                    "error": f"Error during description and rating: {str(e)}",
                    "traceback": traceback.format_exc()
                }), 500

        return jsonify({"error": "File type not allowed"}), 400
        
    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({
            "error": f"Unexpected error: {str(e)}",
            "traceback": traceback.format_exc()
        }), 500
@api_blueprint.route('/batch-analyze', methods=['POST'])
def batch_analyze_resumes():
    try:
        if 'resumes[]' not in request.files:
            return jsonify({"error": "No files uploaded"}), 400

        files = request.files.getlist('resumes[]')
        job_desc = request.form.get('job_desc', '')
        api_key = request.form.get('api_key', os.environ.get('HF_API_KEY', ''))

        if api_key:
            analyzer.set_api_key(api_key)

        results = []
        for file in files:
            if file.filename == '':
                continue

            if file and allowed_file(file.filename):
                try:
                    file.seek(0)
                    text = analyzer.extract_text(file)
                    analysis = analyzer.describe_and_rate_resume(text, job_desc)

                    results.append({
                        'filename': secure_filename(file.filename),
                        'name': analysis.get('name', 'Unknown'),
                        'skills': analysis.get('key_strengths', [])[:5],
                        'score': analysis.get('match_rating', 0),
                        'analysis': analysis.get('summary', ''),
                        'truncated_text': analysis.get('truncated_text', text[:300] + "..." if len(text) > 300 else text)
                    })

                except Exception as e:
                    results.append({
                        'filename': secure_filename(file.filename),
                        'error': str(e)
                    })

        results.sort(key=lambda x: x.get('score', 0), reverse=True)

        return jsonify({
            'job_description': job_desc[:100] + "..." if len(job_desc) > 100 else job_desc,
            'results': results
        }), 200

    except Exception as e:
        return jsonify({
            "error": f"Batch processing failed: {str(e)}",
            "traceback": traceback.format_exc()
        }), 500

# Add new endpoint to set/update API key
@api_blueprint.route('/set-api-key', methods=['POST'])
def set_api_key():
    data = request.json
    if not data or 'api_key' not in data:
        return jsonify({"error": "API key required"}), 400
        
    api_key = data['api_key']
    success = analyzer.set_api_key(api_key)
    
    if success:
        return jsonify({"message": "API key updated successfully"}), 200
    else:
        return jsonify({"error": "Failed to initialize client with provided API key"}), 400