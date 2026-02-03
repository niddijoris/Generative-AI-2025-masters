import os
import glob
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

# Load environment variables
load_dotenv()

DATA_PATH = "data"
DB_PATH = "vector_db"

def load_documents():
    documents = []
    pdf_files = glob.glob(os.path.join(DATA_PATH, "*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in {DATA_PATH}")
        return []

    print(f"Found {len(pdf_files)} PDF files.")
    for pdf_file in pdf_files:
        print(f"Loading {pdf_file}...")
        try:
            loader = PyPDFLoader(pdf_file)
            docs = loader.load()
            documents.extend(docs)
        except Exception as e:
            print(f"Error loading {pdf_file}: {e}")
            
    return documents

def split_documents(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")
    return chunks

def save_to_faiss(chunks):
    embeddings = OpenAIEmbeddings()
    
    print("Creating vector database...")
    db = FAISS.from_documents(chunks, embeddings)
    db.save_local(DB_PATH)
    print(f"Saved {len(chunks)} chunks to {DB_PATH}.")

def main():
    documents = load_documents()
    if not documents:
        return
    
    chunks = split_documents(documents)
    save_to_faiss(chunks)

if __name__ == "__main__":
    main()
