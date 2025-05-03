from typing import Any
import requests
import logging
import os
from . import invenio_rdm_api as invenioAPI 

# Note that all private functions will return requests.Response for flexibility and testing purposes
# Each member function is responsible for handling that requests.Response and parsing relevant data, stored in class files

#TODO Need to refactor
# 1. Relying on side effects to instantiate class is annoying
# 2. Keep the upload method? and also have builder methods if users want to customise the upload process?
# 3. In which case, need way of returning necessary information?
class InvenioRDM:
    """Responsible for InvenioRDM database upload logic.
    """
    def __init__(self) -> None:
        """Class initialiser
        """
        #instantiated after draft record is created
        self.record_id: str = None

        #community uuid extracted from get_community
        self.community_uuid: str = None

        #acquired after submitting request to community
        self.request_id: str = None

        #acquired after reserving doi during draft creation 
        self.doi: str=None
        self.record_link: str=None
        self.self_link: str=None

    def upload_files(self,url: str, token: str, file_paths: list[str], metadata: dict[str,Any],community_id: str) -> None:  
        """Upload files to an InvenioRDM repository and submit to community for review. Full workflow.

        Args:
            url (str): Base URL to the InvenioRDM repository.  For example: "https://my-invenio-rdm.example.com"            
            token (str): User access token
            file_paths (list[str]): list of paths of files to be uploaded
            metadata (dict[str,Any]): Metadata to be uploaded
            community_id (str): Invenio community id for upload or slug
        """        
        #prevent mixup of files from previous uploads
        self._clear()

        self.create_record(url,token,file_paths,metadata)
        self.submit_to_community(url,token,community_id)

    def create_record(self,url: str, token: str, file_paths: list[str], metadata: dict[str,Any]):
        """Create a draft record with the files

        Args:
            url (str): _description_
            token (str): _description_
            file_paths (List[str]): _description_
            metadata (Dict[str,Any]): _description_
        """
        #create the draft
        create_record_response = invenioAPI.create_draft_record(url,token,metadata)
        self._handle_create_draft_response(create_record_response)
        logging.info(f"Record draft {self.record_id} has been created.")

        #after creation of draft, if any api calls fail, clean up the draft to prevent clutter
        try: 
            #set up the file locations in the record
            file_name_list = [self._get_file_name(file) for file in file_paths]
            invenioAPI.prepare_file_upload(url,token,self.record_id,file_name_list) #does batch
            logging.info(f"Draft {self.record_id} now ready for file uploads.")

            #some test instances don't have doi reservation capabilities
            try:
                doi_response = invenioAPI.reserve_doi_draft(url,token,self.record_id)
                self._handle_doi_response(doi_response)
            except Exception:
                pass

            #upload each file and commit
            for file,filename in zip(file_paths,file_name_list):
                invenioAPI.upload_file(url,token,self.record_id,file)
                invenioAPI.commit_file_upload(url,token,self.record_id,filename)
                logging.info(f"File {file} has been uploaded and committed to record {self.record_id}")

        except Exception as e:
            invenioAPI.delete_draft(url,token,self.record_id)
            logging.info(f"Record draft {self.record_id} has been deleted due to error: {e}")
            raise

    def submit_to_community(self,url:str,token:str,community_id:str):
        """Submit draft record for community review

        Args:
            url (str): _description_
            token (str): _description_
            community_id (str): _description_
        """
        #now try submitting to community, if fails here, ask user to manuallyu submit to community
        try:
            #get community uuid, then submit record to communtiy for review
            community_request = invenioAPI.get_community(url,token,community_id)
            self._handle_community_response(community_request)
            create_review_request_response = invenioAPI.submit_record_to_community(url,token,self.community_uuid,self.record_id)
            self._handle_create_review_request_response(create_review_request_response)

            payload = {
                "content": "This record was submitted via the Nektar++ validation and upload pipeline",
                "format": "html"
            } #this is a comment for the reviewer as to what this record is
            
            invenioAPI.submit_record_for_review(url,token,self.record_id,payload)
            logging.info(f"Record {self.record_id} has been submitted to community {self.community_uuid} for review")
        except Exception as e:
            logging.info(f"Failed to submit to community, please manually attempt on IvenioRDM, due to error: {e}")
            raise

    def _get_community_uuid(self) -> str:
        """Get community UUID

        Returns:
            str: Community UUID
        """
        return self.community_uuid

    def _get_file_name(self,file_path: str) -> str:
        """Given a file path, extract the file name

        Args:
            file_path (str): Path to file

        Returns:
            str: File name
        """
        file_name = os.path.basename(file_path)
        return file_name

    def _handle_create_draft_response(self,response: requests.Response) -> None:
        """Handles response from creation of draft. Reads useful information into class variables

        Args:
            response (requests.Response): Create draft response
        """
        data = response.json()
        self.record_id = data["id"]

    def _handle_community_response(self,response: requests.Response) -> None:
        """Handles get community request response

        Args:
            response (requests.Response): Get Community response
        """
        data = response.json()
        self.community_uuid = data["id"]

    def _handle_doi_response(self,response: requests.Response) -> None:
        """Handles the doi reservation request response

        Args:
            response (requests.Response): DOI reservation request response
        """
        data: dict[str,Any] = response.json()
        
        self.doi = data["pids"]["doi"]["identifier"]
        self.record_link = data["links"]["record_html"]
        self.self_link = data["links"]["self_html"]

    def _handle_create_review_request_response(self,response: requests.Response) -> None:
        """Handles create review request response

        Args:
            response (requests.Response): Create review request response
        """
        data = response.json()
        self.request_id = data["id"]

    def _clear(self) -> None:
        """Reset internal state of the invenioRDM uploader
        """
        self.record_id = None
        self.community_uuid = None
        self.request_id = None
        self.doi = None
        self.record_link = None
        self.self_link = None