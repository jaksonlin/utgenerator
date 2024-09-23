from typing import Dict, List
import re

class PromptTemplate:
    language: str

    def __init__(self, language: str):
        self.language = language

    def get_prompt(self, code: str, testcase_type: str) -> str:
        raise NotImplementedError
    
    def get_prompt_chat_message(self, code: str, testcase_type: str) -> List[Dict[str, str]]:
        return [
            {"role": "system", "content": f"You are a helpful assistant that generates unit tests for {self.language} code."},
            {"role": "user", "content": self.get_prompt(code, testcase_type)}
        ]
    
    def get_valid_testcase_type(self) -> List[str]:
        raise NotImplementedError
    
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