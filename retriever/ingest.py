import fitz 
import chromadb
from retriever.embedding_model import get_embedding
import sqlite3
from threading import Thread

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


def add_user_report(username,report_name):
    conn = sqlite3.connect('instance/users.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users_reports (username, report_name) VALUES (?, ?)",
        (username, report_name)
    )
    conn.commit()
    conn.close()

def get_sql_entry(username):
    conn = sqlite3.connect('instance/users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users_reports WHERE username = ?', (username,))
    user = cursor.fetchall()
    conn.close()
    return user

def get_chromadb_reports(report_names):
    client = chromadb.PersistentClient('data/chroma_db')
    reports = [c.name for c in client.list_collections() if c.name in report_names]
    return reports

def check_user_report(report_name):
    conn = sqlite3.connect('instance/users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users_reports WHERE report_name = ?', (report_name,))
    report = cursor.fetchone()
    conn.close()
    if report is None:
        return False
    else:
        return True

def delete_user_report(report_name):
    conn = sqlite3.connect('instance/users.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users_reports WHERE report_name = ?', (report_name,))
    conn.commit()
    conn.close()

def ingest_pdf(username, report_name):
    #Use fitz to open the pdf file, read each page and 
    #concatenate all text into a string separated by newline
    pdf_path = 'context/' + report_name + '.pdf'
    doc = None
    try:
        doc = fitz.open(pdf_path)
    except:
        return False
    
    add_user_report(username,report_name)
    def process_chunks_background(doc, report_name):
        try:
            # split the full_text to chunks
            full_text_parts = []
            for page in doc:
                page_text = page.get_text()
                full_text_parts.append(page_text)  
            full_text = "\n".join(full_text_parts) 
            chunks = chunk_text(full_text)

            # for each chunk, convert it into embeddings and store it in an embeddings array
            n_chunks = len(chunks)
            i = 1
            embeddings = []
            for c in chunks:
                print(f"Chunk: {i} of {n_chunks}")
                embeddings.append(get_embedding(c))
                i = i + 1

            client = chromadb.PersistentClient(path="data/chroma_db") 

            # if collection exists delete it and then create a new collection
            if report_name in [c.name for c in client.list_collections()]:
                client.delete_collection(name=report_name)
            collection = client.create_collection(name=report_name)

            # generate ids from 0 to len(chunks) and store it in chromadb
            ids = [f"doc-{i}" for i in range(len(chunks))]    
            collection.add(documents=chunks, embeddings=embeddings, ids=ids)
        except Exception as e:
            print(e)
            delete_user_report(report_name)

    # Start the background task
    background_thread = Thread(target=process_chunks_background, args=(doc, report_name))
    background_thread.start()
    
    return True
