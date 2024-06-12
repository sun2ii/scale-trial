import streamlit as st
import requests
import json
# from dotenv import load_dotenv
import os

# Load environment variables from .env file
# load_dotenv()

# Retrieve the API key from environment variables
# api_key = os.getenv('API_KEY')
api_key = st.secrets["SCALE_API_KEY"]
print(api_key);

# Knowledge base dictionary
knowledge_base = {
    'JPMorgan': '32cabd39-c257-493e-ab12-517905d4a800',
    'Farmers': 'f682abae-a359-4025-884a-b5e19529e76f',
    'Chegg': '1f8e6b89-5133-4fba-bfb1-fbb2e6213e0d',
}

# Function to query the knowledge base
def query_knowledge_base(query, knowledge_base_id):
    url = f"https://api.egp.scale.com/v3/knowledge-bases/{knowledge_base_id}/query"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "x-api-key": api_key
    }
    data = {
        "include_embeddings": False,
        "verbose": False,
        "query": query,
        "top_k": 3
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

# Function to get chat completion with streaming
def get_chat_completion(content, query):
    url = "https://api.egp.scale.com/v3/chat-completions"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "x-api-key": api_key
    }
    instructions = f"Provide a concise summary that is relevant to the query provided ({query}) and easily understood. At the end provide 1 simple idea to further prompt."
    data = {
        "model": "gpt-4",
        "memory_strategy": {"name": "last_k", "params": {"k": 10}},
        "model_parameters": {"temperature": 0.2},
        "instructions": instructions,
        "stream": True,
        "messages": [{"role": "system", "content": content}]
    }
    with requests.post(url, headers=headers, json=data, stream=True) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            if line:
                yield json.loads(line.decode('utf-8').replace("data: ", ""))

# Streamlit app
st.title("Scale Assessment (Banking, Insurance, Education)")

if 'history' not in st.session_state:
    st.session_state.history = []

# Display chat history
for message in st.session_state.history:
    if message["role"] == "user":
        st.markdown(f"**User:** {message['content']}")
    else:
        st.markdown(f"**Assistant:** {message['content']}")

# User input form at the end to keep the responses on top
with st.form(key='query_form'):
    col1, col2 = st.columns([3, 1])
    with col1:
        query = st.text_input("Enter your query:")
    with col2:
        selected_kb = st.selectbox("Select Knowledge Base", list(knowledge_base.keys()))
    
    submit_button = st.form_submit_button(label='Submit')

knowledge_base_id = knowledge_base[selected_kb]

if submit_button and query:
    # Add user message to history
    st.session_state.history.append({"role": "user", "content": query})

    # Query the knowledge base
    st.markdown("**Assistant:** Querying knowledge base...")
    kb_response = query_knowledge_base(query, knowledge_base_id)
    chunks = kb_response['chunks']
    content = ' '.join(chunk['text'] for chunk in chunks)

    # Stream chat completion
    st.markdown("**Assistant:** Getting chat completion...")
    chat_response_content = ""
    chat_placeholder = st.empty()
    for chunk in get_chat_completion(content, query):
        if "chat_completion" in chunk and "message" in chunk["chat_completion"] and "content" in chunk["chat_completion"]["message"]:
            chat_response_content += chunk["chat_completion"]["message"]["content"]
            chat_placeholder.markdown(f"**Assistant:** {chat_response_content}")

    # Add assistant message to history
    st.session_state.history.append({"role": "assistant", "content": chat_response_content})