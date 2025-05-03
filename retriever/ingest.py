'''
The following code splits a pdf file into max_tokens chunks then maps the chunks to embeddings and stores
them in a chromadb database in memory (these functions should run once to generate the database)
Call parameters:
text - text to convert to embeddings
Function returns:
NumPy array containing float numbers corresponding to the text.
'''


import fitz 
import chromadb
from retriever.embedding_model import get_embedding

#given a text, split it into chunks of 500 words with an overlap of 50 between the chunks
#returns an array of chunks
def chunk_text(text, max_tokens=500, overlap=50):
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = words[i:i+max_tokens]
        chunks.append(" ".join(chunk))
        i += max_tokens - overlap
    return chunks

'''
Given a pdf file, 
'''
def ingest_pdf(pdf_path, collection_name="products"):
    #Use fitz to open the pdf file, read each page and 
    #concatenate all text into a string separated by newline
    doc = fitz.open(pdf_path)
    full_text_parts = []
    for page in doc:
        page_text = page.get_text()
        full_text_parts.append(page_text)  
    full_text = "\n".join(full_text_parts) 

    #split the full_text to chunks
    #for each chunk, convert it into embeddings and store it in an embeddings array
    chunks = chunk_text(full_text)
    embeddings = [get_embedding(c) for c in chunks]

    #saves to ./data/chroma_db/
    client = chromadb.PersistentClient(path="data/chroma_db")  
    #if collection exists delete it and then create a new collection
    if collection_name in [c.name for c in client.list_collections()]:
        client.delete_collection(name=collection_name)
    collection = client.create_collection(name=collection_name)

    #generate ids from 0 to len(chunks) and store it in chromadb where we have ids=doc-{i}, documents=chunk, embeddings=embeddings elements
    ids = [f"doc-{i}" for i in range(len(chunks))]    
    collection.add(documents=chunks, embeddings=embeddings, ids=ids)
