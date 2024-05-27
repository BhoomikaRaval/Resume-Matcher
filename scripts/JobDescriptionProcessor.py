import json
import os.path
import pathlib

from .parsers import ParseJobDesc, ParseResume
from .ReadPdf import read_single_pdf

READ_JOB_DESCRIPTION_FROM = "/Users/bhoomikaraval/Resume_screener/Resume-JD-App/Data/JobDescription/"



class JobDescriptionProcessor:
    def __init__(self, input_file):
        self.input_file = input_file
        self.input_file_name = os.path.join(READ_JOB_DESCRIPTION_FROM + self.input_file)

    def process(self) -> bool:
        try:
            jobDes_dict,job_data = self._read_jd()
            return jobDes_dict,job_data
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return ""

    def _read_jd(self) -> dict:
        data = read_single_pdf(self.input_file_name)
        output = ParseJobDesc(data).get_JSON()
        return output,data

    '''def _write_json_file(self, resume_dictionary: dict):
        file_name = str(
            "JobDescription-"
            + self.input_file
            + resume_dictionary["unique_id"]
            + ".json"
        )
        save_directory_name = pathlib.Path(SAVE_DIRECTORY) / file_name
        json_object = json.dumps(resume_dictionary, sort_keys=True, indent=14)
        with open(save_directory_name, "w+") as outfile:
            outfile.write(json_object)'''
