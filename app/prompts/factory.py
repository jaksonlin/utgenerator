from .prompt_manager import PromptManager
from .java_8 import Java8Prompt

class PromptFactory:

    @staticmethod
    def get_prompt_template(language)->PromptManager:
        if language == "java8":
            return Java8Prompt()
        else:
            return PromptManager()
        