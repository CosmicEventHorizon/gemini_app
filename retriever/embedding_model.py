'''
The following code uses all-MiniLM-L6-v2 to generate embeddings of text. 
Call parameters:
text - text to convert to embeddings
Function returns:
NumPy array containing float numbers corresponding to the text.
'''

from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text: str):
    return model.encode([text])[0]
