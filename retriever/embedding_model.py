import requests

def get_embedding(text: str):
    url = "http://localhost:11434/api/embed"
    data = {
        "model": "mxbai-embed-large",
        "input": text
    }
    response = requests.post(url, json=data)
    response.raise_for_status()
    return response.json()["embeddings"]