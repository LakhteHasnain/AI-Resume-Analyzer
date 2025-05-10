from flask import Flask
import os

app = Flask(__name__)

# Try to load config, but continue if not found
try:
    app.config.from_pyfile('config.py')
except FileNotFoundError:
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
    app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx', 'txt'}
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Import routes after app is created to avoid circular imports
from app.routes import api
app.register_blueprint(api.api_blueprint)

if __name__ == "__main__":
    app.run(debug=True)