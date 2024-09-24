from flask import Flask
from flask_cors import CORS
from app.models.model_manager import model_manager
from dotenv import load_dotenv
import os
import pdb
load_dotenv()  # This loads the variables from .env

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', '/app/uploads')
    app.config['DOWNLOAD_FOLDER'] = os.getenv('DOWNLOAD_FOLDER', '/app/downloads')
    
    # Initialize model_manager with the MODEL_PATH from .env
    #model_manager.initialize(os.getenv('MODEL_PATH', '/app/models/qwen_model'))

    from app.routes.generate_unittest import generate_unittest_bp
    from app.routes.task_management import task_management_bp

    app.register_blueprint(generate_unittest_bp, url_prefix="/api")
    app.register_blueprint(task_management_bp, url_prefix="/api")
    return app