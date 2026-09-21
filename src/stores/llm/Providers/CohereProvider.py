from src.stores.llm.LLMInterface import LLMInterface
import logging
from src.stores.llm.LLMEnums import CoHereEnums ,DocumentTypeEnum
import cohere

class CoHereProvider(LLMInterface):
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

        self.client=cohere.ClientV2(
            api_key=self.api_key,
        )
        self.logger=logging.getLogger(__name__)

    def set_generation_model(self, model_id :str):
        self.generation_model_id=model_id

    def set_embedding_model(self, model_id : str , embedding_size :int ):
        self.embedding_model_id = model_id
        self.embedding_size=embedding_size

    def process_text(self, text):
        return text[ :self.default_input_max_characters].strip()
    
    def generate_text(self ,prompt : str 
                           ,chat_history : list =[],
                            max_output_token : int = None ,
                            temperature  :float = None):

        
        if not self.client:
            self.logger.error("OpenAI client was not set")
            return None
        
        if not self.generation_model_id:
            self.logger.error("Generation model for OpenAI was not set")
            return None
        
        max_output_token = max_output_token if max_output_token is not None else self.default_generation_max_output_tokens

        temperature = temperature if temperature is not None else self.default_generation_temperature

        chat_history.append(
            self.construct_prompt(prompt=prompt ,
                                   role= CoHereEnums.USER.value)
                                   )

        response= self.client.chat(
            model=self.generation_model_id, 
            messages=chat_history,
            max_tokens=max_output_token,
            temperature=temperature
            )
        if not response or not response.message or not response.message.content:
            self.logger.error("Error while generating text with CoHere")
            return None

        return  response.message.content[0].text



    def embed_text(self, text  : str, document_type : str= None):

        if not self.client:
            self.logger.error("CoHere client was not set")
            return None
        
        if not self.embedding_model_id:
            self.logger.error("Embedding model for CoHere was not set")
            return None

        input_type=CoHereEnums.DCUMENT.value
        if document_type == DocumentTypeEnum.QUERY.value:
            input_type=CoHereEnums.QUERY.value

        response= self.client.embed(
            model=self.embedding_model_id, 
            texts = [self.process_text(text)],
            input_type =input_type,
            output_dimension=self.embedding_size,
            embedding_types=["float"],
            )
        
        if not response or not response.embeddings or not response.embeddings.float:
            self.logger.error("Error while embedding text with CoHere")
            return None
        
        return response.embeddings.float[0]

    def construct_prompt(self , prompt : str , role : str):
        return {
            "role" : role,
            "content" : self.process_text(prompt)
            }

    # Before:
    # We called embed_text() once for every chunk.
    #
    # After: added new function solve problem
    # Send multiple texts in one Cohere API request.
    # This reduces the number of API calls and helps avoid
    # the Trial API rate limit.
    def embed_texts(self, texts: list[str], document_type: str = None):

        if not self.client:
            self.logger.error("CoHere client was not set")
            return None

        if not self.embedding_model_id:
            self.logger.error("Embedding model for CoHere was not set")
            return None

        input_type = CoHereEnums.DCUMENT.value

        if document_type == DocumentTypeEnum.QUERY.value:
            input_type = CoHereEnums.QUERY.value

        processed_texts = [
            self.process_text(text)
            for text in texts
        ]

        try:
            response = self.client.embed(
                model=self.embedding_model_id,
                texts=processed_texts,
                input_type=input_type,
                output_dimension=self.embedding_size,
                embedding_types=["float"],
            )

            if (
                not response
                or not response.embeddings
                or not response.embeddings.float
            ):
                self.logger.error("Error while embedding texts with CoHere")
                return None

            return response.embeddings.float

        except Exception as e:
            self.logger.exception(
                f"Error while embedding texts with CoHere: {e}"
            )
            return None
