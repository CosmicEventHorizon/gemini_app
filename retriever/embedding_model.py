'''
The following code uses Google's embedding model to generate embeddings given text
Call parameters:
text - text to convert to embeddings
Function returns:
NumPy array containing float numbers corresponding to the text.
'''

import os
import base64
import tempfile
from google import genai
from google.genai.types import EmbedContentConfig
from config import PROJECT_ID
from config import GOOGLE_APPLICATION_CREDENTIALS_BASE64


#the json key is encoded as base64 key which is decoded here back to a json file
key_path = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
key_path.write(base64.b64decode(GOOGLE_APPLICATION_CREDENTIALS_BASE64))
key_path.close()

#environment variables to be used for authentication
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path.name
os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"

client = genai.Client()

def get_embedding(text: str):
    response = client.models.embed_content(
        model="text-embedding-005",
        contents=[text],
        config=EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT",
            output_dimensionality=768,
        ),
    )
    return response.embeddings[0].values
