import streamlit as st
import pandas as pd
from langchain_community.vectorstores import Chroma

class AppState:

    def __init__(self):
        
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        if "uploaded_files_info" not in st.session_state:
            st.session_state.uploaded_files_info = [] # List of {'name': 'file.zip', 'content': bytes}
        if 'dataframe' not in st.session_state:
            st.session_state.dataframe = None # single dataframe with all student, percentage and assignments
        if "vectorstore" not in st.session_state:
            st.session_state.vectorstore = None
        if "agent_executor" not in st.session_state:
            st.session_state.agent_executor = None
        if "initial_message_sent" not in st.session_state:
            st.session_state.initial_message_sent = False


    def add_message(self, role, content):
        st.session_state.chat_history.append({"role": role, "content": content})


    def get_chat_history(self):
        return st.session_state.chat_history


    def clear_chat_history(self):
        st.session_state.chat_history = []


    def add_uploaded_file_info(self, file_name, file_content):
        st.session_state.uploaded_files_info.append({
            "name": file_name,
            "content": file_content
        })


    def get_uploaded_files_info(self):
        return st.session_state.uploaded_files_info


    def set_dataframe(self, df: pd.DataFrame):
        st.session_state.dataframe = df


    def get_dataframe(self):
        return st.session_state.dataframe
    

    def set_vectorstore(self, vectorstore: Chroma):
        st.session_state.vectorstore = vectorstore


    def get_vectorstore(self):
        return st.session_state.vectorstore


    def set_agent_executor(self, agent_executor):
        st.session_state.agent_executor = agent_executor


    def get_agent_executor(self):
        return st.session_state.agent_executor


    def set_initial_message_sent(self, sent: bool):
        st.session_state.initial_message_sent = sent


    def get_initial_message_sent(self):
        return st.session_state.initial_message_sent