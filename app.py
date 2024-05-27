import logging
import os
from scripts.utils import get_filenames_from_dir, init_logging_config
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain_community.chat_models.openai import ChatOpenAI
import os
import PyPDF2
import spacy
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    DirectoryLoader,
)
import warnings
warnings.simplefilter("ignore", category=UserWarning)
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/match-resume', methods=['POST'])
def match_resume():
    # Retrieve data from request
    data = request.json
    # Call your resume matching function
    result = resume_matcher(data['resume'], data['job_description'])
    return jsonify({'result': result})


def load_document(file_path):
    name, extension = os.path.splitext(file_path)

    if extension == ".pdf":
        logging.info(f"Loading {file_path}")
        loader = PyPDFLoader(file_path, extract_images=True)
    elif extension == ".docx":
        logging.info(f"Loading {file_path}")
        loader = Docx2txtLoader(file_path)
    elif extension == ".txt":
        logging.info(f"Loading {file_path}")
        loader = TextLoader(file_path)
    else:
        logging.info("Document format is not supported!")
        return None

    docs = loader.load()
    return docs

# Load the spaCy English model
nlp = spacy.load("en_core_web_md")

os.environ["OPENAI_API_KEY"] = ""


llm = ChatOpenAI(
    model_name="gpt-4",
    temperature=0.1,
)


def resume_reasoning(llm,resume,job_des,score):
    requirement = {job_des}
    application = {resume}
    score = {score}

    system_message = SystemMessage(content="""
    You are an expert in talent acquisition. consider this job requirement, application and also similarity score that represents how much the candidate is compatible for given requirement.
    Please generate response that represents how much applicant is compatible based on his/her experience,skills,qualification,and projects for given requirement with decision of rejection and selection.
    Only use the information provided in the initial query. Do not make up any requirements of your own.
    Give your response in 10 to 12 lines and precise and systematic manner. 
    """)

    user_message = HumanMessage(content=f"""
    Generate Reason to accept/reject a given application for available requirement based on the provided similarity score of it.
    {requirement},{application},{score}
  """)    
    response = llm.invoke([system_message, user_message])
    return response.content

init_logging_config()


def resume_matcher(resume_path,jd_path):    
    logging.info("Started to read from Data/JobDescription")
    # Now after getting the file_names parse the resumes into a JSON Format.
    logging.info("Started parsing the Job Descriptions.")
    jd = load_document(jd_path)
    jd_data = jd[0].page_content
    jd_info = nlp(jd_data)        
    logging.info("Parsing of the Job Descriptions is now complete.")
    logging.info("Started to read from Data/Resumes")
    try:
        # Check if there are resumes present or not.
        # If present then parse it.
        file_names = get_filenames_from_dir(resume_path)
        logging.info("Reading from Data/Resumes is now complete.")
    except:
        # Exit the program if there are no resumes.
        logging.error("There are no resumes present in the specified folder.")
        logging.error("Exiting from the program.")
        logging.error("Please add resumes in the Data/Resumes folder and try again.")
        exit(1)

    # Now after getting the file_names parse the resumes into a JSON Format.
    logging.info("Started parsing the resumes.")
    result = []
    for file in file_names:
        resume = load_document(os.path.join(resume_path,file))
        resume_data = resume[0].page_content
        resume_info = nlp(resume_data)
        score = jd_info.similarity(resume_info)
        response_content = resume_reasoning(llm,resume_data,jd_data,score)
        result.append(response_content)
    return result


if __name__ == '__main__':
    app.run(debug=True)







