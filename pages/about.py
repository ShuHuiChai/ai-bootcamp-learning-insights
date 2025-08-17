import streamlit as st

st.set_page_config(
    layout='wide',
    page_title='Conversational Intelligent Insight Agent for Teachers'
)

st.title('Conversational Intelligent Insight Agent for Teachers')
st.header('About Us')

st.subheader('Project Scope')
project_scope = """
While the Singapore Student Learning Space (SLS) serves as MOE's core digital platform for teaching and learning, it currently provides teachers 
only with downloadable zip files containing a CSV file of students' marks for each assignment. This format requires teachers to manually process 
and interpret raw data to identify learning gaps and areas for improvement. However, there is no intuitive or intelligent interface that allows 
teachers to pose natural language questions or receive automated summaries that highlight key patterns and anomalies. This limits their ability to 
make timely, data-driven instructional decisions and tailor their teaching to better meet student needs.
"""
st.markdown(project_scope)

st.subheader('Objectives')
objectives="""
The objectives of the proposed Conversational Intelligent Insight Agent for Teachers are to allow teachers to:
1. Consolidate students' marks across multiple assignments without having to unzip and manually process each downloaded zip file.
2. Post natural language queries on the consolidated data. For example, teachers can ask how the average score of one assignment compares to the average score of another.
3. Combine analysis from student performance with information on the EdTech Masterplan 2030 and the Key Applications of Technology (KAT) framework in order to obtain better
suggestions on how to improve student performance in specific topics that are aligned with the Masterplan and KAT framework.
"""
st.markdown(objectives)

st.subheader('Data Sources')
data_sources="""
The Agent is run on two main data sources:
1. Uploads from the users consisting of marks .zip files downloaded from the Student Learning Space (SLS) assignments page.
2. Documents relating to the EdTech Masterplan 2030 and the Key Applications of Technology framework.
"""
st.markdown(data_sources)

st.subheader('Features')
features = """
The core features of the Agent are:
1. Allow uploading of multiple zip files downloaded from SLS corresponding to multiple assignments from user, and pre-processing and preparing the data for subsequent analysis
2. Implementation of Langchain's Agent Executor equipped with two tools: 
    
   - Pandas AI Tool: using Langchain's pandas dataframe agent to analyse the dataframe containing the ingested data from the uploaded zip files 
  
   - RAG Tool: using Langchain's RAG retriever to get information from pre-prepared vectorstore to provide information on the EdTech Masterplan 2030 and the Key Applications of Technology (KAT) 
framework if requested by user

    The Agent will analyse the query to decide which tool to use to address the user's query. Responses from the tool(s) are then consolidated by the Agent to give the final response to the user's query.
"""
st.markdown(features)
