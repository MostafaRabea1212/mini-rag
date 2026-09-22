from src.controllers.BaseController import BaseController
from fastapi import Request
from src.models.db_schemes import Project ,DataChunk
from typing import Optional , List
from src.stores.llm.LLMEnums import DocumentTypeEnum
import json
class NlpController(BaseController):

    def __init__(self , vectordb_client ,
                 generation_client , 
                 embedding_client ):
        super().__init__()
        self.vectordb_client=vectordb_client
        self.generation_client=generation_client
        self.embedding_client=embedding_client

    def create_collection_name(self , project_id : str ):
        return f"collection_{project_id}".strip()

    def reset_vector_db_collection (self , project : Project):
        collection_name = self.create_collection_name (project_id =project.project_id)
        return self.vectordb_client.delete_collection(collection_name=collection_name)

    def get_vector_db_collection_info(self,project :Project ):
        collection_name = self.create_collection_name (project_id =project.project_id)
        collection_info= self.vectordb_client.get_collection_info(collection_name=collection_name)

        return json.loads(json.dumps( collection_info , default= lambda x : x.__dict__))

    def index_into_vector_db(self,project : Project, 
                            chunks : List[DataChunk],
                            chunks_ids : List[int],
                            do_reset : bool = False):
        
        collection_name = self.create_collection_name (project_id =project.project_id)

        texts =[c.chunk_text for c in chunks ]
        metadata=[c.chunk_metadata for c in chunks ]

        """
                vectors = [
                    self.embedding_client.embed_text(
                        text =text, 
                        document_type=DocumentTypeEnum.DCUMENT.value)
                    for text in texts
                ]
        """     
        # Before:
        # embed_text() was called once for every chunk.
        #
        # After:
        # Process chunks in batches to reduce Cohere API calls
        # and avoid the Trial API rate limit.
        BATCH_SIZE = 40

        vectors = []

        for i in range(0, len(texts), BATCH_SIZE):

            batch_texts = texts[i:i + BATCH_SIZE]

            batch_vectors = self.embedding_client.embed_texts(
                texts=batch_texts,
                document_type=DocumentTypeEnum.DCUMENT.value
            )

            if batch_vectors is None:
                self.logger.error(
                    f"Embedding failed for batch starting at index {i}"
                )
                return False

            if len(batch_texts) != len(batch_vectors):
                self.logger.error(
                    f"Texts count: {len(batch_texts)}, "
                    f"Vectors count: {len(batch_vectors)}"
                )
                return False

            vectors.extend(batch_vectors)

        is_created = self.vectordb_client.create_collection(
            collection_name=collection_name,
            embedding_size=self.embedding_client.embedding_size,
            do_reset=do_reset
        )

        if not is_created and not self.vectordb_client.is_collection_existed(
            collection_name
        ):
            self.logger.error(
                f"Failed to create collection: {collection_name}"
            )
            return False

        is_inserted=self.vectordb_client.insert_many(collection_name=collection_name, 
                                                    texts=texts ,vector = vectors , 
                                                    points_id=chunks_ids,
                                                    metadata =metadata)
        if not is_inserted :
            self.logger.error(
                    f"Failed to insert chunks into {collection_name}"
                )
            return False
        return True

    def search_vector_db_collection(self , project : Project ,
                                     text :str , limit :int = 10):
        #step 1 :get collection name
        collection_name = self.create_collection_name (project_id =project.project_id)

        #step 2  : get text embedding vector
        vector = self.embedding_client.embed_text(text=text ,document_type= DocumentTypeEnum.QUERY.value)

        #step 3 : do semantic search 
        if not vector or len(vector) == 0 :
            return False
        
        results =self.vectordb_client.search_by_vector(collection_name = collection_name,
                                                        vector =vector , limit =limit )

        if not results :
            return False
        return json.loads(
            json.dumps(results  , default=lambda x : x.__dict__)
            )


