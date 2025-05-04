import os
import uuid
import shutil
import logging
import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import FastAPI, Request, File, UploadFile, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from docx_utils import extract_text_from_docx, text_to_docx_bytes, create_diff_docx
from gemini_utils import improve_text
from werkzeug.utils import secure_filename
import uvicorn # For running the app

logging.basicConfig(level=logging.INFO, format='%(levelname)s (%(name)s): %(message)s')
logger = logging.getLogger(__name__)

# Prepare environment
load_dotenv()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'output')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Configure app
app = FastAPI()
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@app.route('/')
@app.get("/", response_class=HTMLResponse)
async def index(request: Request, msg: str = None):
    """Serves the main upload page."""
    return templates.TemplateResponse("index.html", {"request": request, "message": msg})

@app.route('/upload', methods=['POST'])
@app.post("/upload", response_class=RedirectResponse)
async def upload_file(request: Request, file: UploadFile = File(...)):
    """Handles file uploads."""
    # Check if a file was uploaded
    if not file:
        return RedirectResponse(url=request.url_for('index') + "?msg=No+file+part", status_code=303)

    # Check if file was selected
    if file.filename == '':
        return RedirectResponse(url=request.url_for('index') + "?msg=No+file+selected", status_code=303)

    # Check if file type is allowed
    allowed_extensions = {'docx'}
    if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
        # Generate a unique filename
        original_filename = secure_filename(file.filename)
        filename = f"{uuid.uuid4()}_-_{original_filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        # Save the file
        try:
            with open(filepath, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        finally:
            await file.close() # Ensure the file pointer is closed

        # Redirect to processing page
        process_url = str(request.url_for('process_file', filename=filename)) + f"?original_filename={original_filename}"
        logger.info(f"File uploaded and saved as {filename} in {UPLOAD_FOLDER}. Redirecting to {process_url}")
        return RedirectResponse(url=process_url, status_code=303)

    return RedirectResponse(url=request.url_for('index') + "?msg=File+type+not+allowed.+Please+upload+a+.docx+file.", status_code=303)

@app.route('/process/<filename>')
@app.get("/process/{filename}", response_class=HTMLResponse)
async def process_file(request: Request, filename: str, original_filename: str):
    """Shows the processing page while the document is being revised."""
    logger.info(f"Processing file {filename} with original filename {original_filename}")
    return templates.TemplateResponse("processing.html", {"request": request, "filename": filename, "original_filename": original_filename})

@app.get("/api/process/{filename}", response_class=JSONResponse)
async def api_process_file(request: Request, filename: str):
    """API endpoint to process the uploaded file and return status"""
    try:
        original_docx_path = os.path.join(UPLOAD_FOLDER, filename)
        original_text = extract_text_from_docx(original_docx_path)
        improved_text = improve_text(original_text)
        # Note: text_to_docx_bytes creates a *new* docx from plain text, losing original formatting.
        # create_diff_docx expects the *original file path* or bytes. Let's pass the path.
        improved_docx_bytes = text_to_docx_bytes(improved_text)
        output_path = os.path.join(OUTPUT_FOLDER, filename)
        revision_count = create_diff_docx(original_docx_path, improved_docx_bytes, output_path) # Pass original path
 
        return {
            'status': 'success',
            'message': 'Document processed successfully',
            'download_url': request.url_for('download_file', filename=filename),
            'revision_count': revision_count
        }
    except Exception as e:
        logger.error(f"Error processing file {filename}: {e}") # Log the error server-side
        # Raise HTTPException for FastAPI error handling
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@app.get("/download/{filename}", response_class=FileResponse)
async def download_file(filename: str): # Make async and add type hint
    """Provides the processed document for download."""
    output_filepath = os.path.join(OUTPUT_FOLDER, filename)
    if not os.path.exists(output_filepath):
        raise HTTPException(status_code=404, detail="File not found")

    # Extract original filename part for download name
    try:
        new_filename = f"changes_in_{filename.split('_-_')[1]}"
    except IndexError:
        new_filename = f"changes_in_{filename}" # Fallback if format is unexpected
        
    return FileResponse(path=output_filepath, filename=new_filename, media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')

if __name__ == '__main__':
    # Set reload=True for development, disable in production
    uvicorn.run(
        "app:app", 
        host='0.0.0.0', # make it accessible on the network
        port=5000, 
        reload=True,
    )
