from .generic_model import GenericModel

class ModelManager:
    def __init__(self, model_path):
        self.model = GenericModel(model_path)

    def generate_unittest(self, code, language):
        all_tests = []
        for test_type, prompt in PromptTemplate.items():
            test_case = self.model.generate_test_case(code, prompt, language)
            all_tests.append({
                'type': test_type,
                'content': test_case
            })
        return all_tests

model_manager = ModelManager("E:\\01-ai")  # Adjust this to your local path