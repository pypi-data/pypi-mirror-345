from typing import Callable
from abc import ABC
from types import MappingProxyType
from .data_type import IntegrationPoint,BasisType,Elements

class ExpansionValidationException(Exception):
    """Custom exception for errors in expansion validation."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

# TODO Note -> See MeshGraph.cpp/DefineBasisKeyFromExpansionTypeHomo
# ReadExpansionInfo etc. for more info in terms of how expansions are handled

class ExpansionDefinition:
    """Class responsible for defining a particular expansion depending on its shape
    """

    @staticmethod
    def _compute_tri_coefficients(num_modes_0: int,num_modes_1: int) -> int:
        """Helper function to compute number of unkown coefficients in a TRI element given the 
        number of modes in each direction.

        Args:
            num_modes_0 (int): Number of modes in direction 0
            num_modes_1 (int): Number of modes in direction 1

        Returns:
            int: Total number of unknown expansion coefficients for the defined TRI element
        """
        #definitions for these can be found in nektar/library/LibUtilities/BasicUtils/ShapeType.hpp
        return num_modes_0 * (num_modes_0 + 1) // 2 + num_modes_0 * (num_modes_1 - num_modes_0)

    @staticmethod
    def _compute_tet_coefficients(num_modes_0: int,num_modes_1: int,num_modes_2: int) -> int:
        """Helper function to compute number of unkown coefficients in a TET element given the 
        number of modes in each direction.

        Args:
            num_modes_0 (int): Number of modes in direction 0
            num_modes_1 (int): Number of modes in direction 1
            num_modes_2 (int): Number of modes in direction 2

        Returns:
            int: Total number of unknown expansion coefficients for the defined TET element
        """
        #definitions for these can be found in nektar/library/LibUtilities/BasicUtils/ShapeType.hpp
        num_coeffs = 0
        for a in range(num_modes_0):
            for b in range(num_modes_1 - a):
                for c in range(num_modes_2-a-b):
                    num_coeffs += 1

        return num_coeffs
    
    @staticmethod
    def _compute_pyr_coefficients(num_modes_0: int,num_modes_1: int,num_modes_2: int) -> int:
        """Helper function to compute number of unkown coefficients in a PYR element given the 
        number of modes in each direction.

        Args:
            num_modes_0 (int): Number of modes in direction 0
            num_modes_1 (int): Number of modes in direction 1
            num_modes_2 (int): Number of modes in direction 2

        Returns:
            int: Total number of unknown expansion coefficients for the defined PYR element
        """
        #definitions for these can be found in nektar/library/LibUtilities/BasicUtils/ShapeType.hpp
        num_coeffs = 0
        for a in range(num_modes_0):
            for b in range(num_modes_1):
                for c in range(num_modes_2-max(a,b)):
                    num_coeffs += 1

        return num_coeffs

    DIMENSIONS: MappingProxyType[Elements,int] = MappingProxyType({
                                        Elements.SEG: 1,
                                        Elements.QUAD: 2,Elements.TRI: 2,
                                        Elements.HEX: 3,Elements.TET: 3,Elements.PYR: 3, Elements.PRISM: 3
                                    })

    #definitions for these can be found in nektar/library/LibUtilities/BasicUtils/ShapeType.hpp
    NUMBER_OF_COEFFICIENTS: MappingProxyType[Elements,Callable[[tuple[int,...]],int]] = MappingProxyType({
                                        Elements.SEG: lambda num_modes: num_modes[0],
                                        Elements.QUAD: lambda num_modes: num_modes[0] * num_modes[1],
                                        Elements.TRI: lambda num_modes: ExpansionDefinition._compute_tri_coefficients(num_modes[0],num_modes[1]),
                                        Elements.HEX: lambda num_modes: num_modes[0]*num_modes[1]*num_modes[2],
                                        Elements.PYR: lambda num_modes: ExpansionDefinition._compute_pyr_coefficients(num_modes[0],num_modes[1],num_modes[2]),
                                        Elements.PRISM: lambda num_modes: num_modes[1] * ExpansionDefinition._compute_tri_coefficients(num_modes[0],num_modes[2]),
                                        Elements.TET: lambda num_modes: ExpansionDefinition._compute_tet_coefficients(num_modes[0],num_modes[1],num_modes[2]),
                                    })

    def __init__(self,
                element: Elements,
                basis_type: tuple[BasisType,...]=None,
                num_modes: tuple[int,...]=None,
                integration_point_type: tuple[IntegrationPoint,...]=None,
                num_points: tuple[int,...]=None,
                fields: tuple[str,...]=None) -> None:
        """Class initialiser

        Args:
            element (Elements): Element type
            basis_type (tuple[BasisType,...], optional): Expansion basis in each principal direction (same size as element dimension). Defaults to None.
            num_modes (tuple[int,...], optional): Number of expansion modes in each principal direction (same size as element dimension). Defaults to None.
            integration_point_type (tuple[IntegrationPoint,...], optional): Integration point type in each principal direction (same size as element dimension). Defaults to None.
            num_points (tuple[int,...], optional): Number of integration points in each principal direction (same size as element dimension). Defaults to None.
            fields (tuple[str,...], optional): Fields associated with this expansion. Defaults to None.
        """

        self.element = element
        self.basis: tuple[BasisType,...] = basis_type
        self.num_points: tuple[int,...] = num_points
        self.integration_point_type: tuple[IntegrationPoint,...] = integration_point_type
        self.num_modes: tuple[int,...] = num_modes
        
        self.fields: tuple[str] = fields
        self.refinements: tuple[int] = None
        #make sure only valid definitions lead to initialisation
        self._validate()

    def add_refinement_ids(self,refinement_ids:list[int]):
        """Add list of refinement ids

        Args:
            refinement_ids (list[int]): _description_
        """
        self.refinements = tuple(refinement_ids)

    def __repr__(self) -> str:
        """String representation of the ExpansionDefinition object.

        Returns:
            str: A string describing the expansion definition.
        """
        return (f"ExpansionDefinition(element={self.element}, "
                f"basis={self.basis}, num_modes={self.num_modes}, "
                f"integration_point_type={self.integration_point_type}, "
                f"num_points={self.num_points}, fields={self.fields})")

    def _validate(self):
        """Check expansion definition is correct. If fails validation, error will be thrown

        Raises:
            ExpansionValidationException: _description_
            ExpansionValidationException: _description_
            ExpansionValidationException: _description_
            ExpansionValidationException: _description_
            ExpansionValidationException: _description_
            ExpansionValidationException: _description_
            ExpansionValidationException: _description_
            ExpansionValidationException: _description_
        """
        expected_dim = ExpansionDefinition.DIMENSIONS[self.element]

        if len(self.num_modes) != expected_dim:
            raise ExpansionValidationException(f"Element {self.element} expects dimension {expected_dim}, modes are: {self.num_modes}")
        if len(self.num_points) != expected_dim:
            raise ExpansionValidationException(f"Element {self.element} expects dimension {expected_dim}, points are: {self.num_points}")
        if len(self.integration_point_type) != expected_dim:
            raise ExpansionValidationException(f"Element {self.element} expects dimension {expected_dim}, point types are: {self.integration_point_type}")
        if len(self.basis) != expected_dim:
            raise ExpansionValidationException(f"Element {self.element} expects dimension {expected_dim}, basis are: {self.basis}")

        #check based on rules in nektar/library/LibUtilies/BasicUtils/ShapeType.hpp 
        if self.element == Elements.TRI and self.num_modes[0] > self.num_modes[1]:
            raise ExpansionValidationException(f"Element {self.element} has invalid mode configuration: num_modes[0] ({self.num_modes[0]}) should not be greater than num_modes[1] ({self.num_modes[1]})")
        if self.element == Elements.TET and (self.num_modes[0] > self.num_modes[2] or self.num_modes[1] > self.num_modes[2]):
            raise ExpansionValidationException(f"Element {self.element} has invalid mode configuration: num_modes[0] ({self.num_modes[0]}) should not be greater than num_modes[1] ({self.num_modes[1]})")
        if self.element == Elements.PYR and (self.num_modes[0] > self.num_modes[2] or self.num_modes[1] > self.num_modes[2]):
            raise ExpansionValidationException(f"Element {self.element} has invalid mode configuration: num_modes[0] ({self.num_modes[0]}) should not be greater than num_modes[1] ({self.num_modes[1]})")
        if self.element == Elements.PRISM and self.num_modes[0] > self.num_modes[2]:
            raise ExpansionValidationException(f"Element {self.element} has invalid mode configuration: num_modes[0] ({self.num_modes[0]}) should not be greater than num_modes[1] ({self.num_modes[1]})")

    def get_num_coefficients(self) -> int:
        """Given the expansion definition, compute number of coefficients to be computed for each
        element of this expansion type.

        Returns:
            _type_: _description_
        """
        num_coeff_callable: Callable[[tuple[int,...]],int] = ExpansionDefinition.NUMBER_OF_COEFFICIENTS[self.element]
        return num_coeff_callable(self.num_modes)

#preferred interface for constructing data
class ExpansionFactory(ABC):
    """Factory interface to define expected default expansion types. In Nektar++ session files, can define expansion with 
    some default construction, e.g. <E COMPOSITE="C[0]" NUMMODES="6" FIELDS="u,v" TYPE="MODIFIED" />. Here "MODIFIED" has 
    a default expansion construction as defined within `nektar/library/SpatialDomains/MeshGraph.cpp 
    <https://gitlab.nektar.info/nektar/nektar/-/blob/master/library/SpatialDomains/MeshGraph.cpp?ref_type=heads>`_.

    Raises:
        ExpansionValidationException: _description_
    """

    #only these four class variables should be overwritten in child classes for different behaviour
    BASIS_MAP: MappingProxyType[Elements,tuple[BasisType,...]]
    INTEGRATION_POINTS_MAP: MappingProxyType[Elements,tuple[IntegrationPoint,...]]
    NUM_MODES_MAP: MappingProxyType[Elements,Callable[[int],tuple[int,...]]]
    NUM_POINTS_MAP: MappingProxyType[Elements,Callable[[int],tuple[int,...]]]

    def __init__(self):
        """Class initialiser
        """
        pass

    def get_expansion(self,element: Elements, nummodes: int,fields: tuple[str,...] | None=None) -> ExpansionDefinition:
        """Get the expansion definition from the factory

        Args:
            element (Elements): Element type to be created. Only shapes are allowed.
            nummodes (int): Number of modes in the expansion
            fields (Optional[tuple[str,...]], optional): Fields in the expansion. Defaults to None.

        Raises:
            ExpansionValidationException: _description_

        Returns:
            ExpansionDefinition: Definition of the expansion
        """

        basis: BasisType | None = self.BASIS_MAP.get(element,None)
        integration_points: IntegrationPoint | None = self.INTEGRATION_POINTS_MAP.get(element,None)
        
        num_modes_callable: Callable[[int],tuple[int,...]] | None = self.NUM_MODES_MAP.get(element,None)
        num_points_callable: Callable[[int],tuple[int,...]] | None = self.NUM_POINTS_MAP.get(element,None)
        
        if basis and integration_points and num_modes_callable and num_points_callable:
            num_modes = num_modes_callable(nummodes)
            num_points = num_points_callable(nummodes)
            return ExpansionDefinition(element,basis,num_modes,integration_points,num_points,fields)
        else:
            raise ExpansionValidationException(f"{self.__class__.__name__} has no default definition for {element}")

#see nektar/library/SpatialDomains/MeshGraph.cpp for default expansions
class ModifiedExpansionFactory(ExpansionFactory):
    """Factory for creating MODIFIED default expansions
    """
    BASIS_MAP: MappingProxyType[Elements,tuple[BasisType,...]] = MappingProxyType({
            Elements.SEG: (BasisType.MODIFIED_A,),
            Elements.TRI: (BasisType.MODIFIED_A, BasisType.MODIFIED_B),
            Elements.QUAD: (BasisType.MODIFIED_A, BasisType.MODIFIED_A),
            Elements.HEX: (BasisType.MODIFIED_A, BasisType.MODIFIED_A, BasisType.MODIFIED_A),
            Elements.PRISM: (BasisType.MODIFIED_A, BasisType.MODIFIED_A, BasisType.MODIFIED_B),
            Elements.PYR: (BasisType.MODIFIED_A, BasisType.MODIFIED_A, BasisType.MODIFIED_PYR_C),
            Elements.TET: (BasisType.MODIFIED_A, BasisType.MODIFIED_B, BasisType.MODIFIED_C),
        })
    
    INTEGRATION_POINTS_MAP: MappingProxyType[Elements,tuple[IntegrationPoint]] = MappingProxyType({
            Elements.SEG: (IntegrationPoint.GAUSS_LOBATTO_LEGENDRE,),
            Elements.QUAD: (IntegrationPoint.GAUSS_LOBATTO_LEGENDRE, IntegrationPoint.GAUSS_LOBATTO_LEGENDRE),
            Elements.TRI: (IntegrationPoint.GAUSS_LOBATTO_LEGENDRE, IntegrationPoint.GAUSS_RADAU_M_ALPHA1_BETA0),
            Elements.HEX: (IntegrationPoint.GAUSS_LOBATTO_LEGENDRE, IntegrationPoint.GAUSS_LOBATTO_LEGENDRE, IntegrationPoint.GAUSS_LOBATTO_LEGENDRE),
            Elements.PRISM: (IntegrationPoint.GAUSS_LOBATTO_LEGENDRE, IntegrationPoint.GAUSS_LOBATTO_LEGENDRE, IntegrationPoint.GAUSS_RADAU_M_ALPHA1_BETA0),
            Elements.PYR: (IntegrationPoint.GAUSS_LOBATTO_LEGENDRE, IntegrationPoint.GAUSS_LOBATTO_LEGENDRE, IntegrationPoint.GAUSS_RADAU_M_ALPHA2_BETA0),
            Elements.TET: (IntegrationPoint.GAUSS_LOBATTO_LEGENDRE, IntegrationPoint.GAUSS_RADAU_M_ALPHA1_BETA0, IntegrationPoint.GAUSS_RADAU_M_ALPHA2_BETA0),
        })
    
    NUM_MODES_MAP: MappingProxyType[Elements,Callable[[int],tuple[int,...]]] = MappingProxyType({
            Elements.SEG: lambda nummodes: (nummodes,),
            Elements.QUAD: lambda nummodes: (nummodes, nummodes),
            Elements.TRI: lambda nummodes: (nummodes, nummodes),
            Elements.HEX: lambda nummodes: (nummodes, nummodes, nummodes),
            Elements.PRISM: lambda nummodes: (nummodes, nummodes, nummodes),
            Elements.PYR: lambda nummodes: (nummodes, nummodes, nummodes),
            Elements.TET: lambda nummodes: (nummodes, nummodes, nummodes),
        })

    NUM_POINTS_MAP: MappingProxyType[Elements,Callable[[int],tuple[int,...]]] = MappingProxyType({
        Elements.SEG: lambda nummodes,quad_offset=1: (nummodes+quad_offset,),
        Elements.QUAD: lambda nummodes,quad_offset=1: (nummodes+quad_offset,nummodes+quad_offset),
        Elements.TRI: lambda nummodes,quad_offset=1: (nummodes+quad_offset, nummodes+quad_offset-1),
        Elements.HEX: lambda nummodes, quad_offset=1: (nummodes+quad_offset, nummodes+quad_offset, nummodes+quad_offset),
        Elements.PRISM: lambda nummodes, quad_offset=1: (nummodes+quad_offset,nummodes+quad_offset,nummodes+quad_offset-1),
        Elements.PYR: lambda nummodes, quad_offset=1: (nummodes+quad_offset,nummodes+quad_offset,nummodes+quad_offset),
        Elements.TET: lambda nummodes, quad_offset=1: (nummodes+quad_offset, nummodes+quad_offset-1, nummodes+quad_offset-1),
    })

class ModifiedQuadPlus1ExpansionFactory(ModifiedExpansionFactory):
    """Factory for creating MODIFIED_QUAD_PLUS_1 default expansions
    """
    NUM_POINTS_MAP: MappingProxyType[Elements,Callable[[int],tuple[int,...]]] = MappingProxyType({
        Elements.SEG: lambda nummodes,quad_offset=2: (nummodes+quad_offset,),
        Elements.QUAD: lambda nummodes,quad_offset=2: (nummodes+quad_offset,nummodes+quad_offset),
        Elements.TRI: lambda nummodes,quad_offset=2: (nummodes+quad_offset, nummodes+quad_offset-1),
        Elements.HEX: lambda nummodes, quad_offset=2: (nummodes+quad_offset, nummodes+quad_offset, nummodes+quad_offset),
        Elements.PRISM: lambda nummodes, quad_offset=2: (nummodes+quad_offset,nummodes+quad_offset,nummodes+quad_offset-1),
        Elements.PYR: lambda nummodes, quad_offset=2: (nummodes+quad_offset,nummodes+quad_offset,nummodes+quad_offset),
        Elements.TET: lambda nummodes, quad_offset=2: (nummodes+quad_offset, nummodes+quad_offset-1, nummodes+quad_offset-1),
    })

class ModifiedQuadPlus2ExpansionFactory(ModifiedExpansionFactory):
    """Factory for creating MODIFIED_QUAD_PLUS_2 default expansions
    """
    NUM_POINTS_MAP: MappingProxyType[Elements,Callable[[int],tuple[int,...]]] = MappingProxyType({
        Elements.SEG: lambda nummodes,quad_offset=3: (nummodes+quad_offset,),
        Elements.QUAD: lambda nummodes,quad_offset=3: (nummodes+quad_offset,nummodes+quad_offset),
        Elements.TRI: lambda nummodes,quad_offset=3: (nummodes+quad_offset, nummodes+quad_offset-1),
        Elements.HEX: lambda nummodes, quad_offset=3: (nummodes+quad_offset, nummodes+quad_offset, nummodes+quad_offset),
        Elements.PRISM: lambda nummodes, quad_offset=3: (nummodes+quad_offset,nummodes+quad_offset,nummodes+quad_offset-1),
        Elements.PYR: lambda nummodes, quad_offset=3: (nummodes+quad_offset,nummodes+quad_offset,nummodes+quad_offset),
        Elements.TET: lambda nummodes, quad_offset=3: (nummodes+quad_offset, nummodes+quad_offset-1, nummodes+quad_offset-1),
    })

class ModifiedGLLRadau10ExpansionFactory(ModifiedExpansionFactory):
    """Factory for creating MODIFIED_GLL_RADAU_10 default expansions
    """
    INTEGRATION_POINTS_MAP: MappingProxyType[Elements,tuple[IntegrationPoint]] = MappingProxyType({
            Elements.SEG: (IntegrationPoint.GAUSS_LOBATTO_LEGENDRE,),
            Elements.QUAD: (IntegrationPoint.GAUSS_LOBATTO_LEGENDRE, IntegrationPoint.GAUSS_LOBATTO_LEGENDRE),
            Elements.TRI: (IntegrationPoint.GAUSS_LOBATTO_LEGENDRE, IntegrationPoint.GAUSS_RADAU_M_ALPHA1_BETA0),
            Elements.HEX: (IntegrationPoint.GAUSS_LOBATTO_LEGENDRE, IntegrationPoint.GAUSS_LOBATTO_LEGENDRE, IntegrationPoint.GAUSS_LOBATTO_LEGENDRE),
            Elements.PRISM: (IntegrationPoint.GAUSS_LOBATTO_LEGENDRE, IntegrationPoint.GAUSS_LOBATTO_LEGENDRE, IntegrationPoint.GAUSS_RADAU_M_ALPHA1_BETA0),
            Elements.PYR: (IntegrationPoint.GAUSS_LOBATTO_LEGENDRE, IntegrationPoint.GAUSS_LOBATTO_LEGENDRE, IntegrationPoint.GAUSS_RADAU_M_ALPHA2_BETA0),
            Elements.TET: (IntegrationPoint.GAUSS_LOBATTO_LEGENDRE, IntegrationPoint.GAUSS_RADAU_M_ALPHA1_BETA0, IntegrationPoint.GAUSS_RADAU_M_ALPHA1_BETA0),
        })

class GLLLagranageExpansionFactory(ExpansionFactory):
    """Factory for creating GLL_LAGRANGE default expansions
    """
    BASIS_MAP: MappingProxyType[Elements,tuple[BasisType,...]] = MappingProxyType({
            Elements.SEG: (BasisType.GLL_LAGRANGE,),
            Elements.QUAD: (BasisType.GLL_LAGRANGE, BasisType.GLL_LAGRANGE),
            Elements.TRI: (BasisType.GLL_LAGRANGE, BasisType.ORTHO_B),
            Elements.HEX: (BasisType.GLL_LAGRANGE, BasisType.GLL_LAGRANGE, BasisType.GLL_LAGRANGE)
        })

    INTEGRATION_POINTS_MAP: MappingProxyType[Elements,tuple[IntegrationPoint]] = MappingProxyType({
            Elements.SEG: (IntegrationPoint.GAUSS_LOBATTO_LEGENDRE,),
            Elements.QUAD: (IntegrationPoint.GAUSS_LOBATTO_LEGENDRE, IntegrationPoint.GAUSS_LOBATTO_LEGENDRE),
            Elements.TRI: (IntegrationPoint.GAUSS_LOBATTO_LEGENDRE, IntegrationPoint.GAUSS_RADAU_M_ALPHA1_BETA0),
            Elements.HEX: (IntegrationPoint.GAUSS_LOBATTO_LEGENDRE, IntegrationPoint.GAUSS_LOBATTO_LEGENDRE, IntegrationPoint.GAUSS_LOBATTO_LEGENDRE)
        })
        
    NUM_MODES_MAP: MappingProxyType[Elements,Callable[[int],tuple[int,...]]] = MappingProxyType({
            Elements.SEG: lambda nummodes: (nummodes,),
            Elements.QUAD: lambda nummodes: (nummodes, nummodes),
            Elements.TRI: lambda nummodes: (nummodes, nummodes),
            Elements.HEX: lambda nummodes: (nummodes, nummodes, nummodes),
        })

    NUM_POINTS_MAP: MappingProxyType[Elements,Callable[[int],tuple[int,...]]] = MappingProxyType({
        Elements.SEG: lambda nummodes,quad_offset=1: (nummodes+quad_offset,),
        Elements.QUAD: lambda nummodes,quad_offset=1: (nummodes+quad_offset,nummodes+quad_offset),
        Elements.TRI: lambda nummodes,quad_offset=1: (nummodes+quad_offset, nummodes+quad_offset-1),
        Elements.HEX: lambda nummodes, quad_offset=1: (nummodes+quad_offset, nummodes+quad_offset, nummodes+quad_offset),
    })
class GLLLagrangeSEMExpansionFactory(GLLLagranageExpansionFactory):
    """Factory for creating GLL_LAGRANGE_SEM default expansions
    """
    NUM_MODES_MAP: MappingProxyType[Elements,Callable[[int],tuple[int,...]]] = MappingProxyType({
        Elements.SEG: lambda nummodes: (nummodes,),
        Elements.QUAD: lambda nummodes: (nummodes, nummodes),
        Elements.HEX: lambda nummodes: (nummodes, nummodes, nummodes),
    })

    NUM_POINTS_MAP: MappingProxyType[Elements,Callable[[int],tuple[int,...]]] = MappingProxyType({
        Elements.SEG: lambda nummodes: (nummodes,),
        Elements.QUAD: lambda nummodes: (nummodes,nummodes),
        Elements.HEX: lambda nummodes: (nummodes, nummodes, nummodes),
    })

class GaussLagrangeExpansionFactory(ExpansionFactory):
    """Factory for creating GAUSS_LAGRANGE default expansions
    """
    BASIS_MAP: MappingProxyType[Elements,tuple[BasisType,...]] = MappingProxyType({
            Elements.SEG: (BasisType.GAUSS_LAGRANGE,),
            Elements.QUAD: (BasisType.GAUSS_LAGRANGE, BasisType.GAUSS_LAGRANGE),
            Elements.HEX: (BasisType.GAUSS_LAGRANGE, BasisType.GAUSS_LAGRANGE, BasisType.GAUSS_LAGRANGE)
        })

    INTEGRATION_POINTS_MAP: MappingProxyType[Elements,tuple[IntegrationPoint]] = MappingProxyType({
            Elements.SEG: (IntegrationPoint.GAUSS_GAUSS_LEGENDRE,),
            Elements.QUAD: (IntegrationPoint.GAUSS_GAUSS_LEGENDRE, IntegrationPoint.GAUSS_GAUSS_LEGENDRE),
            Elements.HEX: (IntegrationPoint.GAUSS_GAUSS_LEGENDRE, IntegrationPoint.GAUSS_GAUSS_LEGENDRE, IntegrationPoint.GAUSS_GAUSS_LEGENDRE)
        })
        
    NUM_MODES_MAP: MappingProxyType[Elements,Callable[[int],tuple[int,...]]] = MappingProxyType({
            Elements.SEG: lambda nummodes: (nummodes,),
            Elements.QUAD: lambda nummodes: (nummodes, nummodes),
            Elements.HEX: lambda nummodes: (nummodes, nummodes, nummodes),
        })

    NUM_POINTS_MAP: MappingProxyType[Elements,Callable[[int],tuple[int,...]]] = MappingProxyType({
        Elements.SEG: lambda nummodes: (nummodes,),
        Elements.QUAD: lambda nummodes: (nummodes,nummodes),
        Elements.HEX: lambda nummodes: (nummodes, nummodes, nummodes),
    })

class OrthogonalExpansionFactory(ExpansionFactory):
    """Factory for creating ORTHOGONAL default expansions
    """
    BASIS_MAP: MappingProxyType[Elements,tuple[BasisType,...]] = MappingProxyType({
            Elements.SEG: (BasisType.ORTHO_A,),
            Elements.QUAD: (BasisType.ORTHO_A, BasisType.ORTHO_A),
            Elements.TRI: (BasisType.ORTHO_A, BasisType.ORTHO_B),
            Elements.TET: (BasisType.ORTHO_A, BasisType.ORTHO_B, BasisType.ORTHO_C)
        })

    INTEGRATION_POINTS_MAP: MappingProxyType[Elements,tuple[IntegrationPoint]] = MappingProxyType({
            Elements.SEG: (IntegrationPoint.GAUSS_LOBATTO_LEGENDRE,),
            Elements.QUAD: (IntegrationPoint.GAUSS_LOBATTO_LEGENDRE, IntegrationPoint.GAUSS_LOBATTO_LEGENDRE),
            Elements.TRI: (IntegrationPoint.GAUSS_LOBATTO_LEGENDRE, IntegrationPoint.GAUSS_RADAU_M_ALPHA1_BETA0),
            Elements.TET: (IntegrationPoint.GAUSS_LOBATTO_LEGENDRE, IntegrationPoint.GAUSS_RADAU_M_ALPHA1_BETA0, IntegrationPoint.GAUSS_RADAU_M_ALPHA2_BETA0)
        })
        
    NUM_MODES_MAP: MappingProxyType[Elements,Callable[[int],tuple[int,...]]] = MappingProxyType({
            Elements.SEG: lambda nummodes: (nummodes,),
            Elements.QUAD: lambda nummodes: (nummodes, nummodes),
            Elements.TRI: lambda nummodes: (nummodes, nummodes),
            Elements.TET: lambda nummodes: (nummodes, nummodes, nummodes),
        })

    NUM_POINTS_MAP: MappingProxyType[Elements,Callable[[int],tuple[int,...]]] = MappingProxyType({
        Elements.SEG: lambda nummodes: (nummodes+1,),
        Elements.QUAD: lambda nummodes: (nummodes+1,nummodes+1),
        Elements.TRI: lambda nummodes: (nummodes+1,nummodes),
        Elements.TET: lambda nummodes: (nummodes+1, nummodes, nummodes),
    })

class FourierExpansionFactory(ExpansionFactory):
    """Factory for creating FOURIER default expansions
    """
    BASIS_MAP: MappingProxyType[Elements,tuple[BasisType,...]] = MappingProxyType({
            Elements.SEG: (BasisType.FOURIER,),
            Elements.QUAD: (BasisType.FOURIER, BasisType.FOURIER),
            Elements.HEX: (BasisType.FOURIER, BasisType.FOURIER, BasisType.FOURIER)
        })

    INTEGRATION_POINTS_MAP: MappingProxyType[Elements,tuple[IntegrationPoint]] = MappingProxyType({
            Elements.SEG: (IntegrationPoint.FOURIER_EVENLY_SPACED,),
            Elements.QUAD: (IntegrationPoint.FOURIER_EVENLY_SPACED, IntegrationPoint.FOURIER_EVENLY_SPACED),
            Elements.HEX: (IntegrationPoint.FOURIER_EVENLY_SPACED, IntegrationPoint.FOURIER_EVENLY_SPACED, IntegrationPoint.FOURIER_EVENLY_SPACED)
        })
        
    NUM_MODES_MAP: MappingProxyType[Elements,Callable[[int],tuple[int,...]]] = MappingProxyType({
            Elements.SEG: lambda nummodes: (nummodes,),
            Elements.QUAD: lambda nummodes: (nummodes, nummodes),
            Elements.HEX: lambda nummodes: (nummodes, nummodes, nummodes),
        })

    NUM_POINTS_MAP: MappingProxyType[Elements,Callable[[int],tuple[int,...]]] = MappingProxyType({
        Elements.SEG: lambda nummodes: (nummodes,),
        Elements.QUAD: lambda nummodes: (nummodes,nummodes),
        Elements.HEX: lambda nummodes: (nummodes, nummodes, nummodes),
    })

class FourierSingleModeExpansionFactory(FourierExpansionFactory):
    """Factory for creating FOURIER_SINGLE_MODE default expansions
    """
    BASIS_MAP: MappingProxyType[Elements,tuple[BasisType,...]] = MappingProxyType({
        Elements.SEG: (BasisType.FOURIER_SINGLE_MODE,),
        Elements.QUAD: (BasisType.FOURIER_SINGLE_MODE, BasisType.FOURIER_SINGLE_MODE),
        Elements.HEX: (BasisType.FOURIER_SINGLE_MODE, BasisType.FOURIER_SINGLE_MODE, BasisType.FOURIER_SINGLE_MODE)
    })

    INTEGRATION_POINTS_MAP: MappingProxyType[Elements,tuple[IntegrationPoint]] = MappingProxyType({
            Elements.SEG: (IntegrationPoint.FOURIER_SINGLE_MODE_SPACED,),
            Elements.QUAD: (IntegrationPoint.FOURIER_SINGLE_MODE_SPACED, IntegrationPoint.FOURIER_SINGLE_MODE_SPACED),
            Elements.HEX: (IntegrationPoint.FOURIER_SINGLE_MODE_SPACED, IntegrationPoint.FOURIER_SINGLE_MODE_SPACED, IntegrationPoint.FOURIER_SINGLE_MODE_SPACED)
        })

class FourierHalfModeReExpansionFactory(FourierSingleModeExpansionFactory):
    """Factory for creating FOURIER_HALF_MODE_RE default expansions
    """
    BASIS_MAP: MappingProxyType[Elements,tuple[BasisType,...]] = MappingProxyType({
        Elements.SEG: (BasisType.FOURIER_HALF_MODE_RE,),
        Elements.QUAD: (BasisType.FOURIER_HALF_MODE_RE, BasisType.FOURIER_HALF_MODE_RE),
        Elements.HEX: (BasisType.FOURIER_HALF_MODE_RE, BasisType.FOURIER_HALF_MODE_RE, BasisType.FOURIER_HALF_MODE_RE)
    })



class FourierHalfModeImExpansionFactory(FourierSingleModeExpansionFactory):
    """Factory for creating FOURIER_HALF_MODE_IM default expansions
    """
    BASIS_MAP: MappingProxyType[Elements,tuple[BasisType,...]] = MappingProxyType({
        Elements.SEG: (BasisType.FOURIER_HALF_MODE_IM,),
        Elements.QUAD: (BasisType.FOURIER_HALF_MODE_IM, BasisType.FOURIER_HALF_MODE_IM),
        Elements.HEX: (BasisType.FOURIER_HALF_MODE_IM, BasisType.FOURIER_HALF_MODE_IM, BasisType.FOURIER_HALF_MODE_IM)
    })

class ChebyshevExpansionFactory(ExpansionFactory):
    """Factory for creating CHEBYSHEV default expansions
    """
    BASIS_MAP: MappingProxyType[Elements,tuple[BasisType,...]] = MappingProxyType({
        Elements.SEG: (BasisType.CHEBYSHEV,),
        Elements.QUAD: (BasisType.CHEBYSHEV, BasisType.CHEBYSHEV),
        Elements.HEX: (BasisType.CHEBYSHEV, BasisType.CHEBYSHEV, BasisType.CHEBYSHEV)
    })

    INTEGRATION_POINTS_MAP: MappingProxyType[Elements,tuple[IntegrationPoint]] = MappingProxyType({
        Elements.SEG: (IntegrationPoint.GAUSS_GAUSS_CHEBYSHEV,),
        Elements.QUAD: (IntegrationPoint.GAUSS_GAUSS_CHEBYSHEV, IntegrationPoint.GAUSS_GAUSS_CHEBYSHEV),
        Elements.HEX: (IntegrationPoint.GAUSS_GAUSS_CHEBYSHEV, IntegrationPoint.GAUSS_GAUSS_CHEBYSHEV, IntegrationPoint.GAUSS_GAUSS_CHEBYSHEV)
    })

    NUM_MODES_MAP: MappingProxyType[Elements,Callable[[int],tuple[int,...]]] = MappingProxyType({
            Elements.SEG: lambda nummodes: (nummodes,),
            Elements.QUAD: lambda nummodes: (nummodes, nummodes),
            Elements.HEX: lambda nummodes: (nummodes, nummodes, nummodes),
        })

    NUM_POINTS_MAP: MappingProxyType[Elements,Callable[[int],tuple[int,...]]] = MappingProxyType({
        Elements.SEG: lambda nummodes: (nummodes,),
        Elements.QUAD: lambda nummodes: (nummodes,nummodes),
        Elements.HEX: lambda nummodes: (nummodes, nummodes, nummodes),
    })

class FourierChebyshevExpansionFactory(ExpansionFactory):
    """Factory for creating FOURIER_CHEBYSHEV default expansions
    """
    BASIS_MAP: MappingProxyType[Elements,tuple[BasisType,...]] = MappingProxyType({
        Elements.QUAD: (BasisType.FOURIER, BasisType.CHEBYSHEV),
    })

    INTEGRATION_POINTS_MAP: MappingProxyType[Elements,tuple[IntegrationPoint]] = MappingProxyType({
        Elements.QUAD: (IntegrationPoint.FOURIER_EVENLY_SPACED, IntegrationPoint.GAUSS_GAUSS_CHEBYSHEV),
    })

    NUM_MODES_MAP: MappingProxyType[Elements,Callable[[int],tuple[int,...]]] = MappingProxyType({
            Elements.QUAD: lambda nummodes: (nummodes, nummodes),
        })

    NUM_POINTS_MAP: MappingProxyType[Elements,Callable[[int],tuple[int,...]]] = MappingProxyType({
        Elements.QUAD: lambda nummodes: (nummodes,nummodes),
    })

class ChebyshevFourierExpansionFactory(FourierChebyshevExpansionFactory):
    """Factory for creating CHEBYSHEV_FOURIER default expansions
    """
    BASIS_MAP: MappingProxyType[Elements,tuple[BasisType,...]] = MappingProxyType({
        Elements.QUAD: (BasisType.CHEBYSHEV, BasisType.FOURIER),
    })

    INTEGRATION_POINTS_MAP: MappingProxyType[Elements,tuple[IntegrationPoint]] = MappingProxyType({
        Elements.QUAD: (IntegrationPoint.GAUSS_GAUSS_CHEBYSHEV, IntegrationPoint.FOURIER_EVENLY_SPACED),
    })

class ModifiedFourierExpansionFactory(ExpansionFactory):
    """Factory for creating MODIFIED_FOURIER default expansions
    """
    BASIS_MAP: MappingProxyType[Elements,tuple[BasisType,...]] = MappingProxyType({
        Elements.QUAD: (BasisType.FOURIER, BasisType.MODIFIED_A),
    })

    INTEGRATION_POINTS_MAP: MappingProxyType[Elements,tuple[IntegrationPoint]] = MappingProxyType({
        Elements.QUAD: (IntegrationPoint.FOURIER_EVENLY_SPACED, IntegrationPoint.GAUSS_LOBATTO_LEGENDRE),
    })

    NUM_MODES_MAP: MappingProxyType[Elements,Callable[[int],tuple[int,...]]] = MappingProxyType({
            Elements.QUAD: lambda nummodes: (nummodes, nummodes),
        })

    NUM_POINTS_MAP: MappingProxyType[Elements,Callable[[int],tuple[int,...]]] = MappingProxyType({
        Elements.QUAD: lambda nummodes: (nummodes,nummodes+1),
    })