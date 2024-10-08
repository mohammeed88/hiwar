import streamlit as st
from dotenv import load_dotenv
import os
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
import google.generativeai as genai
import pandas as pd
from htmlTemplates import css, bot_template, user_template, header_template

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Define base directory
BASE_DIR = Path(__file__).resolve().parent

# Load the data
def load_data(file_path):
    data = pd.read_csv(file_path, engine='python')
    data = data.dropna()
    texts = data['Combined'].tolist()
    return texts

# Load vector store from a file
def load_vectorstore():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.load_local(BASE_DIR / "vectorstore", embeddings=embeddings, allow_dangerous_deserialization=True)
    return vectorstore

# Initialize conversational chain
def get_conversation_chain(vectorstore):
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    return {"vectorstore": vectorstore, "memory": memory, "messages": []}

# Handle user input
def handle_user_input(query, conversation):
    vectorstore = conversation['vectorstore']
    memory = conversation['messages']
    
    # Retrieve the most relevant chunks
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    retrieved_docs = retriever.get_relevant_documents(query)
    retrieved_answers = " \n ".join([doc.page_content for doc in retrieved_docs])
    print('---------------------------------------------------------------------------')
    print(retrieved_answers)
    print('---------------------------------------------------------------------------')

    # Add the new user query to the memory
    memory.append({"role": "user", "content": query})
    
    # Prepare the system message and user query
    system_message = ("You are HiwarBot, an Islamic chatbot designed to help users learn about Islam. "
                      "You should provide answers that are informative, respectful, and based on authentic Islamic teachings. "
                      "Only respond to questions that are directly related to Islam, and do so in English only. "
                      "If a query is unrelated to Islam or in a different language, politely inform the user that you can only answer questions about Islam in English. "
                      "Make sure to clarify any terms or concepts that might be unfamiliar to non-Muslims. "
                      "The context provided includes dialogue chats between an agent and a visitor. "
                      "Use this context to inform your responses and maintain a conversational tone. "
                      "If you cannot provide an answer based on the context, state: 'I'm sorry, I can't answer this question at the moment. Please consult a knowledgeable person or a reliable source for accurate information.'")
    
    user_query = f"Generate a response based on the following context: {retrieved_answers} Query: {query}"

    # Create the model
    generation_config = {
      "temperature": 0.5,
      "max_output_tokens": 500,
    }
    model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=generation_config)

    # Start a chat session
    chat_session = model.start_chat(history=[])

    # Send the system message
    chat_session.send_message(system_message)

    # Send the user query and get the response
    response = chat_session.send_message(user_query)

    assistant_message = response.text
    
    # Add the assistant's response to the memory
    memory.append({"role": "assistant", "content": assistant_message})
    
    # Update the conversation dictionary
    conversation['messages'] = memory
    
    return [{"role": "user", "content": query}, {"role": "assistant", "content": assistant_message}]

# Main Streamlit app
def main():
    st.set_page_config(page_title="HiwarBot")
    st.write(css, unsafe_allow_html=True)

    # Load and process the text data
    if 'conversation' not in st.session_state:
        vectorstore = load_vectorstore()
        st.session_state.conversation = get_conversation_chain(vectorstore)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display header
    st.markdown(header_template.replace("{{MSG}}", "Welcome to HiwarBot! [gemini-1.5-flash]"), unsafe_allow_html=True)

    # Create a container for the chat messages
    chat_container = st.container()
    
    # Display chat history in the container
    with chat_container:
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.markdown(user_template.replace("{{MSG}}", message['content']), unsafe_allow_html=True)
            else:
                st.markdown(bot_template.replace("{{MSG}}", message['content']), unsafe_allow_html=True)

    # Add a text input box for user input
    st.text_input(label="Ask a question about Islam:", max_chars=300, key='user_input', on_change=handle_input_change)

def handle_input_change():
    user_question = st.session_state.user_input
    if user_question and st.session_state.conversation:
        response = handle_user_input(user_question, st.session_state.conversation)
        st.session_state.chat_history.extend(response)
        st.session_state.user_input = ""  # Clear the input box after submission

if __name__ == '__main__':
    main()
