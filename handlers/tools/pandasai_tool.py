import streamlit as st
import pandas as pd
from langchain.tools import BaseTool
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI
from typing import Type
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv


class PandasAIToolInput(BaseModel):
    query: str = Field(description="The natural language query to ask about the pandas dataframes, e.g., 'What is the average student score for this assignment?' or 'Show me the top 5 students by total score'.")

class PandasAITool(BaseTool):
    name: str = "data_analyser"
    description: str = "Useful for answering questions about student marks, assignment responses, and any other data loaded into pandas dataframes. Input should be a natural language question about the data."
    args_schema: Type[BaseModel] = PandasAIToolInput

    dataframe:pd.DataFrame
    
    def _run(self, query: str):
        if self.dataframe is None:
            return "Error: No dataframes have been loaded for analysis."
        
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
                api_key=st.secrets['OPENAI'],
            )

        if not llm:
            return "Error: LLM not initialized. Check OPENAI key."

        
        try:
            agent = create_pandas_dataframe_agent(
                llm=llm,
                df=self.dataframe,
                verbose=True,
                agent_type='tool-calling',
                allow_dangerous_code=True,
            )

            context = f"""
            You are analyzing student assignment performance. Your input is a containing six columns:
            
            KEY INFORMATION:
            - 'Attempt Date' indicates when the student attempted the assignment. An empty date value means the student has not attempted the assignment.
            - 'Form Class', 'Index Number', and 'Name' are the students' details.
            - 'Percentage' contains the percentage of the total marks for the assignment that the student achieved.
            - 'Assignment' is the name of the assignment.
            
            Question: {query}
            
            INSTRUCTIONS:
            1. Make sure you analyse and use all the rows in the dataframes in your calculations. Do not use .head(), .sample(), or sample the data. If you only have five rows in your analysis, check and load the ORIGINAL dataframe again.
            2. If you are asked about assignments, you should consider all the rows in the dataframes provided.
            4. If you are asked to compare student's performance across assignments, you should locate ALL students with the same 'Form Class', 'Index Number' and 'Name' in the assignments.
            Present the comparisons in a table format, with each row representing a student and columns for each assignment's percentage.
            5. Use the 'Attempt Date' column to check whether students have attempted the assignment. An empty date value indicates that the student has not attempted the assignment. Do not check for nan values. Check for empty strings.
            6. Think about the instructions again before giving your response. Ensure that you have used all the rows in the given dataframes and do not assume anything.
            7. Format your response in a way that is easy to read and understand. Use markdown for tables and lists where appropriate. Sort the scores in descending order.
            8. Do not use code blocks or code snippets or data types such as dictionaries or json in your response.
            """
            
            response = agent.invoke(context)
            return response['output']

            
            
        except Exception as e:
            return f"Error: {str(e)}"
