from enum import Enum

class ResponseSignal(Enum):
    FILE_VALIDATED_SUCCESS ="File_Validated_Successfully"
    FILE_TYPE_NOT_SUPPORTED ="File_Type_Not_Supported"
    FILE_SIZE_EXCEEDED  = "File_size_Exceeded"
    FILE_UPLOADED_SUCCESS ="File_Uploaded_Success"
    FILE_UPLOADED_FAILED ="File_Uploaded_Failed"