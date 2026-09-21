from src.stores.vectordb.VectorDBInterface import VectorDBInterface
import logging
from typing import List
from src.stores.vectordb.VectorDBEnums import DistanceMethodEnums
from qdrant_client import  models , QdrantClient

class QdrandDBProvider(VectorDBInterface):
    def __init__(self ,db_path : str ,
                 distance_method : str 
                                        ):
        self.client=None
        self.db_path=db_path
        self.distance_method=None


        if distance_method == DistanceMethodEnums.COSINE.value:
            self.distance_method=models.Distance.COSINE

        elif distance_method == DistanceMethodEnums.DOT.value:
             self.distance_method=models.Distance.DOT
        self.logger=logging.getLogger(__name__)

    def connect(self):
        self.client = QdrantClient(path=self.db_path)

    def disconnect(self):
        self.client =None

    def is_collection_existed(self , collection_name  : str) -> bool:
        return self.client.collection_exists(collection_name=collection_name)

    def list_all_collections(self)-> List:
       return self.client.get_collections()

    def get_collection_info(self , collection_name : str) -> dict:
        return self.client.get_collection(collection_name=collection_name)

    def delete_collection(self , collection_name : str):
        if self.is_collection_existed(collection_name):
            self.client.delete_collection(collection_name=collection_name)
        else:
            self.logger.error(f"the colelction {collection_name} not found")

    def create_collection(self, collection_name, 
                          embedding_size, do_reset = False):
        if do_reset :
           _ = self.delete_collection(collection_name)

        if not self.is_collection_existed(collection_name):

            _ =self.client.create_collection(
            collection_name=collection_name,
                            vectors_config=models.VectorParams(size=embedding_size, distance=self.distance_method),)

            return True
        
        return False
    
    def  insert_one(self , collection_name  :str, 
                    text : str ,vector :list , 
                    metadata :dict =None ,points_id : str =None):
        
        if not self.is_collection_existed(collection_name):

            self.logger.error(f"the colelction {collection_name} not exist")
            return False
        try :
            _ = self.client.upload_points(
                collection_name=collection_name,
                points= [
                    models.PointStruct(
                        id =points_id,
                        vector = vector,
                        payload = {
                            "text" : text,
                            "metadata" : metadata
                                    }
                                        )
                        ]
                            )
        except Exception as e:
            self.logger.error(f"Error While inserting batch : {e}")
            return False
        return True 
    def insert_many(self , collection_name  :str, 
                        texts : list ,vector :list , 
                        metadata : list =None , points_id : list =None 
                        ,batch_size : int = 50):

        if metadata is None: 
            metadata=[None] * len(texts)

        if points_id is None :
            points_id=[None] * len(texts)

        for i in range(0 , len(vector),batch_size ):

            batch_texts = texts[i : i+batch_size]
            batch_vector =vector[i : i+batch_size]
            batch_metadata= metadata[i : i+batch_size]
            batch_points_ids = points_id[i:i + batch_size]

            batch_points=[

                models.PointStruct(
                    id =batch_points_ids[x],
                    vector = batch_vector[x],
                    payload = {
                        "text" : batch_texts[x],
                        "metadata" : batch_metadata[x]
                                }
                                    )

                for x in range(len(batch_texts))
            ]
            try :
                _ = self.client.upload_points(
                collection_name=collection_name,
                points=batch_points
                )
            except Exception as e:
                self.logger.error(f"Error While inserting batch : {e}")

                return False

        return True
    
    def search_by_vector(self , collection_name : str ,
                         vector : list , limit : int = 5 ):
        return self.client.search(
            collection_name=collection_name
            ,query_vector=vector,
            limit=limit
        )
    