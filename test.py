import csv
import pandas as pd
from pandasai import SmartDataframe
import pandasai as pai
from pandasai_litellm.litellm import LiteLLM
import io
import os
import zipfile
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI


def create_dataframe_agent(dataframe):
    """
    Creates a LangChain pandas agent that can answer questions about the dataframe
    """
    # Initialize the LLM
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=os.getenv("OPENAI"),
    )
    
    # Create the pandas dataframe agent
    agent = create_pandas_dataframe_agent(
        llm=llm,
        df=dataframe,
        verbose=True,
        agent_type=AgentType.OPENAI_FUNCTIONS,
        allow_dangerous_code=True
    )
    
    return agent

def query_dataframe(dataframe, question):
    """
    Query the dataframe with natural language
    """
    try:
        agent = create_dataframe_agent(dataframe)
        
        # Add context about the dataframe structure
        context = f"""
        You are analyzing student assessment data with the following columns:
        {', '.join(dataframe.columns)}
        
        Key information:
        - 'Student Score' contains the points earned by each student
        - 'Marks Per Question' contains the maximum possible points for the question
        - 'Complete/Incomplete' indicates if student attempted the question
        - 'Correct/Incorrect' indicates if student got full marks
        - 'Section' and 'Activity' group questions thematically
        - 'Assignment' indicates which test/homework this was from
        
        Question: {question}
        
        Remember that the total marks for an assignment/section/activity would not be the sum of the entire "Marks Per Question" column as each row in the data consists of each student's
        performance in each question in the assignment/section/activity. To calculate total marks of an assignment/section/activity, you must sum the 'Marks Per Question' column
        for only one student in the assignment/section/activity.

        Please provide a clear, concise answer with relevant data.
        """
        
        response = agent.invoke(context)
        return response['output']
        
    except Exception as e:
        return f"Error: {str(e)}"


def process_zip_files():
    """
    Processes a list of uploaded ZIP file information, extracts the single CSV,
    and returns a dictionary of DataFrames.
    Assumes files have already passed `is_valid_zip_file` checks.
    """
    
    dataframe = pd.DataFrame()
    
    # for file_info in uploaded_files_info:
    #     file_name = file_info['name']
    #     file_content = file_info['content']
    try:
        with zipfile.ZipFile('C:/Users/LENOVO1/Documents/Marks_2E1M Mathematics_11.2 Volume and Surface Area of Cones_20241031 (2)/Marks_2E1M Mathematics_11.1 Volume and Surface Area of Pyramids_20241031.zip', 'r') as zf:
            csv_files = [name for name in zf.namelist() if name.endswith('.csv')]

            with zf.open(csv_files[0]) as csv_file:
                csv_content = csv_file.read().decode('utf-8')
                with io.StringIO(csv_content) as f:
                    csv_df = process_csv_content(f)
                    csv_df['Assignment'] = csv_file.name.replace('.csv', '')
                    dataframe = pd.concat([dataframe, csv_df])
                    dataframe['Attempt Date'] = pd.to_datetime(dataframe['Attempt Date'], errors='coerce')
                    dataframe['Student Score'] = pd.to_numeric(dataframe['Student Score'], errors='coerce')
                    dataframe['Marks Per Question'] = pd.to_numeric(dataframe['Marks Per Question'], errors='coerce')
                    dataframe['Complete/Incomplete'] = dataframe['Complete/Incomplete'].astype(str)
                    dataframe['Correct/Incorrect'] = dataframe['Correct/Incorrect'].astype(str)
                # df_name_prefix = file_name.replace('.zip', '')
                # df_name = f"{df_name_prefix}_{os.path.basename(csv_file_in_zip).replace('.csv', '')}"
                # dataframes[df_name] = pd.read_csv(csv_member)

    except Exception as e:
        # st.error(f"Error processing ZIP file '{file_name}': {e}")
        print(e)
    
    
    return dataframe


def process_csv_content(f):
    """
    Reads the csv content of the file and reorganises it according to the following columns:
    'Attempt Date', 'Form Class', 'Index Number', 'Name', 'Assignment', 'Section', 'Activity', 
    'Question No', 'Marks Per Question', 'Student Score', 'Complete/Incomplete', 'Correct/Incorrect'
    """

    reader = csv.reader(f, delimiter=',', quotechar='"', lineterminator='/n')
    
    section_titles = []
    activity_titles = []
    marks_per_question = []
    for i, row in enumerate(reader):
        
        if i == 0:
            # Skip first row
            continue
        elif i == 1:
            # Second row contains section titles
            section_titles = row
        elif i == 2:
            # Third row contains activity titles
            activity_titles = row
        elif i == 3:
            # Fourth row contains marks per question
            marks_per_question = row
        elif i == 4:
            data_df = pd.DataFrame(columns=row)
        else:
            data_df.loc[i-5] = row
        
    
    marks_df = pd.DataFrame(columns=['Attempt Date', 'Form Class', 'Index Number', 'Name', 'Assignment', 'Section', 'Activity', 
                               'Question No', 'Marks Per Question', 'Student Score', 'Complete/Incomplete', 'Correct/Incorrect'])
    

    for i, column_name in enumerate(data_df.columns):
        if not column_name.startswith('Q'):
            continue
        else:
            # only copy columns that are questions
            section_title = ''
            activity_title = ''
            for j in range(i, 3, -1):
                if section_titles[j] != '':
                    section_title = section_titles[j]
                    break
            if section_title == '':
                section_title = 'Untitled Section'


            for j in range(i, 3, -1):
                if activity_titles[j] != '':
                    activity_title = activity_titles[j]
                    break
            if activity_title == '':
                activity_title = 'Untitled Activity'
            
            q_df = pd.DataFrame()
            
            q_df['Attempt Date'] = data_df['Attempt Date']
            q_df['Form Class'] = data_df['Form Class']
            q_df['Index Number'] = data_df['Index Number']
            q_df['Name'] = data_df['Name']
            q_df['Section'] = section_title
            q_df['Activity'] = activity_title
            q_df['Question No'] = column_name
            q_df['Marks Per Question'] = marks_per_question[i]
            q_df['Student Score'] = data_df.iloc[:, i]
            q_df['Complete/Incomplete'] = q_df.apply(set_complete_incomplete, axis=1)
            q_df['Correct/Incorrect'] = q_df.apply(set_correct_incorrect, axis=1)

            marks_df = pd.concat([marks_df, q_df])
        
    return marks_df


def set_complete_incomplete(row):
    if row['Student Score'] == '':
        return 'Incomplete'
    else:
        return 'Complete'
    

def set_correct_incorrect(row):
    if row['Student Score'] == row['Marks Per Question']:
        return 'Correct'
    else:
        return 'Incorrect'
    

dataframe = process_zip_files()
response = query_dataframe(dataframe, "Which student scored the highest in total? What was their score as a percentage of the total marks for the assignment Volume and Surface Area of Pyramids?")
print(response)