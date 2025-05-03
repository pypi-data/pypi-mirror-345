from typing import Callable,Dict,List

class SettingsManager:
    """Manage the change of state of settings across different pages
    """
    def __init__(self,token,database_url,database_name):
        self.token = token
        self.database_url = database_url
        self.database_name = database_name

        self.update_callables: Dict[str,List[Callable]] = {
            "TOKEN": [],
            "HOST_URL": [],
            "HOST_NAME": [],
        }

    def update_api_key(self,token):
        self.token = token

        for callable in self.update_callables["TOKEN"]:
            callable()

    def update_db_url(self,database_target):
        self.database_url = database_target
        for callable in self.update_callables["HOST_URL"]:
            callable()

    def update_host_name(self,database_name):
        self.database_name = database_name
        for callable in self.update_callables["HOST_NAME"]:
            callable()

    def add_callbacks_on_update_token(self,callable: Callable):
        self.update_callables["TOKEN"].append(callable)

    def add_callbacks_on_update_host_url(self,callable: Callable):
        self.update_callables["HOST_URL"].append(callable)

    def add_callbacks_on_update_host_name(self,callable: Callable):
        self.update_callables["HOST_NAME"].append(callable)