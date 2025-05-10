# backend/app/config.py
import os

# Base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Upload settings
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)