from src.stores.vectordb.VectorDBEnums import VectorDBEnum
from src.stores.vectordb.providers import QdrandDBProvider
from src.controllers.BaseController import BaseController
class VectorDBProviderFactory(QdrandDBProvider):

    def __init__(self, config):
        self.config=config
        self.base_controller = BaseController()
    def create(self,provider : str):

        if provider == VectorDBEnum.QDRANT.value:
            return QdrandDBProvider(
                    db_path=self.base_controller.get_data_base_path(self.config.VECTOR_DB_PATH) ,
                    distance_method=self.config.VECTOR_DB_DISTANCE_METHOD,
            )
        return None

