from enum import Enum

#Enums describing various InvenioRDM data types
class RelationsSchemes(Enum):
    DOI = "doi"
    URL = "url"
class RelationType(Enum):
    CONTINUES = "continues"

class ResourceType(Enum):
    DATASET = "dataset"
    PHYSICAL_OBJECT = "physicalobject"
