from .prompt_template import PromptTemplate
from .java_8 import Java8Prompt
class PromptFactory:

    @staticmethod
    def get_prompt_template(language)->PromptTemplate:
        if language == "java8":
            return Java8Prompt()
        