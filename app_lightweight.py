"""
Lightweight Flask API - No Transformer Models
CPU-compatible resume parser without AVX issues
"""

import os
os.environ['OPENBLAS_CORETYPE'] = 'NEHALEM'
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_THREADING_LAYER'] = 'GNU'

from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import json
import traceback
from pathlib import Path
from datetime import datetime

from resume_parser_lightweight import LightweightResumeParser

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'docs'}
MAX_FILE_SIZE = 50 * 1024 * 1024

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

parser = None


def initialize_parser():
    """Initialize parser"""
    global parser
    if parser is None:
        print("Initializing Lightweight Resume Parser...")
        parser = LightweightResumeParser()


def allowed_file(filename):
    """Check if file is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def ensure_upload_folder():
    """Create upload folder"""
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'parser': 'lightweight',
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/parse', methods=['POST'])
def parse_resume():
    """Parse single resume"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'File type not allowed'}), 400
        
        ensure_upload_folder()
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        print(f"Parsing: {filename}")
        parsed_data = parser.parse_resume(file_path)
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
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/parse/batch', methods=['POST'])
def parse_batch():
    """Parse multiple resumes"""
    try:
        if 'files' not in request.files:
            return jsonify({'success': False, 'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        results = []
        errors = []
        
        for file in files:
            try:
                if file.filename == '' or not allowed_file(file.filename):
                    errors.append({'filename': file.filename, 'error': 'File type not allowed'})
                    continue
                
                ensure_upload_folder()
                filename = secure_filename(file.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)
                
                parsed_data = parser.parse_resume(file_path)
                results.append({
                    'filename': filename,
                    'status': 'success',
                    'candidate_name': parsed_data['contact_information'].get('name'),
                    'data': parsed_data
                })
                
                os.remove(file_path)
            except Exception as e:
                errors.append({'filename': file.filename, 'error': str(e)})
        
        return jsonify({
            'success': True,
            'processed': len(results),
            'errors': len(errors),
            'results': results,
            'errors_detail': errors,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/extract/<section>', methods=['POST'])
def extract_section(section):
    """Extract specific section"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'File type not allowed'}), 400
        
        ensure_upload_folder()
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        parsed_data = parser.parse_resume(file_path)
        
        valid_sections = [
            'contact_information', 'professional_summary', 'work_experience',
            'education', 'skills', 'certifications', 'projects'
        ]
        
        if section not in valid_sections:
            return jsonify({'success': False, 'error': 'Invalid section'}), 400
        
        section_data = parsed_data.get(section, {})
        os.remove(file_path)
        
        return jsonify({
            'success': True,
            'section': section,
            'data': section_data,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/info', methods=['GET'])
def info():
    """API info"""
    return jsonify({
        'name': 'Resume Parser API - Lightweight',
        'version': '1.0.0',
        'mode': 'CPU-compatible (no transformer models)',
        'parser': 'Regex + spaCy',
        'supported_formats': list(ALLOWED_EXTENSIONS),
        'max_file_size_mb': MAX_FILE_SIZE / (1024 * 1024)
    }), 200


@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({'message': 'Resume Parser API - Lightweight'}), 200


if __name__ == '__main__':
    initialize_parser()
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
