from __future__ import annotations
import h5py
import numpy as np
from lxml import etree

from .exceptions import SessionFileException
from NekUpload.NekData.composite import CompositeDefinition
import NekUpload.NekData.expansions as nd_exp
from NekUpload.NekData.data_type import Elements,IntegrationPoint,BasisType
from NekUpload.NekData.filters import NekFilter,NekFilterFactory
from NekUpload.NekData.refinements import Refinements
from NekUpload.utils.notification import warn_with_logging
from NekUpload.utils import parsing,extractor

###############################################################################
# This module contains file abstractions for the expected Nektar files
# Responsible for returning relevant data from their associated files
# This should be used as an internal representation of files
###############################################################################

class NekGeometryFile:
    def __init__(self,geometry_path: str):
        self.geometry_path: str = geometry_path
        self.geometry_file: h5py.File | None = None

    def __enter__(self) -> NekGeometryFile:
        """Opens the files and loads data"""
        self.geometry_file = h5py.File(self.geometry_path,"r")
        return self

    def __exit__(self,exc_type: type=None, exec_value: Exception=None, traceback: object=None):
        """Ensures the file is closed on exit"""
        if self.geometry_file:
            self.geometry_file.close()

    def get_composite_info(self) -> dict[int,CompositeDefinition]:
        """Get dictionary of composite information, mapping composite id to its string definition, as per Nektar++ definition

        Returns:
            dict[int,CompositeDefinition]: COMPOSITE ID -> DEFINITION OF COMPOSITE
        """
        composite_maps: np.ndarray = self.geometry_file["NEKTAR/GEOMETRY/MAPS/COMPOSITE"][:]
        composite_mesh: np.ndarray = self.geometry_file["NEKTAR/GEOMETRY/MESH/COMPOSITE"][:]

        composite_info: dict[int,CompositeDefinition] = {comp_id: CompositeDefinition(definition.decode("utf-8").strip()) 
                                                        for comp_id,definition in zip(composite_maps,composite_mesh)}
    
        return composite_info
    
    def get_composite_edge_info(self) -> dict[int,CompositeDefinition]:
        """Get dictionary of composite information, mapping composite id to its string definition, as per Nektar++ definition.
        Only returns edge information.

        Returns:
            dict[int,CompositeDefinition]: COMPOSITE ID -> DEFINITION OF COMPOSITE (ONLY EDGES)
        """
        composite_info: dict[int,CompositeDefinition] = self.get_composite_info()

        #E[...] is an edge
        edges:dict[int,CompositeDefinition] = {comp_id: definition for comp_id,definition in composite_info.items()
                                if definition.element == Elements.EDGE}
        return edges
    
    def get_composite_face_info(self) -> dict[int,CompositeDefinition]:
        """Get dictionary of composite information, mapping composite id to its string definition, as per Nektar++ definition.
        Only returns face information.

        Returns:
            dict[int,CompositeDefinition]: COMPOSITE ID -> DEFINITION OF COMPOSITE (ONLY FACES)
        """
        composite_info: dict[int,CompositeDefinition] = self.get_composite_info()

        #F[...] is a face
        faces:dict[int,CompositeDefinition] = {comp_id: definition for comp_id,definition in composite_info.items()
                                if definition.element == Elements.FACE}
        return faces

class NekSessionFile:
    def __init__(self,session_path: str):
        self.session_path = session_path
        self.xml_tree: etree._ElementTree | None = None
        self.root_nektar: etree._Element | None = None

    def __enter__(self) -> NekSessionFile:
        self.xml_tree = etree.parse(self.session_path)
        self.root_nektar = self.xml_tree.getroot()
        return self
    
    def __exit__(self,exc_type: type | None, exec_value: Exception | None, traceback: object | None) -> None:
        self.xml_tree = None
        self.root_nektar = None

    def get_all_defined_boundary_regions(self) -> dict[int,CompositeDefinition]:
        """Gets all the defined boundary regions defined in session file. If
        these boundary regions are not defined in boundary conditions, raise an error.
        Otherwise, return a mapping from the session region reference id -> composite definition.

        Raises:
            SessionFileException: Regions are referenced, but no boundary condition is imposed

        Returns:
            dict[int,CompositeDefinition]: REGION REFERENCE ID -> COMPOSITE IDS
        """
        CONDITIONS: etree._Element = self.root_nektar.find("CONDITIONS")
        boundary_regions = CONDITIONS.find("BOUNDARYREGIONS")
        boundary_conditions = CONDITIONS.find("BOUNDARYCONDITIONS")

        #check what boundary regions are defined
        boundary_region_map: dict[int,CompositeDefinition] = {
            int(b.get("ID")): CompositeDefinition(ensure_composite_format(b.text)) 
            for b in boundary_regions.findall("B")
            }
        boundary_region_conditions_defined: set[int] = {int(region.get("REF")) for region in boundary_conditions.findall("REGION")}
        
        #first check that all boundary regions references are defined in boundary conditions
        if not set(boundary_region_map.keys()).issubset(boundary_region_conditions_defined):
            raise SessionFileException(self.session_path,(f"<BOUNDARYREGION> contains references to {sorted(list(boundary_region_map.keys()))} "
                                                    f" but only the following REFS are defined in <BOUNDARYCONDITION>: "
                                                    f"{sorted(list(boundary_region_conditions_defined))}"))
            
        return boundary_region_map
    
    def get_geometry_info(self) -> tuple[int,int,str]:
        """Return all info in the GEOMETRY tag of the session file

        Returns:
            tuple[int,int,str]: Max dimension of elements, max dimension of the space, hdf5 geometry file name to be used
        """
        GEOMETRY: etree._Element = self.root_nektar.find("GEOMETRY")
        elmt_dimension = int(GEOMETRY.get("DIM"))
        space_dimension = int(GEOMETRY.get("SPACE"))
        file = str(GEOMETRY.get("HDF5FILE")).strip()

        return elmt_dimension,space_dimension,file
    
    def get_all_boundary_condition_files(self) -> list[str]:
        """Get all filenames referenced by the BOUNDARYCONDITIONS

        Returns:
            list[str]: List of file names
        """
        CONDITIONS: etree._Element = self.root_nektar.find("CONDITIONS")
        BOUNDARYCONDITIONS: etree._Element = CONDITIONS.find("BOUNDARYCONDITIONS")

        referenced_boundary_condition_files: set[str] = set() #remove repeated references to same file
        all_regions = BOUNDARYCONDITIONS.findall("REGION")
        for region in all_regions:
            definition = region.findall("D") + region.findall("N") + region.findall("R")#only 3 tyeps of BCs, Dirichlet, Neumann, Robin
            for d in definition:
                if filename := d.get("FILE",None):
                    referenced_boundary_condition_files.add(str(filename).strip())

        return list(referenced_boundary_condition_files)

    def get_all_function_files(self) -> list[str]:
        """Get all filenames referenced by all stated CONDITIONS/FUNCTION

        Returns:
            list[str]: List of file names
        """
        CONDITIONS: etree._Element = self.root_nektar.find("CONDITIONS")
        FUNCTIONS: list[etree._Element] = CONDITIONS.findall("FUNCTION")
        
        referenced_function_files: set[str] = set() #can have repeated references to same file
        for function in FUNCTIONS:
            for f in function:
                if filename := f.get("FILE"):
                    referenced_function_files.add(str(filename).strip())

        return list(referenced_function_files)

    def get_parameters(self) -> dict[str,int|float]:
        """Parse and evaluate all <P> param = value </P> found under NEKTAR/CONDITIONS/PARAMETERS

        Returns:
            dict[str,int|float]: Parameter name -> numeric value
        """

        CONDITIONS: etree._Element = self.root_nektar.find("CONDITIONS")
        PARAMETERS: etree._Element = CONDITIONS.find("PARAMETERS")

        raw_params: dict[str,str] = {}
        #of form <P> param = value<P/>
        for p in PARAMETERS.findall("P"):
            lhs,rhs = parsing.get_both_sides_of_equals(p.text)
            raw_params[lhs] = rhs
        
        params: dict[str,int | float] = parsing.evaluate_parameters(raw_params)

        return params
    
    def get_filters(self,filter_type:str=None,exclude_chkpoints:bool=False) -> list[NekFilter]:
        """Get list of available filters from file. Note that currently supports only AEROFORCE and CHECKPOINT and History.
        Ignores all other filters. #TODO Implement all other filters.

        Params:
            filter_type(str): Optional, if only want a specific filter type #TODO could make this an enum
            exclude_chkpoints(bool): If True, excludes checkpoint files from list of filters
        
        Returns:
            list[NekFilter]: List of available filters
        """
        
        FILTERS: etree._Element = self.root_nektar.find("FILTERS")
        #if no filters defined, return empty list
        if FILTERS is None:
            return []

        filter_list: list[NekFilter] = []

        for filter in FILTERS.findall("FILTER"):
            filter_name = filter.get("TYPE").strip()

            #if only want certain type of filter, and not satisfied, skip
            if filter_type and filter_name != filter_type:
                continue

            #exclude checkpoints if bool flag is set
            if exclude_chkpoints and filter_name == "Checkpoint":
                continue

            params: dict[str,str] = {param.get("NAME").strip(): param.text.strip() for param in filter.findall("PARAM")}

            if nek_filter := NekFilterFactory.get_filter(filter_name,params,self.session_path):
                filter_list.append(nek_filter)
        return filter_list

    def get_equation_type(self) -> str:
        CONDITIONS: etree._Element = self.root_nektar.find("CONDITIONS")
        SOLVER_INFO: etree._Element = CONDITIONS.find("SOLVERINFO")

        for I in SOLVER_INFO: 
            if I.get("PROPERTY").strip().lower() == "eqtype":
                return I.get("VALUE")
            
        return None

    def get_refinements(self) -> dict[int,Refinements]:
        REFINEMENTS: etree._Element = self.root_nektar.find("REFINEMENTS")

        if REFINEMENTS is None:
            return {}
        
        ref_id_to_refinement_map: dict[int,Refinements] = {}
        for R in REFINEMENTS.findall("R"):
            ref_id: int = int(R.get("REF"))
            type: str = R.get("TYPE").strip()
            radius: float = float(R.get("RADIUS"))
            coord1:tuple[str,str,str] = R.get("COORDINATE1").split(",")
            coord1: np.ndarray = np.array([float(x) for x in coord1])
            
            if coord2 := R.get("COORDINATE2"):
                coord2:tuple[str,str,str] = coord2.split(",")
                coord2: np.ndarray = np.array([float(x) for x in coord2])

            nummodes = R.get("NUMMODES")
            numpoints = R.get("NUMPOINTS")

            refinement = Refinements(ref_id=ref_id,
                                    type=type,
                                    radius=radius,
                                    coordinate1=coord1,
                                    coordinate2=coord2,
                                    nummodes=nummodes,
                                    numpoints=numpoints)
            
            ref_id_to_refinement_map[ref_id] = refinement
        
        return ref_id_to_refinement_map

    def get_variable_list(self) -> list[str]:
        CONDITIONS: etree._Element = self.root_nektar.find("CONDITIONS")
        VARIABLES: etree._Element = CONDITIONS.find("VARIABLES")

        var_list: list[str] = []
        for V in VARIABLES.findall("V"):
            var_list.append(V.text.strip())

        return var_list

    def is_forcing_defined(self) -> bool:
        """placeholder function for deterining if forcing is defined

        Returns:
            bool: _description_
        """
        FORCING: etree._Element = self.root_nektar.find("FORCING")

        return True if FORCING else False

    def get_expansions(self,geometry_file:str) -> dict[int,list[nd_exp.ExpansionDefinition]]:
        """Get expansion list from expansion definitions. Extracts composite info from geometry file,
        and uses it to generate expansion informaiton.

        Args:
            geometry_file (str): Geometry nekg HDF5 file

        Returns:
            dict[int,list[nd_exp.ExpansionDefinition]]: Mapping of composite ID -> list of expansion definitions with this id
        """

        homogeneous_property: str | None = self.get_homogeneous_property()

        with NekGeometryFile(geometry_file) as f:
            COMPOSITE_INFO_MAP: dict[int,CompositeDefinition] = f.get_composite_info()

        EXPANSIONS: etree._Element = self.root_nektar.find("EXPANSIONS")

        #list as can have case where custom type defines u,v and p with different expansion for same element
        expansion_objs: dict[int,list[nd_exp.ExpansionDefinition]] = {}
        for expansion in EXPANSIONS.findall("E"):
            composite_info: CompositeDefinition = CompositeDefinition(expansion.get("COMPOSITE"))

            for composite_id in composite_info.composite_ids:
                #so previously got C[...] so id is that of composite
                #want to get actual composite element definition Q[...] or T[...] etc
                composite_element: CompositeDefinition = COMPOSITE_INFO_MAP[composite_id]
                shape: Elements = composite_element.element

                #TODO, set default here based on solver type
                fields: tuple[str,...] = tuple(expansion.get("FIELDS",None).split(","))

                if not expansion_objs.get(composite_id,None):
                    expansion_objs[composite_id] = []

                expansion_def: nd_exp.ExpansionDefinition = None
                if expansion.get("TYPE",None):
                    expansion_def = self._get_default_expansions(expansion,shape,fields)
                else:
                    expansion_def = self._get_custom_expansions(expansion,shape,fields)

                if refinement_ids := expansion.get("REFIDS"):
                    refinement_ids: tuple[str,...] = refinement_ids.split(",")
                    refinement_ids: list[int] = [int(ref_id) for ref_id in refinement_ids]
                    expansion_def.add_refinement_ids(refinement_ids)

                expansion_objs[composite_id].append(expansion_def)

        return expansion_objs

    def get_homogeneous_property(self) -> str | None:
        """Get HOMOGENEOUS property. If not specified, return None.

        Returns:
            str | None: _description_
        """
        CONDITIONS = self.root_nektar.find("CONDITIONS")
        SOLVER_INFO = CONDITIONS.find("SOLVERINFO")

        for I in SOLVER_INFO:
            if I.get("PROPERTY") == "HOMOGENEOUS":
                return I.get("VALUE").strip()
        
        return None
    
    def get_homogeneous_modes(self) -> tuple[int,int]:
        """Get number of homogenous modes. If none exist, returns unity.
        Else, returns modes in y direction, and modes in z direction

        Returns:
            tuple[int,int]: _description_
        """
        params = self.get_parameters()
        #try and get modes
        hom_modes_y = int(params.get("HomModesY",1))
        hom_modes_z = int(params.get("HomModesZ",1))

        return hom_modes_y,hom_modes_z

    #allows for lazy loading of factories
    _EXPANSION_INSTANCES = {}

    #make assumption on what it looks like
    BASIS_TYPE = {"Modified_A": BasisType.MODIFIED_A,
                "Modified_B": BasisType.MODIFIED_B,
                "Modified_C": BasisType.MODIFIED_C,
                "Ortho_A": BasisType.ORTHO_A,
                "Ortho_B": BasisType.ORTHO_B,
                "Ortho_C": BasisType.ORTHO_C,
                "Ortho_Pyr_C": BasisType.ORTHO_PYR_C,
                "Modified_Pyr_C": BasisType.MODIFIED_PYR_C,
                "Fourier": BasisType.FOURIER,
                "GLL_Lagrange": BasisType.GLL_LAGRANGE,
                "Gauss_Lagrange": BasisType.GAUSS_LAGRANGE,
                "Legendre": BasisType.LEGENDRE,
                "Chebyshev": BasisType.CHEBYSHEV,
                "Monomial": BasisType.MONONMIAL,
                "Fourier_Single_Mode": BasisType.FOURIER_SINGLE_MODE,
                "Fourier_Half_Mode_Re": BasisType.FOURIER_HALF_MODE_RE,
                "Fourier_Half_Mode_Im": BasisType.FOURIER_HALF_MODE_IM,
    }

    #also make assumptions
    INTEGRATION_POINTS_TYPE = {
        "GaussGaussLegendre": IntegrationPoint.GAUSS_GAUSS_LEGENDRE,
        "GaussRadauMLegendre": IntegrationPoint.GAUSS_RADAU_M_LEGENDRE,
        "GaussRadauPLegendre": IntegrationPoint.GAUSS_RADAU_P_LEGENDRE,
        "GaussLobattoLegendre": IntegrationPoint.GAUSS_LOBATTO_LEGENDRE,
        "GaussGaussChebyshev": IntegrationPoint.GAUSS_GAUSS_CHEBYSHEV,
        "GaussRadauMChebyshev": IntegrationPoint.GAUSS_RADAU_M_CHEBYSHEV,
        "GaussRadauPChebyshev": IntegrationPoint.GAUSS_RADAU_P_CHEBYSHEV,
        "GaussLobattoChebyshev": IntegrationPoint.GAUSS_LOBATTO_CHEBYSHEV,
        "GaussRadauMAlpha0Beta1": IntegrationPoint.GAUSS_RADAU_M_ALPHA0_BETA1,
        "GaussRadauMAlpha0Beta2": IntegrationPoint.GAUSS_RADAU_M_ALPHA0_BETA2,
        "GaussRadauMAlpha1Beta0": IntegrationPoint.GAUSS_RADAU_M_ALPHA1_BETA0,
        "GaussRadauMAlpha2Beta0": IntegrationPoint.GAUSS_RADAU_M_ALPHA2_BETA0,
        "GaussKronrodLegendre": IntegrationPoint.GAUSS_KRONROD_LEGENDRE,
        "GaussRadauKronrodMLegendre": IntegrationPoint.GAUSS_RADAU_KRONROD_M_LEGENDRE,
        "GaussRadauKronrodMAlpha1Beta0": IntegrationPoint.GAUSS_RADAU_KRONROD_M_ALPHA1_BETA0,
        "GaussLobattoKronrodLegendre": IntegrationPoint.GAUSS_LOBATTO_KRONROD_LEGENDRE,
        "PolyEvenlySpaced": IntegrationPoint.POLY_EVENLY_SPACED,
        "FourierEvenlySpaced": IntegrationPoint.FOURIER_EVENLY_SPACED,
        "FourierSingleModeSpaced": IntegrationPoint.FOURIER_SINGLE_MODE_SPACED,
        "BoundaryLayerPoints": IntegrationPoint.BOUNDARY_LAYER_POINTS,
        "BoundaryLayerPointsRev": IntegrationPoint.BOUNDARY_LAYER_POINTS_REV,
        "NodalTriElec": IntegrationPoint.NODAL_TRI_ELEC,
        "NodalTriFekete": IntegrationPoint.NODAL_TRI_FEKETE,
        "NodalTriEvenlySpaced": IntegrationPoint.NODAL_TRI_EVENLY_SPACED,
        "NodalTetEvenlySpaced": IntegrationPoint.NODAL_TET_EVENLY_SPACED,
        "NodalTetElec": IntegrationPoint.NODAL_TET_ELEC,
        "NodalPrismEvenlySpaced": IntegrationPoint.NODAL_PRISM_EVENLY_SPACED,
        "NodalPrismElec": IntegrationPoint.NODAL_PRISM_ELEC,
        "NodalTriSPI": IntegrationPoint.NODAL_TRI_SPI,
        "NodalTetSPI": IntegrationPoint.NODAL_TET_SPI,
        "NodalPrismSPI": IntegrationPoint.NODAL_PRISM_SPI,
        "NodalQuadElec": IntegrationPoint.NODAL_QUAD_ELEC,
        "NodalHexElec": IntegrationPoint.NODAL_HEX_ELEC,
        "SizePointsType": IntegrationPoint.SIZE_POINTS_TYPE,
    }

    @staticmethod
    def _get_expansion_factory(name:str) -> nd_exp.ExpansionFactory:
        """Method to lazily load in expansion factory on demand to reduce overhead.
        Returns the correct expansion factory type. #TODO Check names

        Args:
            name (str): String denoting expansion type, as found in session files

        Returns:
            nd_exp.ExpansionFactory: Expansion Factory
        """
    #making some assumptions here about XML input, can't find docs anywhere
        factories = {
            "MODIFIED": nd_exp.ModifiedExpansionFactory,
            "MODIFIEDQUADPLUS1": nd_exp.ModifiedQuadPlus1ExpansionFactory,
            "MODIFIEDQUADPLUS2": nd_exp.ModifiedQuadPlus2ExpansionFactory,
            "ModifiedGLLRadau10": nd_exp.ModifiedGLLRadau10ExpansionFactory,
            "GLL_LAGRANGE": nd_exp.GLLLagranageExpansionFactory,
            "GAUSS_LAGRANGE": nd_exp.GaussLagrangeExpansionFactory,
            "ORTHOGONAL": nd_exp.OrthogonalExpansionFactory,
            "GLL_LAGRANGE_SEM": nd_exp.GLLLagrangeSEMExpansionFactory,
            "FOURIER": nd_exp.FourierExpansionFactory,
            "FOURIERSINGLEMODE": nd_exp.FourierSingleModeExpansionFactory,
            "FOURIERHALFMODERE": nd_exp.FourierHalfModeReExpansionFactory,
            "FOURIERHALFMODEIM": nd_exp.FourierHalfModeImExpansionFactory,
            "CHEBYSHEV": nd_exp.ChebyshevExpansionFactory,
            "FOURIERCHEBYSHEV": nd_exp.FourierChebyshevExpansionFactory,
            "CHEBYSHEVFOURIER": nd_exp.ChebyshevFourierExpansionFactory,
            "FOURIERMODIFIED": nd_exp.ModifiedFourierExpansionFactory,
        }

        if name in factories:
            instance = factories[name]()
            NekSessionFile._EXPANSION_INSTANCES[name] = instance
            return instance
        else:
            return None

    def _get_default_expansions(self,expansion: etree._Element,shape: Elements,fields: tuple[str,...]=None) -> nd_exp.ExpansionDefinition:
        """Gets default expansion if <E ... TYPE=""/>

        Args:
            expansion (etree._Element): Expansion element
            shape (Elements): Element shape
            fields (tuple[str,...], optional): Fields with this definition. Defaults to None.

        Returns:
            ExpansionDefinition: Expansion definition
        """
        num_modes = int(expansion.get("NUMMODES"))
        type: str = expansion.get("TYPE")

        return self._get_expansion_factory(type).get_expansion(shape,num_modes,fields)

    def _get_custom_expansions(self,expansion: etree._Element,shape: Elements,fields: tuple[str,...]=None) -> nd_exp.ExpansionDefinition:
        """If not using predefined element, and instead <E ... /> with custom definition, construct expansion

        Args:
            expansion (etree._Element): Expansion element
            shape (Elements): Element shape
            fields (tuple[str,...], optional): Fields with this definition. Defaults to None.

        Returns:
            ExpansionDefinition: Expansion definition
        """
        numpoints_str = tuple(item for item in expansion.get("NUMPOINTS").split(","))
        nummodes_str = tuple(expansion.get("NUMMODES", "").split(","))
        basistype_str = tuple(expansion.get("BASISTYPE", "").split(","))
        pointstype_str = tuple(expansion.get("POINTSTYPE", "").split(","))
        
        #convert ot format for ExpansionDefinition
        numpoints = tuple(int(val) for val in numpoints_str if val)
        nummodes = tuple(int(val) for val in nummodes_str if val)
        basistype = tuple(NekSessionFile.BASIS_TYPE[basis] for basis in basistype_str)
        pointstype = tuple(NekSessionFile.INTEGRATION_POINTS_TYPE[point] for point in pointstype_str)

        return nd_exp.ExpansionDefinition(shape,basistype,nummodes,pointstype,numpoints,fields)

    def is_movement(self) -> bool:
        #checks existence of MOVEMENTS
        return self.root_nektar.find("MOVEMENT") is not None

def ensure_composite_format(text: str) -> str:
    """Ensure any [...] are converted to C[...]. This is to accouint for the fact
    that in BOUNDARYREGIONS in session file, both [...] and C[...] and be used to 
    define composite ids

    Args:
        text (str): _description_

    Returns:
        str: _description_
    """
    if text.strip().startswith("[") and text.endswith("]"):
        warn_with_logging(
            "Using `[...]` instead of `C[...]` in session file <BOUNDARYREGIONS> is currently supported but may be deprecated in the future.",
        )
        return f"C{text.strip()}"
    return text

class NekOutputFile:
    def __init__(self,output_path: str):
        self.output_path: str = output_path
        self.output_file: h5py.File | None = None

    def __enter__(self) -> NekOutputFile:
        """Opens the files and loads data"""
        self.output_file = h5py.File(self.output_path,"r")
        return self

    def __exit__(self,exc_type: type=None, exec_value: Exception=None, traceback: object=None):
        """Ensures the file is closed on exit"""
        if self.output_file:
            self.output_file.close()

    def get_gitsha(self) -> str | None:
        return extractor.HDF5Extractor.extract_attribute(self.output_file,"NEKTAR/Metadata/Provenance","GitSHA1")
    
    def get_total_coefficients(self) -> int:
        return int(self.output_file["NEKTAR/DATA"].shape[0]) #should be 1d anyway
    
    def get_decomposition(self) -> list[int]:
        return list(self.output_file["NEKTAR/DECOMPOSITION"][:])