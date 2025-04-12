import os
from flask import Flask, request, render_template, send_from_directory, redirect, url_for, flash, jsonify
import google.generativeai as genai
from dotenv import load_dotenv
import uuid
from werkzeug.utils import secure_filename
from docx_utils import extract_text_from_docx, create_improved_docx
from gemini_utils import analyze_and_improve_text

# Load environment variables
load_dotenv()

# Configure app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['PROCESSED_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'processed')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

# Configure Gemini API
try:
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"Error configuring Gemini API: {e}")

# Allowed file extensions
ALLOWED_EXTENSIONS = {'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if a file was uploaded
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    
    # Check if file was selected
    if file.filename == '':
        flash('No file selected')
        return redirect(request.url)
    
    # Check if file is allowed
    if file and allowed_file(file.filename):
        # Generate a unique filename
        original_filename = secure_filename(file.filename)
        filename = f"{uuid.uuid4()}_{original_filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save the file
        file.save(filepath)
        
        # Redirect to processing page
        return redirect(url_for('process_file', filename=filename, original_filename=original_filename))
    
    flash('File type not allowed. Please upload a .docx file.')
    return redirect(url_for('index'))

@app.route('/process/<filename>')
def process_file(filename):
    original_filename = request.args.get('original_filename', filename)
    return render_template('processing.html', filename=filename, original_filename=original_filename)

@app.route('/api/process/<filename>', methods=['GET'])
def api_process_file(filename):
    """API endpoint to process the uploaded file and return status"""
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        original_text = extract_text_from_docx(filepath)
        improved_text = analyze_and_improve_text(original_text)  # Use Gemini
        
        # Create a new DOCX with track changes
        output_filename = f"improved_{filename}"
        output_path = os.path.join(app.config['PROCESSED_FOLDER'], output_filename)
        
        # Create the improved document and get the number of changes
        changes_count, original_paragraphs_count = create_improved_docx(improved_text, output_path)
        
        return jsonify({
            'status': 'success',
            'message': 'Document processed successfully',
            'download_url': url_for('download_file', filename=output_filename),
            'paragraphs_count': original_paragraphs_count,
            'improved_count': changes_count
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
