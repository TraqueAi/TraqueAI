import streamlit as st
from bayesrag.config import DATA_DIR, QDRANT_COLLECTION,ID
from bayesrag.data_loader import load_directory_pdf
from bayesrag.text_splitter import split_texts
from bayesrag.vector_db import VectorDB
from bayesrag.retriever import get_context
from bayesrag.generator import generate_response
from bayesrag.mq import Mqttclient
from qdrant_client import QdrantClient
import warnings
from cryptography.utils import CryptographyDeprecationWarning

warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning, message="ARC4 has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.ARC4 and will be removed from this module in 48.0.0.")

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
vectorDb=VectorDB(QDRANT_COLLECTION)

    # Create vector database and upsert embeddings
vectorDb.create_db()
def insert_data(file):
    with open(DATA_DIR / file.name, "wb") as f:
        f.write(file.getbuffer())

    # Load and split documents
    documents = load_directory_pdf(DATA_DIR)
    text_chunks = split_texts(documents)
    vectorDb=VectorDB(QDRANT_COLLECTION)

    # Create vector database and upsert embeddings
    vectorDb.upsert_embeddings(text_chunks)

def main():
    st.title("Lawyer-Based Chatbot")

    # Sidebar for file upload and actions
    st.sidebar.title("Upload Document")
    uploaded_file = st.sidebar.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file is not None:
        insert_data(uploaded_file)
        st.sidebar.success("Document uploaded and processed successfully!")

    # Sidebar actions
    with st.sidebar.expander("Actions", expanded=True):
        if st.button("Send Vector"):
            qclient = QdrantClient(url="http://localhost:6333")  # Update URL if needed
            client = Mqttclient(replyTopic=f"USER_TOPIC-{ID}", isAdmin=False)
            scroll_result = qclient.scroll(collection_name=QDRANT_COLLECTION, with_vectors=True)
            client.send_vector(scroll_result)
            st.sidebar.success("Vector sent successfully.")

    st.header("Chat with your documents")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input
    user_input = st.chat_input("Type your question here...")
    
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
        
        result = get_context(user_input)

        with st.chat_message("assistant"):
            response_container = st.empty()
            response_text = ""
            for response_part in generate_response(user_input, result):
                response_text += response_part
                response_container.markdown(response_text)
        
        st.session_state.messages.append({"role": "assistant", "content": response_text})

if __name__ == "__main__":
    main()
