'''
The following code gets context based on user query by searching through chromadb. 
Call parameters:
text - query
k - the number of results (chunks of context) to return
collection_name - which collection to search in chromadb
Function returns:
string - k context chunks joined by newline 
'''

import chromadb
from retriever.embedding_model import get_embedding

def get_relevant_chunks(query, k=3, collection_name="products"):
    client = chromadb.Client()
    collection = client.get_collection(name=collection_name)
    query_embedding = get_embedding(query)
    results = collection.query(query_embeddings=[query_embedding], n_results=k)
    
    return "\n".join(results['documents'][0])
