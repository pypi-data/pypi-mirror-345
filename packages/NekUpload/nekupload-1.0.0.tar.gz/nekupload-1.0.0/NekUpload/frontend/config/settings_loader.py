import yaml
import os
from typing import Any

class DatabaseConfig:
    def __init__(self,name:str,url:str=None,communities:list[dict[str,str]]=None):
        self.name = name
        self.url = url or ""
        self.communities = communities or []

    def __repr__(self):
        return f"DatabaseConfig(name={self.name}, url={self.url}, communities={self.communities})"
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, DatabaseConfig):
            return False
        return self.name == other.name and self.url == other.url and self.communities == other.communities

DB_CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'db_targets.yaml') #ensure path always correct

def _load_config(file_path: str=DB_CONFIG_FILE) -> list[DatabaseConfig]:
    """Loads the config file containing database setting information

    Args:
        file_path (str, optional): _description_. Defaults to DB_CONFIG_FILE.

    Returns:
        list[DatabaseConfig]: list of sepcified database configs
    """
    with open(file_path,"r") as file:
        raw_config: dict[str,Any] = yaml.safe_load(file)

    return _generate_database_config_list(raw_config)

def _generate_database_config_list(yaml_content:dict[str,Any]) -> list[DatabaseConfig]:
    """Given a yaml dict, generate the database config. Adds custom defaults in.

    Args:
        yaml_content (dict[str,Any]): _description_

    Returns:
        list[DatabaseConfig]: list of database configurations
    """
    databases = []
    for db in yaml_content.get("databases",[]):
        
        #add a default custom user-defined community
        communities: list[dict[str,str]] = db.get("communities",[])        
        communities.append({"name": "Custom", "community_slug": ""})

        databases.append(DatabaseConfig(
            name=db["name"],
            url=db["url"],
            communities=communities
        ))

    #add a custom url target too
    databases.append(DatabaseConfig(
        name="Custom",
        url="",
        communities = [{"name": "Custom","community_slug": ""}]
    ))

    return databases

#useful values
#only need to calculate these once, then other files can load them in when needed
DB_SETTINGS: list[DatabaseConfig] = _load_config()
DB_NAMES: list[str] = [setting.name for setting in DB_SETTINGS]
DB_NAMES_TO_URL: dict[str,str] = {setting.name: setting.url for setting in DB_SETTINGS}

#this one is DB_NAME -> COMMUNITY_NAME -> COMMUNITY_URL
DB_AVAILABLE_COMMUNITIES: dict[str,dict[str,str]] = {
    setting.name: {
        community.get("name"): community.get("community_slug","") for community in setting.communities
    } for setting in DB_SETTINGS
}
DB_COMMUNITY_NAMES: dict[str,list[str]] = {
    setting.name: [
        community.get("name") for community in setting.communities
    ] for setting in DB_SETTINGS
}