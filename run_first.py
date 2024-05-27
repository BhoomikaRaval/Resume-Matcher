import json
import logging
import os
from scripts import JobDescriptionProcessor, ResumeProcessor
from scripts.utils import get_filenames_from_dir, init_logging_config
import textdistance as td
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain_community.chat_models.openai import ChatOpenAI
import config
import os
from pypdf import PdfReader


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

def match(resume, job_des):
    j = td.jaccard.similarity(resume, job_des)
    s = td.sorensen_dice.similarity(resume, job_des)
    c = td.cosine.similarity(resume, job_des)
    o = td.overlap.normalized_similarity(resume, job_des)
    total = (j + s + c + o ) / 4
    # total = (s+o)/2'''
    return total

def resume_matcher(resume_path,jd_path):    
    logging.info("Started to read from Data/JobDescription")
    try:
        # Check if there are resumes present or not.
        # If present then parse it.
        file_name = get_filenames_from_dir(jd_path)
        print(str(file_name))
        logging.info("Reading from Data/JobDescription is now complete.")
    except:
        # Exit the program if there are no resumes.
        logging.error("There are no job-description present in the specified folder.")
        logging.error("Exiting from the program.")
        logging.error("Please add resumes in the Data/JobDescription folder and try again.")
        exit(1)

    # Now after getting the file_names parse the resumes into a JSON Format.
    logging.info("Started parsing the Job Descriptions.")
    processor = JobDescriptionProcessor(file_name[0])
    job_dict,job_data = processor.process()
        
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
        processor = ResumeProcessor(file)
        resume_dict,resume_data = processor.process()
        resume_keywords, r_entities, r_experience,r_keyterms = resume_dict["extracted_keywords"],resume_dict["entities"],resume_dict["experience"],resume_dict["tri_grams"]
        job_description_keywords,j_entities,j_experience,j_keyterms = job_dict["extracted_keywords"],job_dict["entities"],job_dict["experience"],job_dict["tri_grams"]
        resume_k_string = " ".join(resume_keywords)
        jd_k_string = " ".join(job_description_keywords)
        final_result1 = match(resume_k_string, jd_k_string)
        resume_e_string = " ".join(r_entities)
        jd_e_string = " ".join(j_entities)
        final_result2 = match(resume_e_string, jd_e_string)
        resume_t_string = " ".join(r_keyterms)
        jd_t_string = " ".join(j_keyterms)
        final_result3 = match(resume_t_string, jd_t_string)
        '''resume_exp = " ".join(r_experience)
        jd_exp = " ".join(j_experience)'''
        final_result4 = match(r_experience, j_experience)
        '''for r in final_result:
            print(r.score)
        score = (final_result1+final_result2+final_result3)/3'''
        score = final_result3
        
        print(score,file)
        #response_content = resume_reasoning(llm, resume_data,job_data,score)
        

resume_jd_score = resume_matcher("/Users/bhoomikaraval/Resume_screener/Resume-JD-App/Data/Resumes","/Users/bhoomikaraval/Resume_screener/Resume-JD-App/Data/JobDescription")




