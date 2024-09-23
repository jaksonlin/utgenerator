from typing import Dict, List
import re
from .testcase_type import TestCaseType
from .prompt_default import prompt_without_mock

class PromptManager:
    language: str
    prompt_settings: Dict[str, str] # key being testcase_type, values being the prompt template for this test case type

    def __init__(self, language: str):
        self.language = language
        self.init_prompt_settings()

    def init_prompt_settings(self):
        self.prompt_settings = prompt_without_mock
    
    def get_prompt_chat_message(self, code: str, testcase_type: str) -> List[Dict[str, str]]:
        return [
            {"role": "system", "content": f"You are a helpful assistant that generates unit tests for {self.language} code."},
            {"role": "user", "content": self.get_prompt(code, testcase_type)}
        ]
    
    def get_prompt(self, code: str, testcase_type: str) -> str:
        if testcase_type not in self.prompt_settings:
            return self.prompt_settings[TestCaseType.basic].format(code=code, language=self.language)
        return self.prompt_settings[testcase_type].format(code=code, language=self.language)
       
    def get_valid_testcase_type(self) -> List[str]:
        return [x for x in self.prompt_settings]
    
    def extract_code(self, text: str) -> str:
        # Pattern to match code blocks for the specified language
        pattern = rf'```{self.language}\s*([\s\S]*?)\s*```'
        matches = re.findall(pattern, text)
        if matches:
            return '\n'.join(matches)
        else:
            # If no code block is found, return the entire text
            # This is a fallback in case the model doesn't use code blocks
            return text