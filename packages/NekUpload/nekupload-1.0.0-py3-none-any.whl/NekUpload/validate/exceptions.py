from typing import List,Any
from lxml import etree

class XMLSchemaException(Exception):
    """Exception raised for errors in the XML schema."""
    
    def __init__(self, file: str, schema_error_log: List[etree._LogEntry],message="Error in the XML schema"):        
        errors = "\n".join(f"Line {error.line}, Col {error.column}: {error.message}" for error in schema_error_log)
        full_message = f"{message} for file {file}\n{errors}" if errors else f"{message} for file {file}\n(No detailed errors found)"
        
        super().__init__(full_message)

class MissingInputFileException(Exception):
    """Exception raised when the input file is missing."""
    
    def __init__(self, file: str, message="Input file is missing"):
        full_message = f"{message}: {file}"
        super().__init__(full_message)

class MissingOutputFileException(Exception):
    """Exception raised when the output file is missing."""
    
    def __init__(self, file: str, message="Output file is missing"):
        full_message = f"{message}: {file}"
        super().__init__(full_message)

class HDF5SchemaException(Exception):
    """Exception raised for errors in the HDF5 schema."""
    
    def __init__(self, file: str, message="HDF5 schema error"):
        full_message = f"{message}: {file}"
        super().__init__(full_message)

class HDF5SchemaExistenceException(HDF5SchemaException):
    """Exception raised for errors in the HDF5 schema."""
    pass

class HDF5SchemaMissingDatasetException(HDF5SchemaException):
    """Exception raised for errors in the HDF5 schema."""
    pass

class HDF5SchemaInconsistentException(HDF5SchemaException):
    """Exception raised for errors in the HDF5 schema."""
    pass

class HDF5SchemaMissingDefinitionException(HDF5SchemaException):
    """Exception raised for errors in the HDF5 schema."""
    pass

class HDF5SchemaExtraDefinitionException(HDF5SchemaException):
    """Exception raised for errors in the HDF5 schema."""
    pass

class GeometryFileException(Exception):
    def __init__(self, file: str, message="Geometry file error"):
        full_message = f"{message}: {file}"
        super().__init__(full_message)

class SessionFileException(Exception):
    def __init__(self, file: str, message="Geometry file error"):
        full_message = f"{message}: {file}"
        super().__init__(full_message)

class OutputFileException(Exception):
    def __init__(self, file: str, message="Geometry file error"):
        full_message = f"{message}: {file}"
        super().__init__(full_message)

class ExperimentalException(Exception):
    """Exception raised for experimental feature errors."""
    
    def __init__(self, feature_name: str, message="Experimental feature error"):
        full_message = f"{message}: {feature_name}"
        super().__init__(full_message)