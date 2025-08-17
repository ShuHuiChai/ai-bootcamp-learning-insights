__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate
from handlers.tools.pandasai_tool import PandasAITool
from handlers.tools.rag_tool import RAGTool
import os
from dotenv import load_dotenv


def create_agent_executor(dataframe:pd.DataFrame, vectorstore):
    """
    Creates and returns a LangChain AgentExecutor with PandasAI and RAG tools.
    """
    
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
        st.error("Cannot create agent: LLM not initialized.")
        return None
        
    if dataframe is None:
        st.warning("Cannot create agent: No dataframe provided.")
        return None
    
    if vectorstore is None:
        st.warning("Cannot create agent: No vectorstore provided.")

    tools = []
    
    try:
        pandas_tool = PandasAITool(dataframe=dataframe)
        tools.append(pandas_tool)

        rag_tool = RAGTool(vectorstore=vectorstore)
        tools.append(rag_tool)
        
    except Exception as e:
        st.error(f"Error creating tools: {e}")
        return None
    
    if not tools:
        st.warning("No tools available for agent.")
        return None

    try:
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are a helpful AI assistant that can analyze student performance data and provide suggestions on what teachers can do to improve student outcomes. "
                    You have access to the following tools.

                    Instructions:
                    1. Use the 'data_analyser' tool to answer questions about the assignments and student performance in the assignments. Make sure you analyse and use all the rows in all the dataframes in your calculations. Do not use .head(), .sample(), or sample the data. If you only have five rows in your analysis, check and load the ORIGINAL dataframes again.
                    2. Use the 'knowledge_base' tool to retrieve information on the EdTech Masterplan 2030 and key applications of technology.
                    3. Combine information from both sources as needed to answer complex queries, especially when asked for interventions or what teachers can do to help improve student performance according to the EdTech Masterplan and Key Applications of Technology.
                    For example, if asked 'For student X, what interventions can I provide based on their low score in math?', you should first use 'data_analyser' to get student X's math score and potentially other relevant data, then use 'knowledge_base' to find interventions relevant to the EdTech Masterplan and Key Applications of Technology, and finally synthesize the information. 
                    4. If you are not asked for suggestions for improvements or interventions, do not provide any suggestions. 
                    5. You should only use the tools provided and not come up with your own suggestions. 
                    6. Always provide a helpful and comprehensive answer. If you cannot find relevant information, state that you don't know.
                    7. Format your response in a way that is easy to read and understand. Use markdown for tables and lists where appropriate. Do not use code blocks or code snippets or data types such as dictionaries or json in your response.
                    """
                ),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )
        
        agent = create_openai_tools_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(
            agent=agent, 
            tools=tools, 
            verbose=True,
            handle_parsing_errors=True,
        )
        
        return agent_executor
        
    except Exception as e:
        st.error(f"Error creating agent executor: {e}")
        return None
