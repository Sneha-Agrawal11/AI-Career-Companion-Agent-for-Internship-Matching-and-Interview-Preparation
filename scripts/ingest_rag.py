import os
import hashlib
import docx
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer

KNOWLEDGE_DOC_PATH = "InternMatch_Product_Knowledge.docx"
CHROMA_DB_PATH = os.path.join("app", "data", "chroma_db")
COLLECTION_NAME = "internmatch_knowledge"

def get_text_chunks(docx_path):
    doc = docx.Document(docx_path)
    chunks = []
    current_chunk = ""
    
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
            
        # Basic chunking: group small paragraphs, split on very long ones
        if len(current_chunk) + len(text) > 1000:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = text
        else:
            current_chunk += "\n" + text if current_chunk else text
            
    if current_chunk:
        chunks.append(current_chunk.strip())
        
    return chunks

def main():
    if not os.path.exists(KNOWLEDGE_DOC_PATH):
        print(f"Error: {KNOWLEDGE_DOC_PATH} not found.")
        return

    print("Extracting text from DOCX...")
    chunks = get_text_chunks(KNOWLEDGE_DOC_PATH)
    print(f"Found {len(chunks)} chunks.")

    print("Initializing ChromaDB...")
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    
    # We use SentenceTransformer natively, but Chroma has a built-in wrapper for it
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=sentence_transformer_ef,
        metadata={"hnsw:space": "cosine"}
    )
    
    print("Ingesting chunks (idempotent)...")
    ids = []
    documents = []
    metadatas = []
    
    for i, chunk in enumerate(chunks):
        # Create a deterministic ID based on content hash to ensure idempotency
        chunk_hash = hashlib.md5(chunk.encode('utf-8')).hexdigest()
        ids.append(f"chunk_{chunk_hash}")
        documents.append(chunk)
        metadatas.append({"source": KNOWLEDGE_DOC_PATH, "chunk_index": i})
        
    # Upsert handles idempotent inserts/updates
    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )
    
    print(f"Successfully ingested {len(chunks)} chunks into ChromaDB at {CHROMA_DB_PATH}.")

if __name__ == "__main__":
    main()
