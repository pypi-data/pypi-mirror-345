import logging
from typing import Any
import requests
from .exceptions import APIError,ClientError,ServerError

"""
This file contains python wrapping of API calls for ease of use. 
Not using class here as each method should be atomic and stateless, much like REST API.
It is not the responsibility of this module to validate input, that is the client's job.
All inputs stated in the documentation should be provided.
Always return a response, so clients have flexibility to choose how they want to process things.
For now, lets not worry about other error codes
"""

###############################################################################
# Useful functions
###############################################################################

def raise_status_error(response: requests.Response):
    """Raises suitable error for different status codes

    Args:
        response (requests.Response): Resposne object

    Raises:
        ClientError: _description_
        ServerError: _description_
        APIError: _description_
    """
    if response.status_code < 500 and response.status_code >= 400:
        err_msg = f"Client error: {response.status_code}"
        raise ClientError(err_msg,response=response)
    elif response.status_code >= 500 and response.status_code < 600:
        err_msg = f"Server error: {response.status_code}"
        raise ServerError(err_msg,response=response)
    else:
        err_msg = f"Unexpected status code: {response.status_code} - {response.text}"
        raise APIError(f"Request Error",response)

###############################################################################
# API Wrappers start here
###############################################################################

def create_draft_record(url: str, 
                        token: str,
                        metadata: dict[str,Any],
                        custom_fields:dict[str,Any] = None,
                        upload_file_enabled: bool=True) -> requests.Response:
    """Create a record draft in an InvenioRDM instance with the specified metadata.

    Args:
        url (str): Base url route to the invenio database
        token (str): Personal access token
        metadata (dict[str,Any], optional): Metadata to be uploaded.
        custom_fields (dict[str,Any], optional): Custom fields for record (InvenioRDM v10 and newer). Defaults to None.
        upload_file_enabled (bool, optional): Denotes whether file upload allowed or not. Defaults to True.

    Raises:
        APIError: If an error occurs during the API call. 

    Returns:
        requests.Response: Returns a request.Response obhject on success (201 status code)
    """

    records_url = url.rstrip("/") + "/api/records"
    
    header = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    #create payload
    payload = {"metadata": metadata, 
            "files": {"enabled": upload_file_enabled}}

    if custom_fields:
        payload["custom_fields"] = custom_fields

    response = requests.post(records_url, headers=header, json=payload)    
    if response.status_code == 201:
        _log_debug_response("Record created succesfully",response)
        return response
    else:
        raise_status_error(response)

def update_draft_record(url: str, 
                        token: str,
                        record_id: str,
                        metadata: dict[str,Any],
                        custom_fields:dict[str,Any] = None,
                        upload_file_enabled: bool=True) -> requests.Response:
    """Update a record draft in InvenioRDM with the specified metadata

    Args:
        url (str): Base url route to the invenio database
        token (str): Personal access token
        metadata (dict[str,Any], optional): Metadata to be uploaded.
        custom_fields (dict[str,Any], optional): Custom fields for record (InvenioRDM v10 and newer). Defaults to None.
        upload_file_enabled (bool, optional): Denotes whether file upload allowed or not. Defaults to True.

    Raises:
        APIError: If an error occurs during the API call. 

    Returns:
        requests.Response: Returns a request.Response obhject on success (200 status code)
    """

    records_url = url.rstrip("/") + f"/api/records/{record_id}/draft"
    
    header = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    #create payload
    payload = {"metadata": metadata,
            "files": {"enabled": upload_file_enabled}}

    if custom_fields:
        payload["custom_fields"] = custom_fields

    response = requests.put(records_url, headers=header, json=payload)
    if response.status_code == 200:
        _log_debug_response("Record updated succesfully",response)
        return response
    else:
        raise_status_error(response)

def create_new_record_version(url:str,token:str,record_id: str) -> requests.Response:
    """Create a new draft record from a published record, thereby creating a new version

    Args:
        url (str): Base url route to the invenio database
        token (str): Personal access token
        record_id (str): Record ID from which new record version will be created

    Raises:
        APIError: If an error occurs during the API call. 

    Returns:
        requests.Response: Returns a request.Response obhject on success (201 status code)
    """
    record_url = url.rstrip("/") + f"/api/records/{record_id}/versions"
    header = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    response = requests.post(record_url,headers=header)
    if response.status_code == 201:
        _log_debug_response("New record version created", response)
        return response
    else:
        raise_status_error(response)

def reserve_doi_draft(url:str,token:str,record_id: str) -> requests.Response:
    """Reserve a DOI for the specified draft record

    Args:
        url (str): Base url route to the invenio database
        token (str): Personal access token
        record_id (str): Record ID for which DOI reservation is for

    Raises:
        APIError: If an error occurs during the API call. 

    Returns:
        requests.Response: Returns a request.Response obhject on success (201 status code)
    """

    api_url = f"{url.rstrip('/')}/api/records/{record_id}/draft/pids/doi"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    response = requests.post(api_url,headers=headers)

    if response.status_code == 201:
        _log_debug_response("Reserved DOI", response)
        return response
    else:
        raise_status_error(response)

def prepare_file_upload(url: str,token: str,record_id: str,file_name_list: list[str]) -> requests.Response:
    """Creates a location in the Invenio database record to store the files. Capable of batch file preparation.

    Args:
        url (str): Base url route to the invenio database
        token (str): Personal access token
        record_id (str): Record ID for which files will be uploaded to
        file_name_list (list[str]): list of names of file to be uploaded

    Returns:
        requests.Response: Response for preparing file upload (201 response code on success)

    Raises:
        APIError: If an error occurs during the API call. 
        ClientError: If an error occurs due to invalid message parameters
    """

    header = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    #convert to JSON array with []
    body = [{"key": file_name} for file_name in file_name_list]
    
    record_url = url.rstrip("/") + f"/api/records/{record_id}/draft/files"

    response = requests.post(record_url,headers=header, json=body)
    if response.status_code == 201:
        _log_debug_response("Files prepared for uploads", response)
        return response
    else:
        raise_status_error(response)

def upload_file(url: str, token: str, record_id: str, file_path: str) -> requests.Response:
    """Upload the specified file to the specified draft record

    Args:
        url (str): Base url route to the invenio database
        token (str): Personal access token
        record_id (str): Record ID for which files will be uploaded to
        file_path (str): Path of file to be uploaded

    Returns:
        requests.Response: Upload response object
    
    Raises:
        APIError: If an error occurs during the API call. 
    """

    #there is an optional size parameter, but we choose to ignore for now
    header = {
        "Content-Type": "application/octet-stream",
        "Authorization": f"Bearer {token}"
    }

    filename = file_path.split('/')[-1]
    file_upload_url = url.rstrip("/") + f"/api/records/{record_id}/draft/files/{filename}/content"

    #open in binary mode, requests behaviour is file is streamed for upload, avoiding memory issues
    with open(file_path, "rb") as f:
        response = requests.put(file_upload_url, headers=header, data=f)
        
        if response.status_code == 200:
            _log_debug_response(f"File {file_path} uploaded successfully", response)
            return response
        else:
            raise_status_error(response)

def commit_file_upload(url: str, token: str, record_id: str, filename: str) -> requests.Response:
    """Save uploaded file in the draft record

    Args:
        url (str): Base url route to the invenio database
        token (str): Personal access token
        record_id (str): Record ID for which files are uploaded to
        filename (str): Name of file to be uploaded

    Returns:
        requests.Response: Commit response object

    Raises:
        APIError: If an error occurs during the API call. 
    """

    header = {"Authorization": f"Bearer {token}"}    
    file_commit_url = url.rstrip("/") + f"/api/records/{record_id}/draft/files/{filename}/commit"

    try:
        response = requests.post(file_commit_url, headers=header)
        response.raise_for_status()
        
        if response.status_code == 200:
            _log_debug_response(f"File {filename} committed successfully",response)
            return response
        else:
            err_msg = f"Unexpected status code: {response.status_code} - {response.text}"
            raise APIError(err_msg,response=response)    
    except requests.exceptions.RequestException as e:
            raise APIError(f"Request Error: {e}")

def publish_draft(url: str, token: str, record_id: str) -> requests.Response:
    """Publish the specified draft on InvenioRDM

    Args:
        url (str): Base url route to the invenio database
        token (str): Personal access token
        record_id (str): Id of record to be published

    Returns:
        requests.Response: Publish response object

    Raises:
        APIError: If an error occurs during the API call. 
        ClientError: If an error occurs due to invalid message parameters
    """
        
    header = {"Authorization": f"Bearer {token}"}
    publish_url = url.rstrip("/") + f"/api/records/{record_id}/draft/actions/publish"

    response = requests.post(publish_url, headers=header)
    response.raise_for_status() #raise exception for bad status codes
    
    if response.status_code == 202:
        _log_debug_response(f"Draft published successfully.",response)
        return response
    else:
        raise_status_error(response)

def delete_draft(url: str, token: str, record_id: str) -> requests.Response:
    """Delete a draft record

    Args:
        url (str): Base url route to the invenio database, of form http:// or https://
        token (str): Personal access token
        record_id(str): Id of record to be prepared for file upload

    Returns:
        requests.Response: Delete response object

    Raises:
        APIError: If an error occurs during the API call. 
    """

    delete_url = url.rstrip("/") + f"/api/records/{record_id}/draft"

    header = {"Authorization": f"Bearer {token}"}

    response = requests.delete(delete_url, headers=header)
    if response.status_code == 204:
        _log_debug_response(f"Draft deleted successfully.",response)
        return response
    else:
        raise_status_error(response)

def get_community(url:str, token: str,community_slug: str) -> requests.Response:
    """Get community specified by the community slug or id

    Args:
        url (str): Base url route to the invenio database
        token (str): Personal access token
        community_slug (str): Community url slug or uuid

    Returns:
        requests.Response: Get community response

    Raises:
        APIError: If an error occurs during the API call. 
    """
    header = {"Authorization": f"Bearer {token}"}

    community_url = url.rstrip("/") + f"/api/communities/{community_slug}"

    response = requests.get(community_url,headers=header)

    if response.status_code == 200:
        _log_debug_response(f"Successfully found community associated with {url}",response)
        return response
    else:
        raise_status_error(response)

def submit_record_to_community(url: str,token: str,community_uuid:str, record_id:str) -> requests.Request:
    """Submit a specified record to a specified community

    Args:
        url (str): Base url route to the invenio database
        token (str): Personal access token
        community_uuid (str): Community UUID
        record_id (str): Id of record to be submitted to community

    Returns:
        requests.Request: Community submission response
    
    Raises:
        APIError: If an error occurs during the API call. 
        ClientError: If an error occurs due to invalid message parameters
    """
    
    community_url = url.rstrip("/") + f"/api/records/{record_id}/draft/review"

    header = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
        }

    body =  {
        "receiver" : {
            "community": f"{community_uuid}"
        },
        "type": "community-submission"
    }

    response = requests.put(community_url,headers=header,json=body)

    if response.status_code == 200:
        _log_debug_response(f"Successfully submitted record {record_id} to community {community_uuid}",response)
        return response
    else:
        raise_status_error(response)

def submit_record_for_review(url: str,token: str,record_id: str,payload: dict[str,str]|None=None) -> requests.Response:
    """Once record is submmitted to community, submit it for review to community admins

    Args:
        url (str): Base url route to the invenio database
        token (str): Personal access token
        record_id (str): Id of record to be submitted for review
        payload(str): Contains content and format
        
    Returns:
        requests.Response: Record review submission response
    
    Raises:
        APIError: If an error occurs during the API call. 
    """    
    submit_review_url = url.strip("/") + f"/api/records/{record_id}/draft/actions/submit-review"

    header = {"Authorization": f"Bearer {token}"}
    body = {"payload": payload} if payload else None

    response = requests.post(submit_review_url,headers=header,json=body)

    if response.status_code == 202:
        _log_debug_response(f"Record submitted to community for review",response)
        return response
    else:
        raise_status_error(response)

def get_draft_record(url: str, token: str, record_id: str) -> requests.Response:
    """Get draft record associated with record_id

    Args:
        url (str): Base url route to the invenio database
        token (str): Personal access token
        record_id (str): Id of desired record
        
    Returns:
        requests.Response: Record review submission response
    
    Raises:
        APIError: If an error occurs during the API call. 
    """
    draft_url = url.rstrip("/") + f"/api/records/{record_id}/draft"

    header = {"Authorization": f"Bearer {token}"}
    

    response = requests.get(draft_url,headers=header)

    if response.status_code == 200:
        _log_debug_response(f"Record {record_id} acquired",response)
        return response
    else:
        raise_status_error(response)

def delete_review_request(url:str,token:str,record_id:str) -> requests.Response:
    """Delete review request for the specified draft

    Args:
        url (str): Base url route to the invenio database
        token (str): Personal access token
        record_id (str): Id of record foe which review request will be deleted
    
    Returns:
        requests.Response: Record review submission response
    
    Raises:
        APIError: If an error occurs during the API call. 
        ClientError: If an error occurs due to invalid message parameters
    """
    review_url = url.rstrip("/") + f"/api/records/{record_id}/draft/review"
    header = {"Authorization": f"Bearer {token}"}

    response = requests.delete(review_url,headers=header)
    if response.status_code == 204:
        _log_debug_response(f"Record {record_id} acquired",response)
        return response
    else:
        raise_status_error(response)

def cancel_review_request(url:str,token:str,request_id:str,payload: dict[str,str]|None=None) -> requests.Response:
    """Cancel a user-submitted review request. Only request's creator can cancel it

    Args:
        url (str): Base url route to the invenio database
        token (str): Personal access token
        record_id (str): Id of record for which review request will be cancelled
        payload(str): Contains content and format

    Returns:
        requests.Response: Record review submission response
    
    Raises:
        APIError: If an error occurs during the API call. 
    """    
    cancel_request = url.rstrip("/") + f"/api/requests/{request_id}/actions/cancel"

    header = {"Authorization": f"Bearer {token}"}
    
    body = {"payload": payload} if payload else {}

    response = requests.post(cancel_request,headers=header,json=body)
    if response.status_code == 200:
        _log_debug_response(f"Request {request_id} cancelled.",response)
        return response
    else:
        raise_status_error(response)
    
def get_record(url:str,token:str,record_id:str) -> requests.Response:
    """Get published record associated with record id

    Args:
        url (str): Base url route to the invenio database
        token (str): Personal access token
        record_id (str): Record ID of desired record
    
    Raises:
        APIError: If API call fails

    Returns:
        requests.Response: _description_
    """
    header = {"Authorization": f"Bearer {token}"}
    get_request = url.rstrip("/") + f"/api/records/{record_id}"

    response = requests.get(get_request,headers=header)
    if response.status_code == 200:
        _log_debug_response(f"Record {record_id} retrieved.",response)
        return response
    else:
        raise_status_error(response)

def _log_debug_response(msg: str, response: requests.Response) -> None:
    """Log a debug statement to logger, with message and response.
    Will take form msg: response. For long responses, they are shortened when logged. 

    Args:
        msg (str): User defined message
        response (requests.Response): Request response 
    """
    try:
        response_data = response.json()
        if isinstance(response_data, dict) and len(response_data) > 10:
            response_data = {k: response_data[k] for k in list(response_data)[:10]}
            response_data['...'] = '...'
        elif isinstance(response_data, list) and len(response_data) > 10:
            response_data = response_data[:10] + ['...']
    except ValueError:
        response_data = response.text[:1000] + '...' if len(response.text) > 1000 else response.text

    logging.debug(f"{msg}: {response_data}")