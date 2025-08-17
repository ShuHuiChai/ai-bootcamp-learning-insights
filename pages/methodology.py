import streamlit as st

st.set_page_config(
    layout='wide',
    page_title='Conversational Intelligent Insight Agent for Teachers'
)

st.title('Conversational Intelligent Insight Agent for Teachers')
st.header('Methodology and Flow Chart')

st.subheader('Methodology')
methodology = """
The Conversational Intelligent Insight Agent follows a structured methodology to provide insights into student performance, consisting of:
1. **One-off Operation:**

   - An RAG handler is used to load the EdTech Masterplan 2030 and Key Applications of Technology (KAT) framework documents into a vectorstore.

   - The vectorstore is created using the OpenAI embeddings model and the documents are split into semantic chunks for efficient retrieval.

2. **In-App Operation:**

    - The user uploads .zip files containing assignment marks.

    - The .zip files are processed to extract .csv files, which are then loaded into a Pandas DataFrame.

    - The DataFrame is stored in the app state for further analysis.

    - **Agent Executor**: The user can ask natural language queries about the data, which are processed by a Langchain Agent Executor.

    - The Agent Executor uses two tools:

        - **PandasAI tool**: analyses the DataFrame using Langchain's Pandas dataframe agent if the query relates to the assignments uploaded and provides a response.

        - **RAG tool**: retrieves information from the vectorstore about the EdTech Masterplan/KAT framework if the query relates to those areas and provides a response.
        
    - The Agent Executor consolidates responses from either or both tools (if used) and provides the final response to the user's query.
"""
st.markdown(methodology)

st.subheader('Flow Chart')
st.image('assets/methodology_flowchart.png', caption='Flow Chart')


st.subheader('Use Cases')
query1 = """
**Use Case 1:** User asks an irrelevant question: "How old are you?"

Agent is able to respond without invoking the tools: "I don't have an age as I am an artificial intelligence and do not experience time or aging like humans do. I'm here to assist you with your questions and tasks!"
"""
st.markdown(query1)
st.image('assets/use_case_01.png', caption='Response from irrelevant query')

st.divider()

query2 = """
**Use Case 2:** User asks about student performance: "What is the average score of students in the assignment on Volume and Surface Area of Pyramids?"

Agent is able to respond using the Pandas AI tool: "The average score of students in the assignment on "Volume and Surface Area of Pyramids" is approximately **55.76%**."
"""
st.markdown(query2)
st.image('assets/use_case_02.png', caption='Response from query on assignments')

st.divider()

query3 = """
**Use Case 3:** User asks about student performance and how to improve according to the RAT model of technology integration: "How did students perform in the assignment on the Volume and Surface Area of Spheres? How can I improve student performance using the RAT model of technology integration?"
Agent is able to respond using both the Pandas AI tool and RAG tool:
"""
st.markdown(query3)
st.image('assets/use_case_03_a.png')
st.image('assets/use_case_03_b.png', caption='Response from query on assignments and the RAT model of technology integration')
