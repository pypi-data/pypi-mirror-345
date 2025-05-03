from __future__ import annotations
from abc import ABC,abstractmethod
from typing import Any
from .identifier import Identifier,IdentifierType

class InvenioUserInfoFactory:
    def __init__(self):
        pass

    @classmethod
    def create_from_json(cls,json_data: dict[str,Any]) -> InvenioUserInfo:
        """Create suitable object from json. Note that to figure out which object 
        to create, "type" is used as unique identifier

        Args:
            json_data (dict[str,Any]): JSON serialised data

        Raises:
            ValueError: _description_

        Returns:
            InvenioUserInfo: An object of this class or subclass
        """
        #"type" in the JSON is used to identify what class to create
        type_map: dict[str,InvenioUserInfo] = {
            "personal": InvenioPersonInfo,
            "organizational": InvenioOrgInfo
        }

        user_type = json_data.get("type")
        if user_type not in type_map:
            raise ValueError(f"Unknown user info type: {user_type}")

        return type_map[user_type].from_json(json_data)

class InvenioUserInfo(ABC):
    """Base abstract class describing information about a user
    """

    @abstractmethod
    def __init__(self):
        """Class initiliaser
        """
        self.id_schemes: set[IdentifierType] = set()
        self.identifiers: list[Identifier] = []

    def add_identifier(self,identifier: Identifier) -> None:
        """Add a persistent identifier related to the user

        Args:
            identifier (Identifier): Object describing a unique identifier

        Raises:
            ValueError: _description_
        """
        id_type: IdentifierType = identifier.get_id_type()
        
        if id_type in self.id_schemes:
            raise ValueError(f"Cannot have duplicate identifiers of same type for one organisation {id_type}")        

        self.id_schemes.add(id_type)
        self.identifiers.append(identifier)

    @abstractmethod
    def get_info(self) -> dict[str,Any]:
        """Return the json payload package

        Returns:
            Dict[str,Any]: JSON representation of the information, formatted for an API call
        """
        identifier_payload = []
        for identifier in self.identifiers:
            payload = {
                "scheme": identifier.get_id_type().value.lower(),
                "identifier": identifier.get_id()
            }
            identifier_payload.append(payload)

        data = {}
        if identifier_payload:
            data["identifiers"] = identifier_payload

        return data

    @abstractmethod
    def to_json_serialisable(self) -> dict[str,Any]:
        """Return a json serialisable object representing this class

        Returns:
            Dict[str,Any]: JSON serialisable object
        """
        data = {}
        identifiers = [id.to_json_serialisable() for id in self.identifiers]
        if identifiers:
            data["identifiers"] = identifiers

        return data
    
    @classmethod
    @abstractmethod
    def from_json(cls,data: dict[str,Any]) -> InvenioUserInfo:
        """Deserialise json serialisable object to reconstruct an object of this class. Factory method.

        Args:
            data (Dict[str,Any]): JSON serialisable object

        Returns:
            InvenioUserInfo: Object
        """
        pass

    @abstractmethod
    def __eq__(self,other: object) -> bool:
        pass
    
    @abstractmethod
    def __repr__(self) -> bool:
        return (
            f"Identifiers: {self.identifiers}"
            f"Identifier Types: {sorted(self.id_schemes)}"
        )

class InvenioPersonInfo(InvenioUserInfo):
    """Holds information about a person in the format expected from InvenioRDM. Effectively a model for the 
    InvenioRDM Author as a Person field.
    """
    def __init__(self, given_name: str, family_name: str) -> None:
        """Class initialiser

        Args:
            given_name (str): First name
            family_name (str): Last name
        """
        super().__init__()

        self.type: str = "personal"
        self.given_name: str = given_name
        self.family_name: str = family_name

    def get_info(self) -> dict[str,Any]:
        """Return the json payload package, formatted in a way InvenioRDM API expects

        Returns:
            Dict[str,Any]: json payload package, formatted in a way InvenioRDM API expects
        """        
        data = {
            "type": self.type,
            "given_name": self.given_name,
            "family_name": self.family_name,
        }

        return super().get_info() | data
    
    def __str__(self):
        return f"Person: {self.given_name} {self.family_name}"

    def __repr__(self) -> str:
        return (
            f"InvenioPersonInfo(given_name={self.given_name!r}, "
            f"family_name={self.family_name!r})"
        ) + super().__repr__()

    def to_json_serialisable(self) -> dict[str,Any]:
        """Return a json serialisable object representing this class

        Returns:
            Dict[str,Any]: JSON serialisable object
        """
        data = {
            "type": self.type,
            "given_name": self.given_name,
            "family_name": self.family_name,
        }

        return super().to_json_serialisable() | data
    
    @classmethod
    def from_json(cls,data: dict[str,Any]) -> 'InvenioPersonInfo':
        """Deserialise json serialisable object to reconstruct an object of this class.

        Args:
            data (Dict[str,Any]): JSON serialisable object

        Returns:
            InvenioPersonInfo: Reconstructed object
        """
        given_name = data["given_name"]
        family_name = data["family_name"]

        data_identifiers = data.get("identifiers",[])#in case not present in dict
        identifiers: list[Identifier] = [Identifier.from_json(id) for id in data_identifiers]
        
        person = InvenioPersonInfo(given_name,family_name)

        for identifier in identifiers:
            person.add_identifier(identifier)

        return person

    def __eq__(self,other: object) -> bool:
        if not isinstance(other, InvenioPersonInfo):
            return False
        
        return (
            self.type == other.type and
            self.given_name == other.given_name and
            self.family_name == other.family_name and
            self.identifiers == other.identifiers
        )

class InvenioOrgInfo(InvenioUserInfo):
    """Holds information about an organisation in the format expected from InvenioRDM. Effectively a model for the 
    InvenioRDM Author as an Organisation field.
    """
    def __init__(self, name: str) -> None:
        """Class initialiser

        Args:
            name (str): Organisation name
        """
        super().__init__()
        self.type: str = "organizational"
        self.name: str = name

    def get_info(self) -> dict[str,Any]:
        """Return the json payload package, formatted in a way InvenioRDM API expects

        Returns:
            Dict[str,Any]: json payload package, formatted in a way InvenioRDM API expects
        """
        data = {
            "type": self.type,
            "name": self.name,
        }

        return super().get_info() | data

    def __str__(self):
        return f"Organisation: {self.name}"
    
    def to_json_serialisable(self):
        """Return a json serialisable object representing this class

        Returns:
            Dict[str,Any]: JSON serialisable object
        """
        data = {
            "type": self.type,
            "name": self.name,
        }

        return super().to_json_serialisable() | data
    
    @classmethod
    def from_json(cls,data: dict[str,Any]) -> 'InvenioOrgInfo':
        """Deserialise json serialisable object to reconstruct an object of this class.

        Args:
            data (Dict[str,Any]): JSON serialisable object

        Returns:
            InvenioOrgInfo: Reconstructed object
        """
        name = data["name"]

        data_identifiers = data.get("identifiers",[])#in case not present in dict
        identifiers: list[Identifier] = [Identifier.from_json(id) for id in data_identifiers]
        
        org = InvenioOrgInfo(name)

        for identifier in identifiers:
            org.add_identifier(identifier)

        return org
    
    def __eq__(self,other: object) -> bool:
        if not isinstance(other, InvenioOrgInfo):
            return False
        
        return (
            self.type == other.type and
            self.name == other.name and
            self.identifiers == other.identifiers
        )
    
    def __repr__(self) -> str:
        return (
            f"InvenioOrgInfo(name={self.name!r})"
        ) + super().__repr__()