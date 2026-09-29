from fastapi import FastAPI

from src.routes import base , data ,nlp
from motor.motor_asyncio import AsyncIOMotorClient
from src.helper.config import get_settings
from src.stores.llm.LLMProviderFactory import LLMProviderFactory
from src.stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory
from src.stores.llm.templates.template_parser import TemplateParser

app = FastAPI()

@app.on_event("startup") #--> deprecated
async def startup_span():
    settings = get_settings()
    app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URI)
    app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]

    llm_provider_factory= LLMProviderFactory(settings)

    vectoredb_provider_factory=VectorDBProviderFactory(settings)


    #Generation client
    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)

    # Embedding client
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID,
                                             embedding_size=settings.EMBEDDING_MODEL_SIZE)

    # vector db client
    app.vectordb_client=vectoredb_provider_factory.create(provider =settings.VECTOR_DB_BACKEND)
    app.vectordb_client.connect()

    app.template_parser =TemplateParser(
        language=settings.DEFAULT_LANG,
        default_language= settings.PRIMARY_LANG,
        )

@app.on_event("shutdown") #--> deprecated
async def shutdown_span():
    app.mongo_conn.close()
    app.vectordb_client.disconnect()

#app.router.lifespan.on_startup.append(startup_span)
#app.router.lifespan.on_shutdown.append(shutdown_span)



app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)
