from .BaseController import BaseController
from .ProjectController import ProjectController
import os
from src.helper.config import get_settings ,Settings
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyMuPDFLoader
from src.models import ProcessingEnum
from langchain_text_splitters import RecursiveCharacterTextSplitter                          
class ProcessController(BaseController):
    def __init__(self,project_id:str):
        super().__init__()

        self.project_id=project_id
        self.project_path = ProjectController().get_project_path(project_id=self.project_id)

    def get_file_extention(self , file_id : str):
        return os.path.splitext(file_id)[-1]
    
    def get_file_loader(self,file_id:str ):

        file_ext=self.get_file_extention(file_id=file_id)
        file_path=os.path.join(self.project_path,file_id)

        if not os.path.exists(file_path):
            return None

        if file_ext==ProcessingEnum.TXT.value:
            return TextLoader(file_path,encoding='utf-8')
        
        if file_ext==ProcessingEnum.PDF.value:
            return PyMuPDFLoader(file_path)
        
        return None
    
    def get_file_content(self,file_id:str):

        loader=self.get_file_loader(file_id=file_id)

        if loader:
            return loader.load()

        return None
    
    def process_file_content(self,file_id : str , file_content: list,chunk_size:int=1000,chunk_overlap:int=40):
        text_splitter=RecursiveCharacterTextSplitter(
                                    chunk_size=chunk_size,
                                    chunk_overlap=chunk_overlap,
                                    length_function=len
                                    )
        """
file_content
│
├── Document #1
│   │
│   ├── page_content
│   │      "النص الموجود في الصفحة الأولى..."
│   │
│   └── metadata
│          {
│             "source": "...",
│             "page": 0,
│             ...
│          }
│
├── Document #2
│   │
│   ├── page_content
│   │      "النص الموجود في الصفحة الثانية..."
│   │
│   └── metadata
│          {
│             "source": "...",
│             "page": 1,
│             ...
│          }
│
├── Document #3
│   │
│   ├── page_content
│   │      "النص الموجود في الصفحة الثالثة..."
│   │
│   └── metadata
│          {
│             "source": "...",
│             "page": 2,
│             ...
│          }
│
├── ...
│
└── Document #10
    │
    ├── page_content
    │      "النص الموجود في الصفحة العاشرة..."
    │
    └── metadata
           {
              "source": "...",
              "page": 9,
              ...
           }
"""
        file_content_text=[
            rec.page_content
            for rec in file_content
        ]

        file_content_metadata=[
            rec.metadata
            for rec in file_content
        ]

        chunks = text_splitter.create_documents(file_content_text, metadatas=file_content_metadata)
        return chunks

"""
After text_splitter.create_documents
chunks
│
├── Document
│   ├── page_content = "ABCDEFGHIJ"
│   └── metadata = {...}
│
├── Document
│   ├── page_content = "IJKLMNOPQR"
│   └── metadata = {...}
│
└── Document
    ├── page_content = "QRSTUVWXYZ"
    └── metadata = {...}
"""


