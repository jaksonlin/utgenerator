from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import re

class GenericModel:
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto")
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        
        # Set pad token
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.model.config.pad_token_id = self.model.config.eos_token_id
        
        # Get the model's maximum sequence length
        self.max_model_length = self.model.config.max_position_embeddings
        print(f"Max model length: {self.max_model_length}")

    def extract_code(self, text, language):
        # Pattern to match code blocks for the specified language
        pattern = rf'```{language}\s*([\s\S]*?)\s*```'
        matches = re.findall(pattern, text)
        if matches:
            return '\n'.join(matches)
        else:
            # If no code block is found, return the entire text
            # This is a fallback in case the model doesn't use code blocks
            return text

    def generate_test_case(self, code, prompt_template, language):
        prompt = prompt_template.format(code=code)
        messages = [
            {"role": "system", "content": f"You are a helpful assistant that generates unit tests for {language} code."},
            {"role": "user", "content": prompt}
        ]
        text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        
        model_inputs = self.tokenizer([text], return_tensors="pt").to("cpu")
        generated_ids = self.model.generate(
            model_inputs.input_ids,
            max_new_tokens=2048,
            num_return_sequences=1,
            temperature=0.7,
            do_sample=True,
            top_p=0.95,
            eos_token_id=self.tokenizer.eos_token_id
        )
        
        generated_test = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        extracted_code = self.extract_code(generated_test, language)
        return extracted_code