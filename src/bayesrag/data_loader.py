from pathlib import Path
from langchain_community.document_loaders import PyPDFDirectoryLoader,PyPDFLoader

def load_directory_pdf(directory_path: Path):
    loader = PyPDFDirectoryLoader(directory_path)
    docs = loader.load()
    return docs

