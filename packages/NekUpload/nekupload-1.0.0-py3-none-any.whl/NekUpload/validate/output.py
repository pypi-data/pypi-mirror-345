import os
import h5py
import re

from .hdf5_definitions import HDF5GroupDefinition,HDF5DatasetDefinition
from .exceptions import OutputFileException,HDF5SchemaInconsistentException,HDF5SchemaExtraDefinitionException,ExperimentalException
from NekUpload.utils import parsing
from NekUpload.utils import gitlab_api as GitlabAPI
from NekUpload.validate.files import NekOutputFile,NekSessionFile
from NekUpload.validate.session import ValidateSession

class ValidateOutput:
    """Class responsible for all output file validation checks
    """
    def __init__(self, file_path: str):
        """Class initialiser

        Args:
            file_path (str): File path to output file
        """
        self.file = file_path
        self.file_name = os.path.basename(self.file)

    def check_schema(self) -> bool:
        """Check Output file conforms to HDF5 schema

        Raises:
            OutputSchemaHDF5Validator: _description_

        Returns:
            bool: Passed
        """
        try:
            with h5py.File(self.file, 'r') as f:
                self.schema_checker = OutputSchemaHDF5Validator(f)
                self.schema_checker.validate()
        except OSError as e:
            raise OutputFileException(self.file,f"Geometry file either does not exist or is not in HDF5 format {e}")

        return True
    
    def check_checkpoint_schema(self,filter_checkpoint_list: list[str],chkpoint_file_list: list[str]) -> bool:
        with NekOutputFile(self.file) as f:
            decomposition_info = f.get_decomposition()

        def chk_file_is_from_filter(chk_file: list[str]) -> bool:
            """Helper to check if a single file matches any filter pattern."""
            for pattern in filter_checkpoint_list:
                pattern = pattern.split(".")[0] #remove any extensions if they exist
                if re.search(rf'{re.escape(pattern)}', chk_file):
                    return True
            return False

        for file in chkpoint_file_list:
            if chk_file_is_from_filter(file):
                #for now just skip over these
                # they may have different structure to checkpoint files generated from parameters
                continue

            with NekOutputFile(file) as f:
                decomposition = f.get_decomposition()
                if decomposition != decomposition_info:
                    raise OutputFileException(self.file,f"Output file {self.file} and checkpoint file {file} have mismatched DECOMPOSITION definitions: \n"
                                            f"OUTPUT FILE: {decomposition_info}. \n"
                                            f"CHECKPOINT FILE: {decomposition}. ")

            with h5py.File(file, 'r') as f:
                schema_checker = OutputSchemaHDF5Validator(f)
                schema_checker.validate()

    def check_checkpoint_from_filter_schema(self,session_file: str,geometry_file: str, solver, filter_checkpoint_list: list[str], chkpoint_file_list: list[str]) -> bool:
        def chk_file_is_from_filter(chk_file: list[str]) -> bool:
            """Helper to check if a single file matches any filter pattern."""
            for pattern in filter_checkpoint_list:
                pattern = pattern.split(".")[0] #remove any extensions if they exist
                if re.search(rf'{re.escape(pattern)}', chk_file):
                    return True
            return False

        for file in chkpoint_file_list:
            if not chk_file_is_from_filter(file):
                #for now just skip over these
                # they may have different structure to checkpoint files generated from parmaters
                continue

            with NekSessionFile(session_file) as f:
                var_num: int = len(f.get_variable_list())

            checker = ValidateSession(session_file)
            try:
                checker.check_consistent_output_shape(geometry_file,file,solver,var_num)
            except Exception as e:
                raise ExperimentalException("Checking checkpoint filter files",
                                            "This feature is in ValidateSession.check_consistent_output_shape")

    def check_commit_is_public(self) -> bool:
        """Check that the GitSHA in the file is public

        Returns:
            bool: _description_
        """
        with NekOutputFile(self.file) as f:
            gitsha = f.get_gitsha()

        if gitsha is None:
            return False
        
        try:
            GitlabAPI.get_single_commit("https://gitlab.nektar.info","2",gitsha)
            return True
        except GitlabAPI.MissingGitlabCommit:
            return False

class OutputSchemaHDF5Validator:
    """Class for handling output HDF5 schema validation
    """

    NO_DIM_CONSTRAINTS = -1 #helper

    BASE_GROUPS = (HDF5GroupDefinition("NEKTAR",attributes=["FORMAT_VERSION"]),
                #this is bare minimum, depending on solver, can have more, also sessionFile
                #previously had TIME, but some runs do not output time
                HDF5GroupDefinition("NEKTAR/Metadata",attributes=["ChkFileNum"]), 
                HDF5GroupDefinition("NEKTAR/Metadata/Provenance",attributes=["GitBranch","GitSHA1","Hostname","NektarVersion","Timestamp"]))

    EXPECTED_DATASETS = (HDF5DatasetDefinition("NEKTAR/DECOMPOSITION",(NO_DIM_CONSTRAINTS,)),)

    def __init__(self,f: h5py.File):
        """Class initialiser

        Args:
            f (h5py.File): Opened HDF5 file
        """
        self.file: h5py.File = f

    def validate(self):
        """Check whether specified file conforms to the HDF5 output schema
        """
        self._check_mandatory_groups(OutputSchemaHDF5Validator.BASE_GROUPS)
        self._check_mandatory_datasets(OutputSchemaHDF5Validator.EXPECTED_DATASETS)

        #acquire all other groups and datasets that should be present based on DECOMPOSITION definition
        self._assert_decomposition()
        expansion_groups: tuple[HDF5GroupDefinition] = tuple(self._get_expansion_groups())
        optional_datasets: tuple[HDF5DatasetDefinition] = tuple(self._get_optional_datasets())

        self._check_mandatory_groups(expansion_groups)
        self._check_mandatory_datasets(optional_datasets)
        
        #check no extraneous groups or datasets
        valid_groups: tuple[HDF5GroupDefinition] = OutputSchemaHDF5Validator.BASE_GROUPS + expansion_groups
        valid_datasets: tuple[HDF5DatasetDefinition] = OutputSchemaHDF5Validator.EXPECTED_DATASETS + optional_datasets

        valid_groups_str = [group.get_path() for group in valid_groups]
        valid_datasets_str = [dataset.get_path() for dataset in valid_datasets]
        self._check_only_valid_groups_exist(valid_groups_str)
        self._check_only_valid_datasets_exist(valid_datasets_str)

        #check some more DECOMPOSITION data???

        #assert true, for testing purposes
        return True

    def _check_mandatory_groups(self,groups: tuple[HDF5GroupDefinition]):
        """Check whether mandatory HDF5 Groups are present in the file

        Args:
            groups (tuple[HDF5GroupDefinition]): list of mandatory HDF5 Group definitions
        """
        for group in groups:
            group.validate(self.file)

    def _check_mandatory_datasets(self,datasets: tuple[HDF5DatasetDefinition]):
        """CHeck whether mandatory HDF5 Datasets are present in the file

        Args:
            datasets (tuple[HDF5DatasetDefinition]): list of mandatory HDF5 Dataset definitions
        """
        for dataset in datasets:
            dataset.validate(self.file)

    def _assert_decomposition(self):
        """Assert decomposition has correct shape

        Raises:
            HDF5SchemaInconsistentException: _description_
        """
        #decomposition should come in group of 7
        if self.file["NEKTAR/DECOMPOSITION"].shape[0] % 7 != 0:
            raise HDF5SchemaInconsistentException(self.file,"HDF5 Schema Error: Decomposition shape should be multiple of 7")

    def _get_expansion_groups(self) -> list[HDF5GroupDefinition]:
        """Get the expansion groups that should be defined, based on what is in DECOMPOSITION

        Raises:
            HDF5SchemaInconsistentException: _description_

        Returns:
            list[HDF5GroupDefinition]: _description_
        """
        decomposition_dataset: h5py.Dataset = self.file["NEKTAR/DECOMPOSITION"]
        #last of the 7 is a hash pointing to location in HDF5 file containing expansion data
        num_expansion_groups = decomposition_dataset.shape[0] // 7

        expected_groups: list[HDF5GroupDefinition] = []
        for i in range(6,7*num_expansion_groups,7):
            hash = decomposition_dataset[i]
            expected_groups.append(HDF5GroupDefinition(f"NEKTAR/{hash}",attributes=["BASIS","FIELDS","NUMMODESPERDIR","SHAPE"]))

        return expected_groups
    
    def _get_optional_datasets(self) -> list[HDF5DatasetDefinition]:
        """Get all optional datasets defined by DECOMPOSITION

        Returns:
            list[HDF5DatasetDefinition]: _description_
        """
        optional_datasets: list[HDF5DatasetDefinition] = []

        optionals = {"NEKTAR/ELEMENTIDS": 0,
                    "NEKTAR/DATA": 1,
                    "NEKTAR/POLYORDERS": 2,
                    "NEKTAR/HOMOGENEOUSYIDS": 3,
                    "NEKTAR/HOMOGENEOUSZIDS": 4,
                    "NEKTAR/HOMOGENEOUSSIDS": 5}

        for name,idx in optionals.items():
            if dataset := self._get_dataset_defined_in_decomposition(name,idx):
                optional_datasets.append(dataset)

        return optional_datasets
    
    def _get_dataset_defined_in_decomposition(self,
                                            dataset_name: str,
                                            decomposition_entry_id: int) -> HDF5DatasetDefinition | None:
        """DECOMPOSITION contains sequence of 7 entries, some of which will lead to definition of
        extra datasets within the file. When the following are non-zero, a dataset is expected, and
        are constructed with the same rule:

        Note starting from 0:
        2 -> number of modes when variable polynomial is defined
        3 -> number of y planes for homogeneous simulations
        4 -> number of z planes for homogeneous simulations
        5 -> number of strips for homogeneous simulations

        Args:
            dataset_name (str): Name of the dataset to be defined
            decomposition_entry_id (int): Decomposition entry id for desired dataset 

        Returns:
            Optional[HDF5DatasetDefinition]: Dataset schema definition if one is required
        """
        decomposition_dataset: h5py.Dataset = self.file["NEKTAR/DECOMPOSITION"]
        size = decomposition_dataset.shape[0]
        num_data_points: int = 0

        for i in range(decomposition_entry_id,size,7):
            num_data_points += decomposition_dataset[i]

        return HDF5DatasetDefinition(dataset_name,(num_data_points,)) if num_data_points > 0 else None

    def _get_polyorder_dataset(self) -> HDF5DatasetDefinition | None:
        """Get the polyorder dataset definition if it should exist, based on DECOMPOSITION entries, every third entry

        Returns:
            Optional[HDF5DatasetDefinition]: If polyorder dataset is defined, definition is returned, else None
        """
        decomposition_dataset: h5py.Dataset = self.file["NEKTAR/DECOMPOSITION"]
        size = decomposition_dataset.shape[0]
        #3rd of the 7 grouping in decomposition
        #is a number of modes that are polyorder???
        num_polyorder_modes: int = 0

        for i in range(2,size,7):
            num_polyorder_modes += decomposition_dataset[i]

        return HDF5DatasetDefinition("NEKTAR/POLYORDERS",(num_polyorder_modes,)) if num_polyorder_modes > 0 else None

    def _check_only_valid_groups_exist(self,valid_groups: list[str]):
        """Check that only valid groups exist.

        Args:
            valid_groups (str): list of paths for valid HDF5 Groups
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
        """Check that only valid datasets exist.

        Args:
            valid_datasets (str): list of paths for valid HDF5 Datasets
        """
        max_datasets = len(valid_datasets) + 1
        datasets = parsing.get_hdf5_datasets_with_depth_limit(self.file,3,max_datasets=max_datasets)
        for dataset in datasets:
            if dataset not in valid_datasets:
                raise HDF5SchemaExtraDefinitionException(self.file,f"Encountered unkown dataset: {dataset}")