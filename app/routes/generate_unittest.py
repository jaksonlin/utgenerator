from flask import Blueprint, request, jsonify
from app.models.model_manager import model_manager

generate_unittest_bp = Blueprint('generate_unittest', __name__)

@generate_unittest_bp.route('/generate_unittest', methods=['POST'])
def generate_unittest():
    code = request.json['code']
    all_tests = model_manager.generate_unittest(code)
    # Convert Pydantic models to dictionaries
    all_tests_dict = [test.model_dump_json() for test in all_tests]
    return jsonify({
        'unittest': all_tests_dict,
    })

@generate_unittest_bp.route('/generate_basic_test', methods=['POST'])
def generate_basic_test():
    code = request.json['code']
    testcase = model_manager.generate_basic_test(code)
    # Convert Pydantic model to dictionary
    all_tests_dict = [testcase.model_dump_json()]
    return jsonify({
        'unittest': all_tests_dict,
    })