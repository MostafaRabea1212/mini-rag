from enum import Enum

class ResponseSignal(Enum):
    FILE_VALIDATED_SUCCESS ="File_Validated_Successfully"
    FILE_TYPE_NOT_SUPPORTED ="File_Type_Not_Supported"
    FILE_SIZE_EXCEEDED  = "File_size_Exceeded"
    FILE_UPLOADED_SUCCESS ="File_Uploaded_Success"
    FILE_UPLOADED_FAILED ="File_Uploaded_Failed"
    PROCESSING_FAILED ="Processing_Failed"
    PROCESSING_SUCCESS ="Processing_Success"
    NO_FILE_ERROR="not_found_files"
    FILE_ID_ERROR = "on_file_found_with_this_id"
    PROJECT_NOT_FOUND_ERROR= "project_not_found"
    INSERT_INTO_VECTORDB_ERROR ="insert_into_vectordb_error"
    INSERT_INTO_VECTORDB_SUCCESS ="insert_into_vectordb_success"
    VECTOR_COLLECTION_RETRIVED = "vectordb_collection_retrieved"
    VECTORDB_SEARCH_ERROR = "vectordb_search_error"
    VECTORDB_SEARCH_SUCCESS ="vectordb_search_success"
    RAG_ANSWER_ERROR = "rag_answer_error"
    RAG_ANSWER_SUCCES = "rag_answer_success"
    