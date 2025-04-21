import os
import uuid
import google.generativeai as genai
from dotenv import load_dotenv
from flask import Flask, request, render_template, send_from_directory, redirect, url_for, flash, jsonify
from docx_utils import extract_text_from_docx, text_to_docx_bytes, create_diff_docx
from gemini_utils import improve_text
from werkzeug.utils import secure_filename

# Load environment variables
load_dotenv()

# Configure app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['OUTPUT_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

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
        filename = f"{uuid.uuid4()}_-_{original_filename}"
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
        original_docx_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        original_text = extract_text_from_docx(original_docx_path)
        improved_text = improve_text(original_text)
        original_docx_bytes = text_to_docx_bytes(original_text)
        improved_docx_bytes = text_to_docx_bytes(improved_text)
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        revision_count = create_diff_docx(original_docx_bytes, improved_docx_bytes, output_path)
        
        return jsonify({
            'status': 'success',
            'message': 'Document processed successfully',
            'download_url': url_for('download_file', filename=filename),
            'revision_count': revision_count
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/download/<filename>')
def download_file(filename):
    new_filename = f"changes_in_{filename.split("_-_")[1]}"
    return send_from_directory(
        app.config['OUTPUT_FOLDER'], 
        filename, 
        as_attachment=True,
        download_name=new_filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
