__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
import os
from handlers.login_handler import check_password
from handlers.state_manager import AppState
from handlers.file_handler import process_zip_files, is_valid_zip_file
from handlers.rag_handler import load_vectorstore_from_directory
from handlers.agent_builder import create_agent_executor
import pandas as pd
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

def main():
    
    # region <--------- Streamlit Page Configuration --------->
    st.set_page_config(
        layout='wide',
        page_title='Conversational Intelligent Insight Agent for Teachers'
    )

    # Do not continue if valid_password is not True.
    if not check_password():
        st.stop()

    # endregion <--------- Streamlit Page Configuration --------->

    # main <--------- Main Page --------->

    # initialise layout
    st.title('Conversational Intelligent Insight Agent for Teachers')
    
    file_col, chat_col = st.columns([0.3,0.7])

    # initialise variables and agent
    app_state = AppState()

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

    greeting = """Hello! I am your friendly Intelligent Insight Agent, here to help you analyse your students' performance on assignments in \
        the Singapore Student Learning Space (SLS).\n\nTo begin, upload assignment Marks .zip files that you have downloaded from SLS in the file uploader on the left. You can upload more than one zip file \
        across multiple classes and assignments. Each zip file should contain exactly one CSV file with the assignment marks.\n\nYou can also ask me about how to apply the EdTech Masterplan or the Key Applications \
        of Technology to improve your students' performance in the assignments.\n\nHowever, note that I may be prone to hallucination. If you are asking about specific assignments, \
        it is preferable that you give me the exact name of the assignments, or ask me for the names of the assignments you have uploaded which you can use in your query. \
            I may also provide you suggestions for improving student performance outside what is suggested in the Key Applications of Technology framework. \
                Be very clear and specific in your query, e.g., whether to include students who have not attempted the assignment in calculating the average score in the assignment.
    """

    current_dataframe = app_state.get_dataframe()
    current_vectorstore = app_state.get_vectorstore()
    current_agent = app_state.get_agent_executor() 

    if current_vectorstore is None:
        app_state.set_vectorstore(load_vectorstore_from_directory())
        current_vectorstore = app_state.get_vectorstore()

    new_df_required = False
    if current_dataframe is not None:
        # dataframe has been loaded
        if current_agent is None:
            # no agent
            new_df_required = True
        else:
            # agent available
            if current_agent.tools[0].dataframe.equals(current_dataframe) == False:
                # the dataframes are not the same
                new_df_required = True

    # new agent required, i.e., this is the first time or dataframe has changed
    if new_df_required:
        if llm:
            new_agent = create_agent_executor(current_dataframe, current_vectorstore)
            if new_agent:
                app_state.set_agent_executor(new_agent)
              
    # initialise first message
    if not app_state.get_initial_message_sent():
        app_state.add_message('assistant', greeting)
        app_state.set_initial_message_sent(True)
    
    with chat_col:
        message_con = st.container(height=500, border=False)
        status_con = st.container()
        chat_con = st.container()

    # print messages in chat_history. at first run, this prints the greeting
    with message_con:
        for message in app_state.get_chat_history():
            with st.chat_message(message['role']):
                st.markdown(message['content'])
    
    with chat_con:
        user_message = st.chat_input('Ask me anything about the assignments you have uploaded!')

    with file_col:
        with st.form('file_upload_form', clear_on_submit=True, border=False):
            file_uploads = st.file_uploader('File Uploader', accept_multiple_files=True, type='zip', key='zips')
            upload_button = st.form_submit_button('Upload files')
        
        st.markdown("""
IMPORTANT NOTICE: This web application is developed as a proof-of-concept prototype. The information provided here is NOT intended for actual usage and should not be relied upon for making any decisions, especially those related to financial, legal, or healthcare matters.

Furthermore, please be aware that the LLM may generate inaccurate or incorrect information. You assume full responsibility for how you use any generated output.

Always consult with qualified professionals for accurate and personalized advice.
                    """)

    # submit button for file upload is clicked
    if upload_button:
        with status_con:
            with st.spinner('Processing...'):
                handle_zip_uploads(app_state, file_uploads)
                st.rerun()

    # user sends message in chat input
    if user_message:
        app_state.add_message('user', user_message)
        st.rerun()

    chat_history = app_state.get_chat_history()
    if chat_history and len(st.session_state.chat_history) > 0:
        last_message = st.session_state.chat_history[-1]
        if last_message['role'] == 'user':
            user_message = last_message['content']
            
            with status_con:
                with st.spinner('Thinking...'):
                    handle_chat_input(app_state, user_message)
                    st.rerun()


def handle_zip_uploads(app_state: AppState, uploaded_files):
    '''Processes newly uploaded .zip files for dataframe'''
    valid_zips = []
    invalid_zips = []
    nl = '''  
    '''
    for uploaded_file in uploaded_files:
        is_valid = is_valid_zip_file(uploaded_file)
        if is_valid:
            app_state.add_uploaded_file_info(uploaded_file.name, uploaded_file.getvalue())
            valid_zips.append(uploaded_file.name)
        else:
            invalid_zips.append(uploaded_file.name)

    if valid_zips:
        file_list = [f'{i+1}. {filename}' for i, filename in enumerate(valid_zips)]
        app_state.add_message('assistant', f"""I've received the following valid Marks .zip files:  
                                {nl.join(file_list)}  """)

    all_uploaded_data_files = [f['name'] for f in app_state.get_uploaded_files_info()]
    if all_uploaded_data_files:
        with st.spinner('Processing files...'):
            dataframe = process_zip_files(app_state.get_uploaded_files_info())
            if dataframe is not None:
                app_state.set_dataframe(dataframe)
                app_state.add_message('assistant', 'The Marks .zip files have been successfully processed! You can now ask me questions about them.')
            else:
                app_state.add_message('assistant', "I'm sorry, I could not process the .zip files properly. Please check the contents of the .zip files.")
    else:
        app_state.add_message('assistant', 'No valid Marks .zip files were uploaded. Please try again with a valid .zip file.')


def handle_chat_input(app_state: AppState, user_query: str):
    
    agent_executor = app_state.get_agent_executor()

    if not agent_executor:
        app_state.add_message('assistant', 'I do not have any information loaded. Please upload Marks .zip file(s) first.')
        return
    
    try:
        response = agent_executor.invoke({'input': user_query})
        final_answer = response.get('output', 'I could not find an answer to your question.')
        app_state.add_message('assistant', final_answer)
    
    except Exception as e:
        error_msg = f'I apologize, but I encountered an error while processing your question: {str(e)}'
        app_state.add_message('assistant', error_msg)


if __name__ == '__main__':
    main()
