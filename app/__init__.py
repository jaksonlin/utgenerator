from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os
import pdb
load_dotenv()  # This loads the variables from .env



def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB
    app.config['CELERY_RESULT_BACKEND'] = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    app.config['CELERY_BROKER_URL'] = os.getenv('CELERY_BROKER_URL','redis://localhost:6379/0')
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', '/app/uploads')
    app.config['DOWNLOAD_FOLDER'] = os.getenv('DOWNLOAD_FOLDER', '/app/downloads')
    
    # Initialize model_manager with the MODEL_PATH from .env
    #model_manager.initialize(os.getenv('MODEL_PATH', '/app/models/qwen_model'))

    from .generate_unittest import generate_unittest_bp
    from .task_management import task_management_bp

    app.register_blueprint(generate_unittest_bp, url_prefix="/api")
    app.register_blueprint(task_management_bp, url_prefix="/api")
    @app.route('/health', methods=['GET'])
    def health_check():
        return 'OK', 200
    return app


app = create_app()
