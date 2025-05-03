from .data_type import Elements
from types import MappingProxyType
import re

class CompositeValidationException(Exception):
    """Custom exception for errors in composite validation."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class CompositeDefinition:
    #E - edge, F - face, T - tris, Q - quads, A - Tetrahedron, P - Pyramid, R - Prism, H - Hexahedron
    #C - composite
    VALID_EXPR: str = r"^[EFTQAPRHC]\[.*?\]$"
    SHAPE_MAP: MappingProxyType[str,Elements] = MappingProxyType({"E" : Elements.EDGE,"F" : Elements.FACE,
                                                                "T" : Elements.TRI,"Q" : Elements.QUAD,
                                                                "A" : Elements.TET,"P" : Elements.PYR,
                                                                "R" : Elements.PRISM,"H" : Elements.HEX,
                                                                "C": Elements.COMPOSITE})

    def __init__(self,definition: str):
        """Contains information about composites

        Args:
            definition (str): Of form E[...]

        Raises:
            CompositeValidationException: _description_
        """
        definition = definition.strip()

        if not re.match(CompositeDefinition.VALID_EXPR,definition):
            raise CompositeValidationException(f"COMPOSITE {definition} is not valid")

        self.element: Elements = CompositeDefinition.SHAPE_MAP.get(definition[0])
        
        try:
            self.composite_ids: set[int] = CompositeDefinition._expand_element_list(definition)
        except ValueError as e:
            raise CompositeValidationException(e)

        self.count: int = len(self.composite_ids)
    
    def __str__(self):
        return f"Composite Definition: element={self.element}, count={self.count}, ids={self.composite_ids}"
    
    def __repr__(self):
        return f"Composite Definition: element={self.element}, count={self.count}, ids={self.composite_ids}"

    def __eq__(self, other):
        if not isinstance(other, CompositeDefinition):
            return False
        return self.element == other.element and self.composite_ids == other.composite_ids

    @staticmethod
    def _expand_element_list(definition: str) -> set[int]:
        """Expands the composite definition into a list of individual elements.

        Args:
            definition (str): Of form E[...]

        Returns:
            list[int]: List of expanded elements
        """
        definition = definition[2:-1]  # Remove "E[" and "]"
        expanded_list = []

        for part in definition.split(','):
            if '-' in part:
                start, end = map(int, part.split('-'))
                expanded_list.extend(range(start, end + 1))  # Expand range
            else:
                expanded_list.append(int(part))  # Single number

        return set(expanded_list)