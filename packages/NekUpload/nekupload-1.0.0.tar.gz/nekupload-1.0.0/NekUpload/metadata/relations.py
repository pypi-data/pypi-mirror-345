from types import MappingProxyType
from typing import Any
from .data_types import RelationsSchemes,RelationType,ResourceType

# these are same as defined somewhere in invenio-records in a yaml file???
RELATION_TYPE_TITLE: MappingProxyType[RelationType,dict[str,str]] = MappingProxyType({
    RelationType.CONTINUES: {"en": "Continues"}
})

RESOURCE_TYPE_TITLE: MappingProxyType[ResourceType,dict[str,str]] = MappingProxyType({
    ResourceType.DATASET: {"en": "Dataset"},
    ResourceType.PHYSICAL_OBJECT: {"en": "Physical object"}
})

class Relations:
    """Metadata model for handling the Relations field in InvenioRDM. Describes any links between records with each other and/or external resources
    """
    def __init__(self,
                id: str,
                scheme: RelationsSchemes,
                relation: RelationType,
                resource: ResourceType):
        """Class initialiser

        Args:
            id (str): ID of the resource to be linked
            scheme (RelationsSchemes): ID scheme of the resource to be linked
            relation (RelationType): Describes the relationship of the link
            resource (ResourceType): Describes the resource type of the linked resource
        """
        self.id: str = id
        self.scheme: RelationsSchemes = scheme
        self.relation_type: RelationType = relation
        self.resource_type: ResourceType = resource

    def __eq__(self, other):
        if not isinstance(other, Relations):
            return NotImplemented
        
        return (self.id == other.id and
                self.scheme == other.scheme and
                self.relation_type == other.relation_type and
                self.resource_type == other.resource_type)

    def __repr__(self) -> str:
        """Unambiguous representation of the object (for debugging)."""
        return (f"YourClass(id='{self.id}', "
                f"scheme={self.scheme}, "
                f"relation_type={self.relation_type}, "
                f"resource_type={self.resource_type})")

    def __str__(self) -> str:
        """Readable representation of the object (for users)."""
        return (f"Resource ID: {self.id}, "
                f"Scheme: {self.scheme}, "
                f"Relation: {self.relation_type}, "
                f"Resource Type: {self.resource_type}")

    def to_json(self):
        return {
            "identifier": self.id,
            "scheme": self.scheme.value,
            "relation_type": {
                "id": self.relation_type.value,
                "title": RELATION_TYPE_TITLE[self.relation_type]
            },
            "resource_type": {
                "id": self.resource_type.value,
                "title": RESOURCE_TYPE_TITLE[self.resource_type]
            }
        }
    
    @classmethod
    def from_json(cls,data: dict[str,Any]) -> 'Relations':
        return Relations(data["identifier"],
                        RelationsSchemes(data["scheme"]),
                        RelationType(data["relation_type"]["id"]),
                        ResourceType(data["resource_type"]["id"]))