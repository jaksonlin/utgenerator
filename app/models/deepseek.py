from transformers import AutoTokenizer, AutoModelForCausalLM, AutoConfig, BitsAndBytesConfig
from .generic_model import GenericModel
from ..prompts.prompt_manager import PromptManager
import torch
from typing import List
import logging

logger = logging.getLogger(__name__)

class GPUNotAvailableError(Exception):
    pass

class DeepseekModel(GenericModel):
    def __init__(self, model_path: str, prompt_manager: PromptManager):
        if not torch.cuda.is_available():
            raise GPUNotAvailableError("This model requires a GPU to run.")
        super().__init__(model_path, prompt_manager)
        self.device = "cuda"

    def load_model(self):
        try:
            logger.info(f"Loading model from {self.model_path}")
            config = AutoConfig.from_pretrained(self.model_path, trust_remote_code=True)
            
            config.use_cache = True
            
            if hasattr(config, 'use_flash_attention_2'):
                config.use_flash_attention_2 = False

            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, trust_remote_code=True)
            
            vram_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
            use_8bit = vram_gb < 16

            quantization_config = BitsAndBytesConfig(load_in_8bit=True) if use_8bit else None

            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                config=config,
                trust_remote_code=True,
                torch_dtype=torch.float16,
                device_map="auto",
                quantization_config=quantization_config,
            )

            self.model.gradient_checkpointing_enable()

            # Set pad token
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                self.model.config.pad_token_id = self.model.config.eos_token_id
            
            # Get the model's maximum sequence length
            self.max_model_length = self.model.config.max_position_embeddings
            logger.info(f"Max model length: {self.max_model_length}")
            logger.info(f"Model loaded successfully on GPU with {vram_gb:.2f}GB VRAM")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise

    @torch.no_grad()
    def generate_test_case(self, code: str, testcase_type: str) -> List[str]:
        messages = self.prompt_manager.get_prompt_chat_message(code, testcase_type)
        text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        
        tokenized_input = self.tokenizer(text, return_tensors="pt")
        if tokenized_input.input_ids.size(1) > self.max_model_length:
            raise ValueError(f"Input text exceeds the model's maximum sequence length of {self.max_model_length} tokens.")
        
        model_inputs = tokenized_input.to(self.device)
        try:
            generated_ids = self.model.generate(
                model_inputs.input_ids,
                max_new_tokens=2048,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                top_p=0.95,
                eos_token_id=self.tokenizer.eos_token_id,
                use_cache=True,
            )
            
            generated_tests = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
            extracted_codes = [self.prompt_manager.extract_code(test) for test in generated_tests]
            return extracted_codes
        except Exception as e:
            logger.error(f"Error generating test case: {e}")
            return []