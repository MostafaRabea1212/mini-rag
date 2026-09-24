from src.stores.llm.LLMInterface import LLMInterface
import logging
from src.stores.llm.LLMEnums import LocalLLMEnums ,DocumentTypeEnum
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM 
import torch

class LLMLocalProvider(LLMInterface):
    def __init__(self, api_key : str , 
                    default_input_max_characters : int = 1000,
                    default_generation_max_output_tokens : int = 1000,
                    default_generation_temperature : float = 0.1 ):
        
        self.api_key=api_key

        self.default_input_max_characters=default_input_max_characters
        self.default_generation_max_output_tokens=default_generation_max_output_tokens
        self.default_generation_temperature=default_generation_temperature

        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

        # Local models
        self.embedding_model = None 
        self.generation_model = None 
        self.generation_tokenizer = None

        self.client=None
        self.enums=LocalLLMEnums
        self.logger=logging.getLogger(__name__)

    def set_generation_model(self, model_id :str):
        self.generation_model_id=model_id

        try : 
            self.logger.info( f"Loading local generation model: {model_id}" ) 
            self.generation_tokenizer = AutoTokenizer.from_pretrained( model_id ) 
            self.generation_model = AutoModelForCausalLM.from_pretrained( model_id, torch_dtype="auto", device_map="auto" ) 
            self.logger.info( f"Local generation model loaded: {model_id}" )
        except Exception as e:
                self.logger.exception( f"Error while loading local generation model: {e}" ) 
                self.generation_model = None
                self.generation_tokenizer = None
              
    def set_embedding_model(self, model_id : str , embedding_size :int ):
        self.embedding_model_id = model_id
        self.embedding_size=embedding_size

        self.embedding_model_id = model_id 

        try: 
            self.logger.info( f"Loading local embedding model: {model_id}" )

            device = "cuda" if torch.cuda.is_available() else "cpu"

            self.embedding_model = SentenceTransformer( model_id ,device=device )

            # Get embedding size directly from the model. 
            self.embedding_size = ( self.embedding_model.get_sentence_embedding_dimension() ) 

            self.logger.info( f"Local embedding model loaded: {model_id}" ) 
            self.logger.info( f"Embedding size: {self.embedding_size}" ) 

        except Exception as e: 

            self.logger.exception( f"Error while loading local embedding model: {e}" ) 
            
            self.embedding_model = None 
            self.embedding_size = None
  
    def process_text(self, text):
        return text[ :self.default_input_max_characters].strip()
    
    def generate_text(self, prompt: str,
                       chat_history: list = [],
                       max_output_token: int = None,
                       temperature: float = None):

        if not self.generation_model or not self.generation_tokenizer:
            self.logger.error("Local generation model was not set")
            return None

        if not self.generation_model_id:
            self.logger.error("Generation model for Local provider was not set")
            return None

        max_output_token = max_output_token if max_output_token is not None else self.default_generation_max_output_tokens
        temperature = temperature if temperature is not None else self.default_generation_temperature

        chat_history.append(
            self.construct_prompt(prompt=prompt, role=LocalLLMEnums.USER.value)
        )

        try:
            input_text = self.generation_tokenizer.apply_chat_template(
                chat_history,
                tokenize=False,
                add_generation_prompt=True
            )
            inputs = self.generation_tokenizer(
                input_text, return_tensors="pt"
            ).to(self.generation_model.device)

            with torch.no_grad():
                outputs = self.generation_model.generate(
                    **inputs,
                    max_new_tokens=max_output_token,
                    temperature=temperature,
                    do_sample=temperature > 0,
                )

            # بنشيل التوكنز بتاعة البرومبت ونسيب بس الرد الجديد
            generated_tokens = outputs[0][inputs["input_ids"].shape[-1]:]
            response_text = self.generation_tokenizer.decode(
                generated_tokens, skip_special_tokens=True
            )

            if not response_text:
                self.logger.error("Error while generating text with Local model")
                return None

            return response_text.strip()

        except Exception as e:
            self.logger.exception(f"Error while generating text with Local model: {e}")
            return None



    def embed_text(self, text: str, document_type: str = None):

        if not self.embedding_model:
            self.logger.error("Local embedding model was not set")
            return None

        if not self.embedding_model_id:
            self.logger.error("Embedding model for Local provider was not set")
            return None

        try:
            embedding = self.embedding_model.encode(
                self.process_text(text),
                convert_to_numpy=True,
                batch_size=32
            )
            return embedding.tolist()
        except Exception as e:
            self.logger.exception(f"Error while embedding text with Local model: {e}")
            return None

    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "content": self.process_text(prompt)
        }



    # Before:
    # We called embed_text() once for every chunk.
    #
    # After: added new function solve problem
    # Send multiple texts in one Cohere API request.
    # This reduces the number of API calls and helps avoid
    # the Trial API rate limit.
    def embed_texts(self, texts: list[str], document_type: str = None):

        if not self.embedding_model:
            self.logger.error("Local embedding model was not set")
            return None

        if not self.embedding_model_id:
            self.logger.error("Embedding model for Local provider was not set")
            return None

        processed_texts = [self.process_text(text) for text in texts]

        try:
            embeddings = self.embedding_model.encode(
                processed_texts,
                convert_to_numpy=True,
                batch_size=32
            )
            return embeddings.tolist()

        except Exception as e:
            self.logger.exception(f"Error while embedding texts with Local model: {e}")
            return None
