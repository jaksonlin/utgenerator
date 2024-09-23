from flask import Blueprint, request, jsonify
from app.models.model_manager import model_manager

generate_unittest_bp = Blueprint('generate_unittest', __name__)

@generate_unittest_bp.route('/generate_unittest', methods=['POST'])
def generate_unittest():
    java_code = request.json['java_code']
    all_tests = model_manager.generate_unittest(java_code)
    return jsonify({
        'unittest': all_tests,
        'test_types': list(model_manager.PROMPT_TEMPLATES.keys())
    })