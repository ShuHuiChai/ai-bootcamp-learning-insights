import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_experimental.text_splitter import SemanticChunker
from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader, TextLoader
import chromadb
import os
from dotenv import load_dotenv

from langchain.prompts import PromptTemplate
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.chains import RetrievalQA

import tiktoken


def count_tokens(text):
    encoding = tiktoken.encoding_for_model('gpt-4o-mini')
    return len(encoding.encode(text))


def get_embeddings_model():
    if load_dotenv():
        API_KEY=os.getenv('OPENAI')
    else:
        API_KEY=st.secrets('OPENAI')
    
    return OpenAIEmbeddings(model='text-embedding-3-small', api_key=API_KEY)


def create_vectorstore():

    embeddings_model = get_embeddings_model()

    doc_list = [
        'EdTech Masterplan 2030 _ MOE.pdf',
        'Key Applications of Technology.pdf'
    ]

    loaded_docs = []

    for doc in doc_list:
        try:
            markdown_path = os.path.join('../docs', doc)
            loader = PyPDFLoader(markdown_path)
            data = loader.load()
            loaded_docs.extend(data)
        except Exception as e:
            print(f"Error loading {doc}: {e}")
            continue

    # print("Total documents loaded:", len(loaded_docs))

    # for doc in loaded_docs:
    #     print(f'{doc.metadata.get("source")} has {count_tokens(doc.page_content)} tokens')

    text_splitter = SemanticChunker(embeddings_model)

    splitted_docs = text_splitter.split_documents(loaded_docs)

    vectorstore = Chroma.from_documents(
        documents=splitted_docs,
        embedding=embeddings_model,
        collection_name='semantic_embedding',
        persist_directory='../vector_db'
    )


def load_vectorstore_from_directory():
    client = chromadb.PersistentClient(path="../vector_db")
    vectorstore = Chroma(
        client=client,
        collection_name="semantic_embedding",
        embedding_function=get_embeddings_model()
    )

    return vectorstore


# create_vectorstore() # run this function as a python script, so that user does not need to wait for vectorstore to be created from scratch. comment out when completed.