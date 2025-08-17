import streamlit as st
import pandas as pd
from langchain.tools import BaseTool
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from typing import Type
from pydantic import BaseModel, Field
import os
import chromadb
from dotenv import load_dotenv


__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

class RAGToolInput(BaseModel):
    query: str = Field(description="The natural language question to ask about how to apply technology in the classroom that is aligned with the EdTech Masterplan 2030 and the Key Applications of Technology framework.")

class RAGTool(BaseTool):
    name: str = "knowledge_base"
    description: str = "Useful for answering questions about the EdTech Masterplan 2030 and Key Applications of Technology in the classroom."
    args_schema: Type[BaseModel] = RAGToolInput

    vectorstore: Chroma
    
    def _run(self, query: str):

        if not self.vectorstore:
            return "Error: No vectorstore available."
        
        if load_dotenv():
            llm = ChatOpenAI(
                model='gpt-4o-mini',
                temperature=0,
                api_key=os.getenv('OPENAI'),
            )
        else:
            llm = ChatOpenAI(
                model='gpt-4o-mini',
                temperature=0,
                api_key=st.secrets('OPENAI'),
            )

        if not llm:
            return "Error: LLM not initialized. Check OPENAI key."
        
        try:
            
            template = """You are an assistant for question-answering tasks related to the EdTech Masterplan 2030 and Key Applications of Technology in the classroom.
                Use the following pieces of retrieved context to answer the question.
                If you don't know the answer, just say you don't know.
                Keep the answer concise and relevant to the retrieved information.\n\n
                
                Context: {context}

                Question: {question}

                Answer:
            """

            prompt_template = PromptTemplate.from_template(template)
            
            retriever = self.vectorstore.as_retriever()

            def format_docs(docs):
                return "\n\n".join(doc.page_content for doc in docs)

            rag_chain = (
                {"context": retriever | format_docs, "question": RunnablePassthrough()}
                | prompt_template
                | llm
                | StrOutputParser()
            )

            response = rag_chain.invoke(query)

            return response

        except Exception as e:
            return f"Error: {str(e)}"
