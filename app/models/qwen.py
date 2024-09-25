from transformers import AutoTokenizer, AutoModelForCausalLM, AutoConfig
from .generic_model import GenericModel
from ..prompts.prompt_manager import PromptManager
import torch
from typing import List
import logging

logger = logging.getLogger(__name__)

class QwenModel(GenericModel):
    def __init__(self, model_path: str, prompt_manager: PromptManager):
        super().__init__(model_path, prompt_manager)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.load_model()

    def load_model(self):
        try:
            logger.info(f"Loading Qwen model from {self.model_path}")
            config = AutoConfig.from_pretrained(self.model_path, trust_remote_code=True)
            
            # Enable YaRN for long context handling
            config.rope_scaling = {
                "type": "yarn",
                "factor": 4.0,
                "original_max_position_embeddings": 32768
            }
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, trust_remote_code=True)
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                config=config,
                trust_remote_code=True,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto",
            )

            # Set pad token if not set
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                self.model.config.pad_token_id = self.model.config.eos_token_id
            
            # Get the model's maximum sequence length
            self.max_model_length = self.model.config.max_position_embeddings
            logger.info(f"Max model length: {self.max_model_length}")
            logger.info(f"Model loaded successfully on {self.device}")
        except Exception as e:
            logger.error(f"Error loading Qwen model: {e}")
            raise

    def generate_test_case(self, code: str, testcase_type: str) -> List[str]:
        messages = self.prompt_manager.get_prompt_chat_message(code, testcase_type)
        text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        
        tokenized_input = self.tokenizer(text, return_tensors="pt")
        if tokenized_input.input_ids.size(1) > self.max_model_length:
            logger.warning(f"Input text exceeds the model's maximum sequence length of {self.max_model_length} tokens. It will be truncated.")
        
        model_inputs = tokenized_input.to(self.device)
        try:
            with torch.no_grad():
                generated_ids = self.model.generate(
                    model_inputs.input_ids,
                    max_new_tokens=2048,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    top_p=0.95,
                    eos_token_id=self.tokenizer.eos_token_id,
                    pad_token_id=self.tokenizer.pad_token_id,
                )
            
            generated_tests = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
            extracted_codes = [self.prompt_manager.extract_code(test) for test in generated_tests]
            return extracted_codes
        except Exception as e:
            logger.error(f"Error generating test case: {e}")
            return []