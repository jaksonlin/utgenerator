from flask import Flask
from app.models.model_manager import model_manager

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

from app.routes.generate_unittest import generate_unittest_bp

app.register_blueprint(generate_unittest_bp)