import os
import base64
import tempfile
from google import genai
from google.genai.types import EmbedContentConfig

#Google authentication requires the project_id and the service account key
project_id = os.environ["PROJECT_ID"]
creds_data = os.environ["GOOGLE_APPLICATION_CREDENTIALS_BASE64"]

#the json key is encoded as base64 key which is decoded here back to a json file
key_path = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
key_path.write(base64.b64decode(creds_data))
key_path.close()

#environment variables to be used for authentication
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path.name
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
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
