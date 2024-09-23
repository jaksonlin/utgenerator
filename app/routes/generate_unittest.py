from flask import Blueprint, request, jsonify
from app.models.model_manager import model_manager

generate_unittest_bp = Blueprint('generate_unittest', __name__)

@generate_unittest_bp.route('/generate_unittest', methods=['POST'])
def generate_unittest():
    code = request.json['code']
    all_tests = model_manager.generate_unittest(code)
    return jsonify({
        'unittest': all_tests,
    })

@generate_unittest_bp.route('/generate_basic_test', methods=['POST'])
def generate_basic_test():
    code = request.json['code']
    basic_test = model_manager.generate_basic_test(code)
    return jsonify({
        'unittest': basic_test,
    })