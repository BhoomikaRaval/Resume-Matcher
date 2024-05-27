import json
import logging
import os
from typing import List
import textdistance as td
import yaml
from qdrant_client import QdrantClient

''''from scripts import utils
from utils.logger import init_logging_config

init_logging_config(basic_log_level=logging.INFO)
# Get the logger
logger = logging.getLogger(__name__)

# Set the logging level
logger.setLevel(logging.INFO)'''


def find_path(folder_name):
    """
    The function `find_path` searches for a folder by name starting from the current directory and
    traversing up the directory tree until the folder is found or the root directory is reached.

    Args:
      folder_name: The `find_path` function you provided is designed to search for a folder by name
    starting from the current working directory and moving up the directory tree until it finds the
    folder or reaches the root directory.

    Returns:
      The `find_path` function is designed to search for a folder with the given `folder_name` starting
    from the current working directory (`os.getcwd()`). It iterates through the directory structure,
    checking if the folder exists in the current directory or any of its parent directories. If the
    folder is found, it returns the full path to that folder using `os.path.join(curr_dir, folder_name)`
    """
    curr_dir = os.getcwd()
    while True:
        if folder_name in os.listdir(curr_dir):
            return os.path.join(curr_dir, folder_name)
        else:
            parent_dir = os.path.dirname(curr_dir)
            if parent_dir == "/":
                break
            curr_dir = parent_dir
    raise ValueError(f"Folder '{folder_name}' not found.")


cwd = find_path("Resume-Matcher")
print(cwd)
READ_RESUME_FROM = os.path.join(cwd, "Data", "Processed", "Resumes")
READ_JOB_DESCRIPTION_FROM = os.path.join(cwd, "Data", "Processed", "JobDescription")
config_path = os.path.join(cwd, "scripts", "similarity")


def read_config(filepath):
    """
    The `read_config` function reads a configuration file in YAML format and handles exceptions related
    to file not found or parsing errors.

    Args:
      filepath: The `filepath` parameter in the `read_config` function is a string that represents the
    path to the configuration file that you want to read and parse. This function attempts to open the
    file specified by `filepath`, load its contents as YAML, and return the parsed configuration. If any
    errors occur during

    Returns:
      The function `read_config` will return the configuration loaded from the file if successful, or
    `None` if there was an error during the process.
    """
    try:
        with open(filepath) as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError as e:
        print(f"Configuration file {filepath} not found: {e}")
    except yaml.YAMLError as e:
        print(
            f"Error parsing YAML in configuration file {filepath}: {e}", exc_info=True
        )
    except Exception as e:
        print(f"Error reading configuration file {filepath}: {e}")
    return None


def read_doc(path):
    """
    The `read_doc` function reads a JSON file from the specified path and returns its contents, handling
    any exceptions that may occur during the process.

    Args:
      path: The `path` parameter in the `read_doc` function is a string that represents the file path to
    the JSON document that you want to read and load. This function reads the JSON data from the file
    located at the specified path.

    Returns:
      The function `read_doc(path)` reads a JSON file located at the specified `path`, and returns the
    data loaded from the file. If there is an error reading the JSON file, it logs the error message and
    returns an empty dictionary `{}`.
    """
    with open(path) as f:
        try:
            data = json.load(f)
        except Exception as e:
            print(f"Error reading JSON file: {e}")
            data = {}
    return data


def match(resume, job_des):
    j = td.jaccard.similarity(resume, job_des)
    s = td.sorensen_dice.similarity(resume, job_des)
    c = td.cosine.similarity(resume, job_des)
    o = td.overlap.normalized_similarity(resume, job_des)
    total = (j + s + c + o) / 4
    # total = (s+o)/2
    return total * 100
    
    


if __name__ == "__main__":
    # To give your custom resume use this code
    resume_dict = read_config(
        READ_RESUME_FROM
        + "/Resume-barry_allen_fe.pdf0df1b6e3-5ce2-488d-808a-d542670f076e.json"
    )
    job_dict = read_config(
        READ_JOB_DESCRIPTION_FROM
        + "/JobDescription-mle_jd_uber.pdf8cb9a0fa-83aa-4956-bf3e-13b218b5dbec.json"
    )
    resume_keywords, r_entities, r_experience = resume_dict["extracted_keywords"],resume_dict["entities"],resume_dict["experience"]
    job_description_keywords,j_entities,j_experience = job_dict["extracted_keywords"],job_dict["entities"],job_dict["experience"]

    resume_k_string = " ".join(resume_keywords)
    print(resume_k_string)
    jd_k_string = " ".join(job_description_keywords)
    final_result1 = match(resume_k_string, jd_k_string)
    resume_e_string = " ".join(r_entities)
    jd_e_string = " ".join(j_entities)
    final_result2 = match(resume_e_string, jd_e_string)
    '''resume_exp = " ".join(r_experience)
    jd_exp = " ".join(j_experience)'''
    final_result3 = match(r_experience, j_experience)
    '''for r in final_result:
        print(r.score)
    print((final_result1+final_result2+final_result3)/3)'''
    print(final_result1,final_result2,final_result3)

