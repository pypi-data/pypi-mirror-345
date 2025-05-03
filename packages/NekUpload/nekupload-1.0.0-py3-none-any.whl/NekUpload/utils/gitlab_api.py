import requests
from functools import lru_cache

class MissingGitlabCommit(Exception):
    """Exception raised when a commit is missing."""
    pass

def get_single_commit(host_name:str,project_id:str,gitSHA:str) -> requests.Response:
    url = f"{host_name}/api/v4/projects/{project_id}/repository/commits/{gitSHA}"

    response = requests.get(url)

    #success
    if response.status_code == 200:
        return response
    elif response.status_code == 404:
        raise MissingGitlabCommit(f"GitSHA not found in GITLAB repository at {host_name}, project id: {project_id}")

#this can be an expensive function
#getting thousands of items, so lru cache to remove redundant calls
@lru_cache
def get_list_of_commits(host_name:str,project_id:str) -> requests.Response:
    url = f"{host_name}/api/v4/projects/{project_id}/repository/commits"

    response = requests.get(url)

    return response

if __name__ == "__main__":
    host = "https://gitlab.nektar.info"
    nekupload_id = 396
    gitSHA = "0ee9c83e5cf0b907574cf0165977335fcf77a1ac"
    response = get_single_commit(host,nekupload_id,gitSHA)

    print(response.json())