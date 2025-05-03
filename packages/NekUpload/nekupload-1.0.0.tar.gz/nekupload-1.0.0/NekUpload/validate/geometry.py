import os
import h5py
from types import MappingProxyType

from .hdf5_definitions import HDF5GroupDefinition,HDF5DatasetDefinition
from .exceptions import GeometryFileException,HDF5SchemaExtraDefinitionException,HDF5SchemaExistenceException
from .exceptions import HDF5SchemaMissingDatasetException,HDF5SchemaInconsistentException,HDF5SchemaMissingDefinitionException
from NekUpload.utils import parsing

class ValidateGeometry:
    """Class responsible for all geometry validation checks
    """
    def __init__(self, file_path: str):
        """Class initialiser

        Args:
            file_path (str): Path to file
        """
        self.file = file_path
        self.file_name = os.path.basename(self.file)

    def check_schema(self) -> bool:
        """Checks whether file conforms to HDF5 geometry schema

        Raises:
            GeometryFileException: _description_

        Returns:
            bool: Passed
        """
        try:
            with h5py.File(self.file, 'r') as f:
                self.schema_checker = GeometrySchemaHDF5Validator(f)
                self.schema_checker.validate()
        except OSError as e:
            raise GeometryFileException(self.file,f"Geometry file either does not exist or is not in HDF5 format {e}")

        return True
    
class GeometrySchemaHDF5Validator:
    """Schema validator for HDF5 geometry .nekg files. Checks whether all valid groups and datasets are there.

    Raises:
        HDF5SchemaExtraDefinitionException: _description_
        HDF5SchemaExtraDefinitionException: _description_
        HDF5SchemaMissingDatasetException: _description_
        HDF5SchemaInconsistentException: _description_
        HDF5SchemaMissingDefinitionException: _description_
        HDF5SchemaMissingDefinitionException: _description_
        HDF5SchemaMissingDefinitionException: _description_
        HDF5SchemaMissingDefinitionException: _description_
    """

    NO_DIM_CONSTRAINTS = -1 #helper

    #using immutable dictionary to define what structure of each group and dataset should look like regardless of geometry file
    #dict to help associate each set with a useful descriptor, which will be beneficial later on
    BASE_GROUPS: MappingProxyType[str,HDF5GroupDefinition] = MappingProxyType({"NEKTAR": HDF5GroupDefinition("NEKTAR"),
                                            "GEOMETRY": HDF5GroupDefinition("NEKTAR/GEOMETRY",attributes=["FORMAT_VERSION"]),
                                            "MAPS": HDF5GroupDefinition("NEKTAR/GEOMETRY/MAPS"),
                                            "MESH": HDF5GroupDefinition("NEKTAR/GEOMETRY/MESH")})

    DATASETS_MANDATORY_MAPS: MappingProxyType[str,HDF5DatasetDefinition] = MappingProxyType(
                                                            {"VERT": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MAPS/VERT",(NO_DIM_CONSTRAINTS,)),
                                                            "DOMAIN": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MAPS/DOMAIN",(NO_DIM_CONSTRAINTS,)),
                                                            "COMPOSITE": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MAPS/COMPOSITE",(NO_DIM_CONSTRAINTS,))
                                                            })

    DATASETS_MANDATORY_MESH: MappingProxyType[str,HDF5DatasetDefinition] = MappingProxyType(
                                                                {"CURVE_NODES": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MESH/CURVE_NODES",(NO_DIM_CONSTRAINTS,3)),
                                                                "VERT": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MESH/VERT",(NO_DIM_CONSTRAINTS,3)),
                                                                "DOMAIN": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MESH/DOMAIN",(NO_DIM_CONSTRAINTS,)),
                                                                "COMPOSITE": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MESH/COMPOSITE",(NO_DIM_CONSTRAINTS,))
                                                                })
    
    DATASETS_1D_MAPS: MappingProxyType[str,HDF5DatasetDefinition] = MappingProxyType(
                                                        {"SEG": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MAPS/SEG",(NO_DIM_CONSTRAINTS,)),
                                                        "CURVE_EDGE": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MAPS/CURVE_EDGE",(NO_DIM_CONSTRAINTS,))
                                                        })
    
    DATASETS_1D_MESH: MappingProxyType[str,HDF5DatasetDefinition] = MappingProxyType(
                                                        {"SEG": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MESH/SEG",(NO_DIM_CONSTRAINTS,2)),
                                                        "CURVE_EDGE": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MESH/CURVE_EDGE",(NO_DIM_CONSTRAINTS,3))
                                                        })

    DATASETS_2D_MAPS: MappingProxyType[str,HDF5DatasetDefinition] = MappingProxyType(
                                                        {"TRI": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MAPS/TRI",(NO_DIM_CONSTRAINTS,)),
                                                        "QUAD": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MAPS/QUAD",(NO_DIM_CONSTRAINTS,)),
                                                        "CURVE_FACE": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MAPS/CURVE_FACE",(NO_DIM_CONSTRAINTS,))
                                                        })
    
    DATASETS_2D_MESH: MappingProxyType[str,HDF5DatasetDefinition] = MappingProxyType(
                                                        {"TRI": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MESH/TRI",(NO_DIM_CONSTRAINTS,3)),
                                                        "QUAD": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MESH/QUAD",(NO_DIM_CONSTRAINTS,4)),
                                                        "CURVE_FACE": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MESH/CURVE_FACE",(NO_DIM_CONSTRAINTS,3))
                                                        })

    DATASETS_3D_MAPS: MappingProxyType[str,HDF5DatasetDefinition] = MappingProxyType(
                                                        {"HEX": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MAPS/HEX",(NO_DIM_CONSTRAINTS,)),
                                                        "TET": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MAPS/TET",(NO_DIM_CONSTRAINTS,)),
                                                        "PYR": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MAPS/PYR",(NO_DIM_CONSTRAINTS,)),
                                                        "PRISM": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MAPS/PRISM",(NO_DIM_CONSTRAINTS,))
                                                        })

    DATASETS_3D_MESH: MappingProxyType[str,HDF5DatasetDefinition] = MappingProxyType(
                                                        {"HEX": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MESH/HEX",(NO_DIM_CONSTRAINTS,6)),
                                                        "TET": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MESH/TET",(NO_DIM_CONSTRAINTS,4)),
                                                        "PYR": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MESH/PYR",(NO_DIM_CONSTRAINTS,5)),
                                                        "PRISM": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MESH/PRISM",(NO_DIM_CONSTRAINTS,5))
                                                        })
    
    DATASETS_MAPS: MappingProxyType[str,HDF5DatasetDefinition] = MappingProxyType({**DATASETS_MANDATORY_MAPS,**DATASETS_1D_MAPS,
                                                                                   **DATASETS_2D_MAPS,**DATASETS_3D_MAPS})

    DATASETS_MESH: MappingProxyType[str,HDF5DatasetDefinition] = MappingProxyType({**DATASETS_MANDATORY_MESH,**DATASETS_1D_MESH,
                                                                                   **DATASETS_2D_MESH,**DATASETS_3D_MESH})

    def __init__(self,f: h5py.File):   
        """Class initialiser

        Args:
            f (h5py.File): Opened HDF5 file
        """
        self.file: h5py.File = f

        self.datasets_present: set[str] = set()
        self.element_number: dict[str] = {}
        
    def validate(self) -> bool:
        """Check whether the provided file conforms to the geometry HDF5 schema

        Returns:
            bool: Valid
        """
        #check mandatory groups
        for group in GeometrySchemaHDF5Validator.BASE_GROUPS.values():
            group.validate(self.file)
        
        #check all datasets
        self.datasets_present.update(self._check_mandatory_dataset(GeometrySchemaHDF5Validator.DATASETS_MANDATORY_MAPS))
        self.datasets_present.update(self._check_mandatory_dataset(GeometrySchemaHDF5Validator.DATASETS_MANDATORY_MESH))
        self.datasets_present.update(self._check_mandatory_dataset(GeometrySchemaHDF5Validator.DATASETS_1D_MAPS))
        self.datasets_present.update(self._check_mandatory_dataset(GeometrySchemaHDF5Validator.DATASETS_1D_MESH))

        self.datasets_present.update(self._check_optional_dataset(GeometrySchemaHDF5Validator.DATASETS_2D_MAPS))
        self.datasets_present.update(self._check_optional_dataset(GeometrySchemaHDF5Validator.DATASETS_2D_MESH))
        self.datasets_present.update(self._check_optional_dataset(GeometrySchemaHDF5Validator.DATASETS_3D_MAPS))
        self.datasets_present.update(self._check_optional_dataset(GeometrySchemaHDF5Validator.DATASETS_3D_MESH))

        self._check_consistent_maps_mesh_definition(self.datasets_present,GeometrySchemaHDF5Validator.DATASETS_MAPS,GeometrySchemaHDF5Validator.DATASETS_MESH)

        self.element_number = self._get_number_of_elements(self.datasets_present,GeometrySchemaHDF5Validator.DATASETS_MESH)
        self._check_element_construction(self.element_number)

        #finally check no extra unexpected payload in file
        valid_groups_keys: list[str] = [group.get_path() for group in GeometrySchemaHDF5Validator.BASE_GROUPS.values()]
        self._check_only_valid_groups_exist(valid_groups_keys)

        valid_dataset_keys: list[str] = [dataset.get_path() for dataset in GeometrySchemaHDF5Validator.DATASETS_MESH.values()] + \
                                        [dataset.get_path() for dataset in GeometrySchemaHDF5Validator.DATASETS_MAPS.values()]
        self._check_only_valid_datasets_exist(valid_dataset_keys)

        return True
    
    def _check_only_valid_groups_exist(self,valid_groups: list[str]):
        """Check that only valid HDF5 groups exist.

        Args:
            valid_groups (str): list of valid groups
        """
        #plus one to search for any extra invalid groups
        #"" is a valid group too, and is provided in function call
        valid_groups.append("")
        max_groups = len(valid_groups) + 1 
        groups = parsing.get_hdf5_groups_with_depth_limit(self.file,3,max_groups=max_groups)

        for group in groups:
            if group not in valid_groups:
                raise HDF5SchemaExtraDefinitionException(self.file,f"Encountered unkown group: {group}")

    def _check_only_valid_datasets_exist(self,valid_datasets: list[str]):
        """Check that only valid HDF5 datasets exist.

        Args:
            valid_datasets (str): list of valid datasets
        """
        max_datasets = len(valid_datasets) + 1
        datasets = parsing.get_hdf5_datasets_with_depth_limit(self.file,3,max_datasets=max_datasets)
        for dataset in datasets:
            if dataset not in valid_datasets:
                raise HDF5SchemaExtraDefinitionException(self.file,f"Encountered unkown dataset: {dataset}")

    def _check_mandatory_dataset(self,mandatory_datasets: MappingProxyType[str,HDF5DatasetDefinition]) -> set[str]:
        """Helper function. Checks mandatory datasets and if all valid, return the keys of the present datasets

        Args:
            mandatory_datasets (MappingProxyType[str,HDF5DatasetDefinition]): Dictionary of datasets that should be present

        Returns:
            set[str]: set of keys denoting which datasets are present
        """
        datasets_present_key: set[str] = set()

        for key,dataset in mandatory_datasets.items():
            if dataset.validate(self.file):
                datasets_present_key.add(key)

        return datasets_present_key

    def _check_optional_dataset(self,optional_dataset: MappingProxyType[str,HDF5DatasetDefinition]) -> set[str]:
        """Helper function. Checks optional datasets and valid datasets will have their keys added to present datasets, which is returned.

        Args:
            optional_dataset (MappingProxyType[str,HDF5DatasetDefinition]): Dataset definitions that are optional

        Returns:
            set[str]: set of keys denoting which datasets are present

        Raises:
            HDF5SchemaException: _description_
        """
        datasets_present_key: set[str] = set()

        for key,dataset in optional_dataset.items():
            try:
                dataset.validate(self.file)
                datasets_present_key.add(key)
            except HDF5SchemaExistenceException:
                pass #optional, so allow if doesn't exist, but any other definition error should be re-raised
            except Exception:
                raise

        return datasets_present_key

    def _check_consistent_maps_mesh_definition(self,
                                                present_datasets_keys: set[str],
                                                dataset_maps: dict[str,HDF5DatasetDefinition],
                                                dataset_mesh: dict[str,HDF5DatasetDefinition]) -> None:
        """Check that for all present dataset keys, there is a consistent definition between the MAPS and MESH

        Args:
            present_datasets_keys (set[str]): list of keys denoting datasets that are present
            dataset_maps (set[str,HDF5DatasetDefinition]): Definitions of MAPS datasets
            dataset_mesh (dict[str,HDF5DatasetDefinition]): Definitions of MESH datasets
        """
        #now check that each pair exists and have consistent shapes
        #maps can't be defined without corresponding mesh and vice versa
        for key in present_datasets_keys:
            #curve nodes only exception to above rule
            if key != "CURVE_NODES":
                self._check_pair_of_datasets(dataset_maps.get(key),dataset_mesh.get(key))

    def _check_pair_of_datasets(self, dataset_map: HDF5DatasetDefinition, dataset_mesh: HDF5DatasetDefinition) -> None:
        """Helper funcion for checking whether a map and mesh dataset have consistent definitions

        Args:
            dataset_1 (HDF5DatasetDefinition): First HDF5 dataset
            dataset_2 (HDF5DatasetDefinition): Second HDF5 dataset

        Raises:
            HDF5SchemaException: _description_
        """
        data_map = self.file.get(dataset_map.get_path())
        data_mesh = self.file.get(dataset_mesh.get_path())

        if (data_map is not None and data_mesh is None) or (data_mesh is not None and data_map is None):
            raise HDF5SchemaMissingDatasetException(self.file, f"HDF5 Schema Error: {dataset_map} and {dataset_mesh} should be defined together, \
                                                    but one exists and other doesn't")

        if data_map is not None and data_mesh is not None:
            if isinstance(data_map, h5py.Dataset) and isinstance(data_mesh, h5py.Dataset):
                shape_map = data_map.shape
                shape_mesh = data_mesh.shape
                if shape_map[0] != shape_mesh[0]:
                    raise HDF5SchemaInconsistentException(self.file, f"HDF5 Schema Error: {dataset_map} has shape {shape_map} and {dataset_mesh} \
                                                            has shape {shape_mesh}. Inconsistent lengths {shape_map[0]} != {shape_mesh[0]}")

    def _get_number_of_elements(self,
                                present_datasets_keys: set[str],
                                dataset_mesh: dict[str,HDF5DatasetDefinition]) -> dict[str,int]:
        """For all datasets present in the geometry file, generate a dictionary mapping dataset keys to number of elements defined.
        Assumes consistency between maps and meshes, so meshes will be used as it contains CURVE_NODES

        Args:
            present_datasets_keys (set[str]): set to track number of datasets that are present
            dataset_mesh (dict[str,HDF5DatasetDefinition]): list of valid dataset MESH definitions

        Returns:
            dict[str,int]: Number of elements in the geometry dataset for each element type
        """

        number_elements: dict[str,int] = {}

        for dataset_key in present_datasets_keys:
            dataset_definition: HDF5DatasetDefinition = dataset_mesh[dataset_key]
            data = self.file.get(dataset_definition.get_path())
            shape = data.shape
            elmt_num = shape[0]
            number_elements[dataset_key] = elmt_num

        return number_elements

    def _check_element_construction(self,num_elements: dict[str,int]):
        """Make sure element construction is consistent

        Args:
            num_elements (dict[str,int]): Mapping of HDF5 dataset to number of elements defined in that dataset

        Raises:
            HDF5SchemaMissingDefinitionException: _description_
            HDF5SchemaMissingDefinitionException: _description_
            HDF5DatasetDefinition: _description_
        """
        #3D elements can only be defined if corresponding 2D elements are present
        quads = num_elements.get("QUAD",0)
        tris = num_elements.get("TRI",0)
        
        if num_elements.get("HEX",None) and quads < 6:
            raise HDF5SchemaMissingDefinitionException(self.file,f"HDF5 Schema Error: HEX requires quads. There are only {quads} QUADS defined")

        if num_elements.get("TET",None) and tris < 4:
            raise HDF5SchemaMissingDefinitionException(self.file,f"HDF5 Schema Error: TET requires tris. There are only {tris} TRIS defined")
            
        if num_elements.get("PYR",None) and (tris < 4 or quads < 1):
            raise HDF5SchemaMissingDefinitionException(self.file,f"HDF5 Schema Error: PYR requires quads and tris. There are only {tris} TRIS and {quads} QUADS defined")
        
        if num_elements.get("PRISM",None) and (tris < 2 or quads < 4):
            raise HDF5SchemaMissingDefinitionException(self.file,f"HDF5 Schema Error: PRISM requires quads and tris. There are only {tris} TRIS and {quads} QUADS defined")
