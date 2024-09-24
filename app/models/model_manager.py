from typing import List
from .generic_model import GenericModel
from .deepseek import DeepseekModel
from ..prompts import Java8Prompt, PromptManager
from .model_result import TestCase
from ..prompts.testcase_type import TestCaseType
import os
import pdb

from dotenv import load_dotenv
load_dotenv()

class ModelManager:
    def __init__(self):
        model_path = os.getenv("MODEL_PATH")
        if model_path is None or len(model_path) == 0:
            raise ValueError("MODEL_PATH is not set in the environment variables.")
        
        language = os.getenv("LANGUAGE")
        if language is None or len(language) == 0:
            raise ValueError("LANGUAGE is not set in the environment variables.")
        
        self.language = language
        self.prompt_manager = self._create_prompt_manager(language)
        self.model = GenericModel(model_path, self.prompt_manager)

    def _create_prompt_manager(self, language: str):
        if language.lower() == "java":
            return Java8Prompt(language=language)
        # Add more language-specific prompt managers as needed
        else:
            return PromptManager(language=language)

    def generate_unittest(self, code: str) -> List[TestCase]:
        all_tests = []
        for test_type in self.prompt_manager.get_valid_testcase_type():
            test_case = self.model.generate_test_case(code, test_type)
            all_tests.append(TestCase(type=test_type, content=test_case))
        return all_tests
    
    def generate_basic_test(self, code: str) -> TestCase:
        extracted_code = self.model.generate_test_case(code, TestCaseType.basic)
        return TestCase(type=TestCaseType.basic, content=extracted_code)
    
    _model_manager = None

    @staticmethod
    def get_model_manager() -> "ModelManager":
        if ModelManager._model_manager is None:
            ModelManager._model_manager = ModelManager()
        return ModelManager._model_manager

