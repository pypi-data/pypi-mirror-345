class HDF5ReaderException(Exception):
    """_summary_

    Args:
        Exception (_type_): _description_
    """
    def __init__(self, message):
        super().__init__(message)

class XMLReaderException(Exception):
    """_summary_

    Args:
        Exception (_type_): _description_
    """
    def __init__(self, message):
        super().__init__(message)