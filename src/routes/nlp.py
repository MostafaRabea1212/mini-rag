from fastapi import FastAPI,APIRouter,Depends,UploadFile,status,Request
from fastapi.responses import JSONResponse
import os
import logging
from src.routes.schemes.nlp import PushRequest ,SearchRequest
from src.models.ProjectModel import ProjectModel
from src.models.ChunkModel import ChunkModel
from src.controllers.NlpController import NlpController
from src.models import ResponseSignal

logger=logging.getLogger("uvicorn.error")

nlp_router=APIRouter(
    prefix="/api/v1/nlp",
    tags=["api_v1" , "nlp"]
    )

@nlp_router.post("/index/push/{project_id}")
async def index_project(request :Request , 
                        project_id :str,
                        push_request :PushRequest ):

    projectmodel=await ProjectModel.create_instance(
        db_client=request.app.db_client
        )

    chunk_model=await ChunkModel.create_instance(
        db_client=request.app.db_client
    )
    
    project= await projectmodel.get_project_or_create_one(
        project_id=project_id
        )

    if not project:
        return JSONResponse(
            status_code =status.HTTP_400_BAD_REQUEST,
            content={
                "signal" : ResponseSignal.PROJECT_NOT_FOUND_ERROR.value

            }
        )

    nlpcontroller=NlpController(vectordb_client=request.app.vectordb_client,
                                generation_client=request.app.generation_client,
                                embedding_client=request.app.embedding_client)
    has_record = True
    page_no = 1
    inserted_item_count = 0
    idx = 0 

    while has_record:
        page_chunks=await chunk_model.get_project_chunk(project_id=project.id , page_no=page_no)

        if len(page_chunks):
            page_no+=1
        if not page_chunks or len(page_chunks) == 0 :
            has_record =False
            break

        chunks_ids=list(range(idx , idx +len (page_chunks)))
        idx+=len(chunks_ids)

        is_inserted= nlpcontroller.index_into_vector_db(project =project ,
                                                        chunks=page_chunks,
                                                        chunks_ids = chunks_ids,
                                                        do_reset=push_request.do_reset)

        if not is_inserted:
            return JSONResponse(
            status_code =status.HTTP_400_BAD_REQUEST,
            content={
                "signal" : ResponseSignal.INSERT_INTO_VECTORDB_ERROR.value
            }
        )
        inserted_item_count += len(page_chunks)
    return JSONResponse(
                    content={
                "signal" : ResponseSignal.INSERT_INTO_VECTORDB_SUCCESS.value,
                "inserted_item_count" :inserted_item_count
            }
    )
@nlp_router.get("/index/info/{project_id}")
async def get_proejct_index_info(request : Request , project_id :str):

    projectmodel=await ProjectModel.create_instance(
        db_client=request.app.db_client
        )
    
    project= await projectmodel.get_project_or_create_one(
        project_id=project_id
        )

    nlpcontroller=NlpController(
                vectordb_client=request.app.vectordb_client,
                generation_client=request.app.generation_client,
                embedding_client=request.app.embedding_client)
    
    collection_info=nlpcontroller.get_vector_db_collection_info(project=project)

    return  JSONResponse(
        content={
            "signal" : ResponseSignal.VECTOR_COLLECTION_RETRIVED.value, 
            "collection_info" : collection_info
        }
    )

@nlp_router.post("/index/search/{project_id}")
async def search_index(request : Request , project_id : str ,search_request :SearchRequest):

    projectmodel=await ProjectModel.create_instance(
        db_client=request.app.db_client
        )
    
    project= await projectmodel.get_project_or_create_one(
        project_id=project_id
        )

    nlpcontroller=NlpController(
                vectordb_client=request.app.vectordb_client,
                generation_client=request.app.generation_client,
                embedding_client=request.app.embedding_client)
    reuslts= nlpcontroller.search_vector_db_collection(text = search_request.text ,
                                                       project= project,
                                                       limit=search_request.limit)
    if not reuslts:
        return JSONResponse(
            content ={
                "signal" : ResponseSignal.VECTORDB_SEARCH_ERROR.value           }
        )
    
    return JSONResponse(
        content ={
            "signal" : ResponseSignal.VECTORDB_SEARCH_SUCCESS.value,
            "results" : reuslts
        }
    )


