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



import warnings
warnings.simplefilter("ignore", category=UserWarning)


# Load the spaCy English model
nlp = spacy.load("en_core_web_sm")

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
    '''print(response.content)'''
    return response.content

init_logging_config()

# Function to extract text from a PDF file
def extract_text_from_pdf(file_path):
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

def resume_matcher(resume_path,jd_path):    
    logging.info("Started to read from Data/JobDescription")
    # Now after getting the file_names parse the resumes into a JSON Format.
    logging.info("Started parsing the Job Descriptions.")
    '''jd  = extract_text_from_pdf(jd_path)'''
    jd = load_document(jd_path)
    jd_info = nlp(jd[0].page_content)        
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
    for file in file_names:
        resume = load_document(os.path.join(resume_path,file))
        resume_info = nlp(resume[0].page_content) 
        score = jd_info.similarity(resume_info)
        print(file,score)
        response_content = resume_reasoning(llm,resume,jd,score)
    

resume_jd_score = resume_matcher("/Users/bhoomikaraval/Resume_screener/Resume-JD-App/Data/Resumes1/","/Users/bhoomikaraval/Resume_screener/Resume-JD-App/Data/JobDescription/computer_vision_jd.pdf")




