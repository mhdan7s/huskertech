from flask import Flask, jsonify, request
import requests
from flask_cors import CORS
from dotenv import load_dotenv
import numpy as np
import os
from supabase import create_client

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# --- Configuration for Hugging Face LLaMA/Mistral Chat Model ---
CHAT_MODEL = "meta-llama/llama-3-8b-instruct"
CHAT_API_URL = "https://router.huggingface.co/novita/v3/openai/chat/completions" # Your chat completion API URL
HF_CHAT_API_TOKEN = os.getenv("HUGGING_FACE_API_TOKEN") # Token for chat model

# --- Configuration for Hugging Face Embedding Model ---
EMBEDDING_MODEL_ID = "intfloat/e5-base-v2"
EMBEDDING_API_URL = f"https://router.huggingface.co/hf-inference/models/{EMBEDDING_MODEL_ID}/pipeline/feature-extraction" # Your embedding API URL
HF_EMBEDDING_API_TOKEN = os.getenv("HUGGING_FACE_VECTOR_API_TOKEN") # Token for embedding model

# --- Supabase Configuration ---
SUPABASE_URL = os.get("SUPABASE_URL")
# It's better to get the key from environment variables too for security
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


@app.route("/")
def hello_world():
    return "<p>Hello, World! This is the data from backend. <p>"

@app.route("/api/tickets")
def get_tickets():
    tickets = [
        {"id":1, "issue": "printer not working", "status":"Open"},
        {"id":2, "issue": "Cannot connect to Wifi", "status":"In Progress"},
        {"id":3, "issue": "Software license expired", "status":"Closed"}
    ]
    return jsonify(tickets)


# --- Re-usable function for calling Hugging Face chat API ---
def call_huggingface_chat_api(messages, max_tokens=512, temperature=0.6):
    if not HF_CHAT_API_TOKEN:
        return {"error": "Hugging Face Chat API token is not configured."}

    payload = {
        "model": CHAT_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    chat_headers = {"Authorization": f"Bearer {HF_CHAT_API_TOKEN}", "Content-Type": "application/json"}

    try:
        response = requests.post(CHAT_API_URL, headers=chat_headers, json=payload, timeout=45)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        result = response.json()
        ai_response = result["choices"][0]['message']["content"]
        return {"answer": ai_response.strip()}
    except requests.exceptions.RequestException as e:
        error_message = f"An error occurred with the AI chat API request: {e}"
        print(error_message)
        if hasattr(e, 'response') and e.response is not None:
            print(f"Chat API Response Status: {e.response.status_code}")
            print(f"Chat API Response Body: {e.response.text}")
            if e.response.status_code == 503:
                return {"error": "The AI model is loading. Try again later."}
        return {"error": error_message}

@app.route("/api/ai", methods=['POST'])
def ai_endpoint():
    data = request.get_json()
    if not data or 'question' not in data:
        return jsonify({"error": "No question provided in the request body."}), 400

    user_question = data['question']
    
    messages = [
        {
            "role": "system",
            "content": "You are a specialized IT Support Assistant. Your one and only purpose is to help users with technical problems. "
                       "You must strictly answer questions only about hardware, software, networking, and other IT-related issues. "
                       "If the user asks about any other topic (like history, math, art, general knowledge, or asks you to be creative), you MUST politely refuse. "
                       "When you refuse, state that your function is limited to IT support only. "
                       "For example, if asked 'What is the capital of France?', you should respond with something like: 'I can only assist with IT-related questions.'"
        }, 
        {
            "role": "user",
            "content": user_question
        }
    ]
    
    result = call_huggingface_chat_api(messages)
    if "error" in result:
        status_code = 500
        if "loading" in result["error"]: # Heuristic for loading error
            status_code = 503
        return jsonify({"error": result["error"]}), status_code
    return jsonify({"answer": result["answer"]})


@app.route("/api/duo", methods=['POST'])
def duo_endpoint():
    data = request.get_json()
    if not data or 'question' not in data:
        return jsonify({"error": "No question provided in the request body."}), 400
    
    user_question = data['question']

    messages = [
        {
            "role": "system",
            "content": "You are a specialized IT Support Assistant. Your one and only purpose is to help users with technical problems. "
                       "You must strictly answer questions only about hardware, software, DUO, bypass code, networking, and other IT-related issues. "
                       "If the user asks about any other topic (like history, math, art, general knowledge, or asks you to be creative), you MUST politely refuse. "
                       "When you refuse, state that your function is limited to IT support only. "
                       "For example, if asked 'What is the capital of France?', you should respond with something like: 'I can only assist with IT-related questions.' "
                       "If someone asks a question about a bypass code while logging in the website. Provide them steps as 1. Go to trueyou.nebraska.edu 2. Click on Manage account 3. Log in with their credentials 4. When it comes to the trueyou or DUO page and asks for a bypass code, ask them to click a blue hyper link down there which says other options. They should see an option which says Text message Passcode. Now here the process splits into two: (a) If the user sees Text message passcode option continue in the process with the 5. Click that option and verify yourself. 6. Once they are in ask them to click on the link called Two Factor management. After they click on that link it will take them to a page where they have to click another link called manage two factor devices. 7. The website will ask them to login again. They should select the same option, text message passcode, and login. 8. Finally, they should see a plus icon on the screen which says add a device. 9. They have to click on it and then select DUO mobile and then enter their phone number. 10. If they are doing this on a computer/laptop they should get a QR code which can be scanned opeaning up the DUO mobile app. If they are doing this on phone after the entering the phone number when they hit next, it should directly take them to the DUO mobile app. Now in case we follow method (b) after 4th step, in which the use do not see text message passcode option or any other option other than bypass code ask them to contact the IT desk for help with the contact details as Phone: (402) 472-3970 Email: nusupport@nebraska.edu"
        }, 
        {
            "role": "user",
            "content": user_question
        }
    ]
    
    result = call_huggingface_chat_api(messages)
    if "error" in result:
        status_code = 500
        if "loading" in result["error"]:
            status_code = 503
        return jsonify({"error": result["error"]}), status_code
    return jsonify({"answer": result["answer"]})


# --- Corrected Embedding Function ---
def get_text_embedding(text_input):
    if not HF_EMBEDDING_API_TOKEN:
        return {'error': "Hugging Face Embedding API token is not configured."}

    # The Hugging Face feature-extraction API expects JSON like {"inputs": ["text1", "text2"]}
    # If text_input is a single string, wrap it in a list.
    payload_inputs = [text_input] if isinstance(text_input, str) else text_input

    payload = {
        "inputs": payload_inputs
    }
    
    try:
        embedding_headers = {"Authorization": f"Bearer {HF_EMBEDDING_API_TOKEN}"}
        response = requests.post(EMBEDDING_API_URL, headers=embedding_headers, json=payload)
        response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)
        result = response.json()

        # The API returns a list of lists of floats for single/multiple inputs
        # Example: [[0.1, 0.2, ...]] for single input
        if isinstance(result, list) and len(result) > 0 and isinstance(result[0], list):
            return result[0] # Return the first (and only) embedding vector as a flat list
        else:
            # If the API returned something unexpected but no HTTP error
            print(f"Warning: Unexpected format from embedding API (status 200 OK): {result}")
            return {'error': f"Embedding API returned unexpected data format: {result}"}

    except requests.exceptions.RequestException as e:
        print(f"Error calling embedding API: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Embedding API Response Status: {e.response.status_code}")
            print(f"Embedding API Response Body: {e.response.text}")
        return {'error': f"Failed to get embedding: {e}"}

# --- Supabase Document Retrieval Function ---
def get_docs(question_vector):
    # This function expects a flat list of floats, or an error dictionary from get_text_embedding
    
    # Check for error dict from embedding function
    if isinstance(question_vector, dict) and 'error' in question_vector:
        print(f"Error passed from embedding to get_docs: {question_vector['error']}")
        # Propagate the error message for better debugging
        raise ValueError(f"Failed to retrieve documents due to embedding error: {question_vector['error']}")

    # If it's not an error, it must be a list of floats.
    if not isinstance(question_vector, list) or not all(isinstance(x, (float, int)) for x in question_vector):
        raise TypeError(f"Expected question_vector to be a list of floats, but received type {type(question_vector)} or invalid contents.")

    vector_list = question_vector # It should already be the correct format

    try:
        # Assuming 'get_similar_documents' is correctly set up in your Supabase database
        response = supabase.rpc('get_similar_documents', {'query_embedding': vector_list}).execute()
        
        # Check for errors in Supabase response itself (not HTTP errors from postgrest-py)
        if response.data is None and response.error:
            print(f"Supabase RPC error: {response.error}")
            raise RuntimeError(f"Supabase RPC call failed: {response.error.get('message', 'Unknown error')}")
        
        return [row['doc_context'] for row in response.data]
    except Exception as e:
        print(f"Error during Supabase RPC call: {e}")
        raise # Re-raise the exception to be caught by the calling endpoint

# --- RAG Endpoint ---
@app.route("/api/rag", methods=["POST"])
def rag_endpoint():
    data = request.get_json()
    question = data.get("question") # Use .get() for safer access

    if not question:
        return jsonify({"error": "Question is required"}), 400

    # 1. Get the embedding for the question
    question_vector = get_text_embedding(question)

    # Check if embedding failed and returned an error dict
    if isinstance(question_vector, dict) and 'error' in question_vector:
        # Return the error message to the client
        return jsonify({"error": f"Failed to generate embedding: {question_vector['error']}"}), 500

    # 2. Retrieve relevant documents from Supabase
    try:
        docs = get_docs(question_vector)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    context = "\n".join(docs)
    
    # Provide a fallback if no relevant context is found
    if not context:
        print("No relevant context found for the question. Proceeding without context.")
       
        pass # Allow the LLM to answer without context if no docs were found

    # 3. Prepare message for the chat model
    rag_system_content = (
        "You are a specialized IT Support Assistant. Your one and only purpose is to help users with technical problems. "
        "You must strictly answer questions only about hardware, software, networking, and other IT-related issues. "
        "If the user asks about any other topic (like history, math, art, general knowledge, or asks you to be creative), you MUST politely refuse. "
        "When you refuse, state that your function is limited to IT support only. "
        "For example, if asked 'What is the capital of France?', you should respond with something like: 'I can only assist with IT-related questions.' "
        f"Here is some context to help you answer: {context}" # Context injected here
    )

    messages = [
        {"role": "system", "content": rag_system_content},
        {"role": "user", "content": question}
    ]

    # 4. Call the Hugging Face chat API with the RAG prompt
    chat_result = call_huggingface_chat_api(messages)
    
    if "error" in chat_result:
        status_code = 500
        if "loading" in chat_result["error"]:
            status_code = 503
        return jsonify({"error": chat_result["error"]}), status_code
    
    return jsonify({"answer": chat_result["answer"]})

if __name__ == '__main__':
    app.run(debug=True)