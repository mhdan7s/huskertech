from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv
import requests
from supabase import create_client

SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD")
SUPABASE_KEY = os.getenv("SERVICE_KEY")

# https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2 => this link is if you want to compare a sentence to a list of sentences.

load_dotenv()

# Here we extract the data from pdf using PdfReader
# reader1 = PdfReader("C:/Users/Anas/backend/text/Connecting to Campus WiFi (eduroam).pdf")
# reader2 = PdfReader("C:/Users/Anas/backend/text/Connecting to Guest WiFi (NU-Guest).pdf")
reader3 = PdfReader("C:/Users/Anas/backend/text/bypass.pdf")
text = ""
for page in reader3.pages:
    text += page.extract_text()


# # here we convert the text into vector embeddings

model_id = "intfloat/e5-base-v2"
HF_VECTOR_API_TOKEN = os.getenv("HUGGING_FACE_VECTOR_API_TOKEN")


api_url = f"https://router.huggingface.co/hf-inference/models/{model_id}/pipeline/feature-extraction"
headers = {"Authorization": f"Bearer {HF_VECTOR_API_TOKEN}"}


def embedding(texts):
    response = requests.post(api_url, headers=headers, json = texts)
    return response.json()

texts = {
    "inputs" : text
}

output = embedding(texts)



SUPABASE_URL = os.get("SUPABASE_URL")
SUPABASE_KEY = os.get("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

data = {
    "context": text,
    "embedding" : output
}

supabase.table("documents").insert(data).execute()