"""
Flask REST API for Resume Parser
Provides HTTP endpoints for resume parsing
"""

from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import json
import traceback
from pathlib import Path
from datetime import datetime

from resume_parser import ResumeParser

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'docs'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Initialize parser
parser = None


def initialize_parser():
    """Initialize the resume parser"""
    global parser
    if parser is None:
        print("Initializing Resume Parser...")
        parser = ResumeParser()


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def ensure_upload_folder():
    """Ensure upload folder exists"""
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/parse', methods=['POST'])
def parse_resume():
    """Parse uploaded resume file"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': f'File type not allowed. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Save uploaded file
        ensure_upload_folder()
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Parse resume
        print(f"Parsing file: {filename}")
        parsed_data = parser.parse_resume(file_path)
        
        # Clean up uploaded file
        os.remove(file_path)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'data': parsed_data,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/parse/batch', methods=['POST'])
def parse_batch():
    """Parse multiple resume files"""
    try:
        if 'files' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No files provided'
            }), 400
        
        files = request.files.getlist('files')
        results = []
        errors = []
        
        for file in files:
            try:
                if file.filename == '' or not allowed_file(file.filename):
                    errors.append({
                        'filename': file.filename,
                        'error': 'File type not allowed'
                    })
                    continue
                
                # Save and parse
                ensure_upload_folder()
                filename = secure_filename(file.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)
                
                parsed_data = parser.parse_resume(file_path)
                
                results.append({
                    'filename': filename,
                    'status': 'success',
                    'candidate_name': parsed_data['contact_information'].get('name'),
                    'email': parsed_data['contact_information'].get('email'),
                    'skills_count': len(parsed_data['skills']),
                    'data': parsed_data
                })
                
                # Clean up
                os.remove(file_path)
                
            except Exception as e:
                errors.append({
                    'filename': file.filename,
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'total_files': len(files),
            'processed': len(results),
            'errors': len(errors),
            'results': results,
            'errors_detail': errors,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/extract/<section>', methods=['POST'])
def extract_section(section):
    """Extract specific section from resume"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'File type not allowed'
            }), 400
        
        # Save and parse
        ensure_upload_folder()
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        parsed_data = parser.parse_resume(file_path)
        
        # Extract requested section
        valid_sections = [
            'contact_information', 'professional_summary', 'work_experience',
            'education', 'skills', 'certifications', 'projects'
        ]
        
        if section not in valid_sections:
            return jsonify({
                'success': False,
                'error': f'Invalid section. Valid: {", ".join(valid_sections)}'
            }), 400
        
        section_data = parsed_data.get(section, {})
        
        # Clean up
        os.remove(file_path)
        
        return jsonify({
            'success': True,
            'section': section,
            'data': section_data,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/info', methods=['GET'])
def info():
    """Get API information"""
    return jsonify({
        'name': 'Resume Parser API',
        'version': '1.0.0',
        'description': 'REST API for parsing resumes and extracting structured information',
        'endpoints': {
            'POST /parse': 'Parse a single resume file',
            'POST /parse/batch': 'Parse multiple resume files',
            'POST /extract/<section>': 'Extract specific section from resume',
            'GET /health': 'Health check',
            'GET /info': 'API information'
        },
        'supported_formats': list(ALLOWED_EXTENSIONS),
        'max_file_size_mb': MAX_FILE_SIZE / (1024 * 1024)
    }), 200


@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        'message': 'Resume Parser API',
        'documentation': '/info'
    }), 200


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({
        'success': False,
        'error': f'File too large. Maximum size: {MAX_FILE_SIZE / (1024 * 1024):.1f} MB'
    }), 413


@app.errorhandler(404)
def not_found(error):
    """Handle 404 error"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 error"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


if __name__ == '__main__':
    # Initialize parser
    initialize_parser()
    
    # Run app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )
