import chromadb
from retriever.embedding_model import get_embedding

def get_relevant_chunks(query, collection_name, k=3):
    client = chromadb.PersistentClient(path="data/chroma_db") 
    try:
        collection = client.get_collection(name=collection_name)
        query_embedding = get_embedding(query)
        results = collection.query(query_embeddings=[query_embedding], n_results=k)
        return "\n".join(results['documents'][0])
    except:
        return None
