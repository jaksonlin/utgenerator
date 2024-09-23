from typing import List
from .generic_model import GenericModel
from ..prompts import Java8Prompt, PromptManager
from .model_result import TestCase
from ..prompts.testcase_type import TestCaseType
import os

from dotenv import load_dotenv
load_dotenv()

class ModelManager:
    def __init__(self):
        model_path = os.getenv("model_weight")
        if model_path is None or len(model_path) == 0:
            raise ValueError("Model weight path is not set in the environment variables.")
        
        language = os.getenv("language")
        if language is None or len(language) == 0:
            raise ValueError("Language is not set in the environment variables.")
        
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
        return  self.model.generate_test_case(code, TestCaseType.basic)
    
model_manager = ModelManager()