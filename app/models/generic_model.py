from typing import List
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import re
from ..prompts.prompt_manager import PromptManager

class GenericModel:

    prompt_manager: PromptManager

    def __init__(self, model_path: str, prompt_manager: PromptManager):
        self.model_path = model_path
        self.prompt_manager = prompt_manager
        self.load_model()

    def load_model(self):
        self.model = AutoModelForCausalLM.from_pretrained(self.model_path, device_map="auto",  trust_remote_code=True)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, trust_remote_code=True)
        # Set pad token
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.model.config.pad_token_id = self.model.config.eos_token_id
        
        # Get the model's maximum sequence length
        self.max_model_length = self.model.config.max_position_embeddings
        print(f"Max model length: {self.max_model_length}")

    def generate_test_case(self, code: str, testcase_type: str) -> List[str]:
        messages = self.prompt_manager.get_prompt_chat_message(code, testcase_type)
        text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        
        # Validate input size against model's max sequence length
        tokenized_input = self.tokenizer(text, return_tensors="pt")
        if tokenized_input.input_ids.size(1) > self.max_model_length:
            raise ValueError(f"Input text exceeds the model's maximum sequence length of {self.max_model_length} tokens.")
        
        model_inputs = tokenized_input.to("cpu")
        generated_ids = self.model.generate(
            model_inputs.input_ids,
            max_new_tokens=2048,
            num_return_sequences=1,  # Change this value to generate multiple sequences
            temperature=0.7,
            do_sample=True,
            top_p=0.95,
            eos_token_id=self.tokenizer.eos_token_id
        )
        
        generated_tests = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
        
        # Process all generated sequences
        extracted_codes = [self.prompt_manager.extract_code(test) for test in generated_tests]
        
        # Return the first extracted code or all extracted codes based on your requirement
        return extracted_codes