from __future__ import annotations
from enum import Enum
import re
from typing import Any,Type

class IdentifierType(Enum):
    """Enum denoting persistent identifier types
    """
    ORCID = "orcid"
    GND = "gnd"
    ISNI = "isni"
    ROR = "ror"

class Identifier:
    """Metadata object describing a persistent identifier associated with a person or organisation
    """
    def __init__(self, id: str, id_type: IdentifierType):
        """Class initialiser

        Args:
            id (str): ID
            id_type (IdentifierType): Persitent identifier type

        Raises:
            ValueError: _description_
        """
        self.id_type: IdentifierType = id_type

        if not self._check_valid_id(id,id_type):
            msg =f"ID {id} is not of type {id_type}"
            raise ValueError(msg)

        self.id = id
    
    def __repr__(self) -> str:
        return f"Identifier(id='{self.id}', id_type='{self.id_type.value}')"

    def __str__(self) -> str:
        return self.__repr__()

    def to_json_serialisable(self) -> dict[str, Any]:
        """Method to serialise object as JSON

        Returns:
            dict[str,Any]: JSON serialised object
        """
        return {
            "id": self.id,
            "id_type": self.id_type.value
        }

    @classmethod
    def from_json(cls: Type[Identifier],data: dict[str,Any]) -> 'Identifier':
        """Deserialise json object to reconstruct object

        Args:
            cls (Type[Identifier]): Class
            data (dict[str,Any]): JSON serialised object

        Raises:
            ValueError: _description_

        Returns:
            Identifier: Reconstructed object
        """
        id = data["id"]
        id_type_value = data["id_type"]

        try:
            id_type = IdentifierType(id_type_value)
        except ValueError:
            msg = f"Invalid identifier type: {id_type_value}"
            raise ValueError(msg)

        return cls(id, id_type)  # Create and return the Identifier object
        
    def get_id_type(self) -> IdentifierType:
        """Get the id type

        Returns:
            IdentifierType: Identifier type
        """
        return self.id_type
    
    def get_id(self) -> str:
        """Get the ID

        Returns:
            str: ID
        """
        return self.id
    
    def _check_valid_id(self,id:str,id_type:IdentifierType) -> bool:
        """Check whether stated ID is valid given the ID type

        Args:
            id (str): ID
            id_type (IdentifierType): Identifier type

        Returns:
            bool: Whether id is valid
        """
        validation_methods = {
            IdentifierType.ORCID: self._is_valid_orcid_id,
            IdentifierType.GND: self._is_valid_gnd_id,
            IdentifierType.ISNI: self._is_valid_isni_id,
            IdentifierType.ROR: self._is_valid_ror_id,
        }
        
        validate = validation_methods.get(id_type)
        if validate:
            return validate(id)
        return False

    def _is_valid_orcid_id(self,id: str) -> bool:
        """Checks whether is a valid ORCID identifier

        Args:
            id (str): ID

        Returns:
            bool: Valid
        """
        #orcid id of form xxxx-xxxx-xxxx-xxxx, all numbers, last num (checksum) optionally capital 'X' for 10
        pattern = r'^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$'
        if not re.match(pattern, id):
            return False

        base_digits = id.replace("-", "")[:-1]
        calculated_checksum = self._generate_check_digit_orcid(base_digits)
        return calculated_checksum == id[-1]    
    
    def _is_valid_gnd_id(self,id:str) -> bool:
        """[TODO] Not yet implemented: Checks whether ID is a valid GND ID.

        Args:
            id (str): ID

        Returns:
            bool: Valid
        """
        raise NotImplementedError("GND ID validation not yet implemented")
    
    def _is_valid_isni_id(self, id: str) -> bool:
        """Checks whether the given ID is a valid ISNI.

        ISNI (International Standard Name Identifier) consists of:
        - 16 characters (digits only, except last digit can be 'X' for 10).
        - Follows the ISO 7064 Mod 11,10 checksum validation.

        Args:
            id (str): ID to validate.

        Returns:
            bool: True if valid ISNI, False otherwise.
        """
        # Regex to match 16-digit ISNI, with last character optionally 'X'
        pattern = r'^\d{15}[\dX]$'
        
        if not re.fullmatch(pattern, id):
            return False  # Must match the format

        # Validate checksum
        expected_checksum = self._generate_check_digit_isni(id[:-1])
        return expected_checksum == id[-1]  # Compare computed vs provided checksum

    def _is_valid_ror_id(self,id:str) -> bool:
        """[TODO] Not yet implemented: Checks whether ID is a valid ROR ID.

        Args:
            id (str): ID

        Returns:
            bool: Valid
        """
        raise NotImplementedError("ROR ID validation not yet implemented")

    def _generate_check_digit_orcid(self,base_digits: str) -> str:
        """Generates checksum digit. Checksum code adapted from
        https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier

        Args:
            base_digits (str): Base digits.

        Returns:
            str: Checksum digit
        """
        total = 0
        for digit in base_digits:
            total = (total + int(digit)) * 2

        remainder = total % 11
        result = (12 - remainder) % 11
        return "X" if result == 10 else str(result)
    
    def _generate_check_digit_isni(self, base_digits: str) -> str:
        """
        Generate the ISNI (ISO 7064 Mod 11,10) checksum digit.

        Args:
            base_digits (str): The base 15 digits of the ISNI (excluding the check digit).

        Returns:
            str: The calculated check digit ('0'-'9' or 'X' if 10).
        """
        if len(base_digits) != 15 or not base_digits.isdigit():
            raise ValueError("ISNI base must be exactly 15 digits.")

        total = 0
        weight = 2  # Initial weight

        for digit in base_digits:
            total += int(digit) * weight
            weight += 1
            if weight > 11:
                weight = 2  # Reset after reaching 11

        remainder = total % 11
        check_digit = (12 - remainder) % 11  # (12 - remainder) ensures proper mod 11 behavior

        return "X" if check_digit == 10 else str(check_digit)

    def __eq__(self, other: 'Identifier') -> bool:
        if not isinstance(other,Identifier):
            return False
        
        return (
            self.id_type == other.id_type and
            self.id == other.id
        )