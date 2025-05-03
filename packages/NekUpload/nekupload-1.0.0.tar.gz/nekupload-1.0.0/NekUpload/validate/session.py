from lxml import etree
import os
import numpy as np

from NekUpload.validate.exceptions import XMLSchemaException,MissingInputFileException,MissingOutputFileException,SessionFileException
from NekUpload.validate.files import NekGeometryFile,NekSessionFile,NekOutputFile
from NekUpload.NekData.composite import CompositeDefinition
from NekUpload.NekData.expansions import ExpansionDefinition
from NekUpload.NekData.data_type import Elements,SolverType
from NekUpload.NekData.solver import SolverInfo
from NekUpload.NekData.filters import CheckpointFilter,NekFilterFactory,NekFilter
from NekUpload.utils.notification import warn_with_logging

class ValidateSession:
    """Class responsible for validation session files
    """
    def __init__(self,file_path: str):
        """Class initialiser

        Args:
            file_path (str): File path to the session XML file
        """
        self.file_path = file_path
        self.xml_tree = self._load_DOM_tree(self.file_path)

    def _load_DOM_tree(self, xml_file: str) -> etree._Element:
        """Loads the DOM tree of the XML file

        Args:
            xml_file (str): Path to XML file

        Returns:
            etree._Element: Internal representation of DOM tree
        """
        with open(xml_file, "rb") as xml:
            xml_tree = etree.XML(xml.read())
        
        return xml_tree

    def is_valid_xml(self,xml_file: str,schema_file_path: str) -> bool:
        """Checks whether XML file conforms to a schema

        Args:
            xml_file (str): XML file path
            schema_file_path (str): XSD schema file path

        Raises:
            XMLSchemaException: _description_

        Returns:
            bool: Passed
        """
        xsd_file = schema_file_path
        
        with open(xsd_file,"rb") as xsd:
            schema_root = etree.XML(xsd.read())
            schema = etree.XMLSchema(schema_root)

        with open(xml_file,"rb") as xml:
            xml_tree = etree.XML(xml.read())
        
        if schema.validate(xml_tree):
            return True
        else:
            raise XMLSchemaException(xml_file,schema.error_log)
    
    def check_schema(self) -> bool:
        """Check file conforms to XML session schema

        Returns:
            bool: Passed
        """
        xsd_schema = os.path.join(os.path.dirname(__file__), 'schemas/nektar.xsd') #ensure path always correct
        return self.is_valid_xml(self.file_path, xsd_schema)
        
    def check_boundary_condition_schema(self,boundary_condition_files: list[str]) -> bool:
        """Identifies boundary condition files, and checks against schema

        Args:
            boundary_condition_files (list[str]): INput files

        Returns:
            bool: Valid
        """
        filenames: list[str] = [os.path.basename(file) for file in boundary_condition_files]
        with NekSessionFile(self.file_path) as f:
            bc_filenames: list[str] = f.get_all_boundary_condition_files()

        xsd_schema = os.path.join(os.path.dirname(__file__),"schemas/nektarbc.xsd")
        for idx,file in enumerate(filenames):
            if file in bc_filenames:
                file_path = boundary_condition_files[idx]
                self.is_valid_xml(file_path,xsd_schema)

        return True

    def check_boundary_definition(self,geometry_file: str) -> bool:
        """Check that all boundaries defined in session file are present in the geometry file

        Args:
            geometry_file (str): Geometry nekg file

        Returns:
            bool: Valid if all boundaries in geometry files are defined in nekg file
        """

        with NekSessionFile(self.file_path) as f:
            geometry_dim,*_ = f.get_geometry_info()
            #thses composite definitions contain C[...] i.e. ids for composites
            session_defined_composite: dict[int,CompositeDefinition] = f.get_all_defined_boundary_regions()

        with NekGeometryFile(geometry_file) as f:
            geometry_boundary_info: dict[int,CompositeDefinition] = None
            if geometry_dim == 2:
                #these composite definitions contain E[...] i.e. ids for edges
                geometry_boundary_info = f.get_composite_edge_info()
            elif geometry_dim == 3:
                #these composite definitions contain F[...] i.e. ids for faces
                geometry_boundary_info = f.get_composite_face_info()

        #extract all composite ids from geometry file that should be defined
        boundary_composite_ids_to_be_defined_in_geometry: set[int] = set(geometry_boundary_info.keys())

        #extract all composites that have been defined by session file
        boundary_composite_ids_defined_by_session: set[int] = set()
        for composite in session_defined_composite.values():
            boundary_composite_ids_defined_by_session.update(composite.composite_ids)

        #make sure all boundary composites in geometry are defined by session file
        if not boundary_composite_ids_defined_by_session <= boundary_composite_ids_to_be_defined_in_geometry:
            raise SessionFileException(self.file_path,(f"Session file has defined dimension as {geometry_dim} "
                                                    f"and expects {Elements.EDGE if geometry_dim == 2 else Elements.FACE}."
                                                    f"Geometry {geometry_file} expects COMPOSITE_ID : COMPOSITE_DEFINITION of {geometry_boundary_info}, "
                                                    f"while session {self.file_path} defined the following COMPOSITE_ID: {boundary_composite_ids_defined_by_session}"))
        
        return True

    def check_geometry_file_reference(self,geometry_file: str) -> bool:
        """Check whether the geometry file provided is the one referencedd by the session file

        Args:
            geometry_file (str): Geometry file name

        Raises:
            SessionFileException: _description_

        Returns:
            bool: Valid
        """

        with NekSessionFile(self.file_path) as f:
            _,_,referenced_geometry_filename = f.get_geometry_info()

        geometry_filename: str = os.path.basename(geometry_file)
        
        if geometry_filename != referenced_geometry_filename:
            raise SessionFileException(self.file_path,(f"Session file makes reference to <GEOMETRY HDF5FILE={referenced_geometry_filename}. "
                                                    f"However, you are uploading the geometry file: {geometry_filename}."))

        return True

    def check_boundary_conditions_reference(self,boundary_condition_files: list[str]) -> bool:
        """Checks whetehr all files referenced in BOUNDARYCONDITION in session file are
        present in the input list

        Args:
            boundary_condition_files (list[str]): Input file list

        Raises:
            SessionFileException: _description_

        Returns:
            bool: Valid
        """
        boundary_condition_file_set: set[str] = {os.path.basename(file) for file in boundary_condition_files}

        with NekSessionFile(self.file_path) as f:
            mandatory_bc_files: list[str] = f.get_all_boundary_condition_files()

        #make sure all mandatory boundary condition files are present
        for file in mandatory_bc_files:
            if file not in boundary_condition_file_set:
                raise SessionFileException(self.file_path,(f"Session file, under BOUNDARYCONDITIONS, makes reference to "
                                                        f" the following boundary condition files {mandatory_bc_files}. "
                                                        f"Did not find the file: {file}. "
                                                        f"You have provided the following files: {boundary_condition_files}"))

        return True

    def check_function_reference(self,function_file_list: list[str]) -> bool:
        """Checks whetehr all files referenced in FUNCTION in session file are
        present in the input list

        Args:
            function_file_list (list[str]): Input file list

        Raises:
            SessionFileException: _description_

        Returns:
            bool: Valid
        """
        function_file_set: set[str] = {os.path.basename(file) for file in function_file_list}

        with NekSessionFile(self.file_path) as f:
            mandatory_function_files: list[str] = f.get_all_function_files()

        #make sure all mandatory boundary condition files are present
        for file in mandatory_function_files:
            if file not in function_file_set:
                raise SessionFileException(self.file_path,(f"Session file, under FUNCTION/F, makes reference to "
                                                        f" the following function files {mandatory_function_files}. "
                                                        f"Did not find the file: {file}. "
                                                        f"You have provided the following files: {function_file_list}"))

        return True

    def check_filter_files_reference(self,file_list: list[str]) -> bool:

        #nektar is messy, some append ext others don't, so handle both cases
        #exclude .chk files as though they can come from filters, they are counted as a separate entity
        file_set: set[str] = {os.path.basename(file) for file in file_list}
        file_set_no_extension: set[str] = {os.path.splitext(os.path.basename(file))[0] for file in file_list}
        with NekSessionFile(self.file_path) as f:
            filter_list: list[NekFilter] = f.get_filters(exclude_chkpoints=True)

        expected_file_names: list[str] = [os.path.basename(f.output_file) for f in filter_list]

        #make sure all mandatory filter files are present
        for file in expected_file_names:
            if file not in file_set and file not in file_set_no_extension:
                raise SessionFileException(self.file_path,(f"Session file, under FILTERS, makes reference to "
                                                        f" the following filters {expected_file_names}. "
                                                        f"Did not find the output file for filter: {file}. "
                                                        f"You have provided the following files: {file_set}"))

        return True

    def get_checkpoint_filter_filenames(self) -> list[str]:
        with NekSessionFile(self.file_path) as f:
            filter_list: list[NekFilter] = f.get_filters("Checkpoint")

        filename_list = [filter.output_file for filter in filter_list]

        return filename_list

    def check_checkpoint_files(self,checkpoint_files:list[str]) -> bool:

        #if checkpoints are defined in both parameters and filters, both are printed out
        chk_file_num_from_parameters,chk_timesteps_from_parameters = self._compute_chk_file_requirements_from_filter()
        chk_file_num_from_filter,chk_timesteps_from_filter = self._compute_chk_file_requirements_from_parameters()

        chk_file_num = chk_file_num_from_parameters + chk_file_num_from_filter

        #generate a list from the checkpoint_files, as may not all be checkpoint files
        #should have .chk
        chk_file_list: list[str] = [file for file in checkpoint_files if file.endswith(".chk")]

        if len(chk_file_list) != chk_file_num:
            raise SessionFileException(self.file_path,(f"Based on the session file provided, there should be {chk_file_num} checkpoint files (.chk)."
                                                    f"There are actually {len(chk_file_list)} files: {chk_file_list}"))
        
        return True

    def _compute_chk_file_requirements_from_filter(self) -> tuple[int,tuple[float,...]]:
        """Given PARAMETERS and FILTERS in session file, try and identify how many checkpoint files are generated.
        Attempts to find Checkpoint FILTER in FILTERS. If does not exist, returns empty information.

        Returns:
            tuple[int,tuple[float,...]]: Number of checkpoint files and a tuple contianing the expected time step at each point
        """
        
        with NekSessionFile(self.file_path) as f:
            chk_filter: list[CheckpointFilter] = f.get_filters("Checkpoint")

            params: dict[str,int | float] = f.get_parameters()

            num_steps: int = int(params.get("NumSteps", 0))
            time_step: float | None = params.get("TimeStep")
            final_time: float | None = params.get("FinTime")

        #TODO unknown implementation, will need to doublecheck
        if len(chk_filter) > 2:
            raise SessionFileException(self.file_path,(
                f"While looking for checkpoint filters under FILTERS, found {len(chk_filter)} CHECKPOINT definitions."
                f"Undefined behaviour."
            ))
        #for no checkpoint filters found, return empty
        if not chk_filter:
            return (0,())

        output_frequency:int = chk_filter[0].output_frequency
        output_start_time: int = chk_filter[0].output_start_time
        if output_frequency == 0:
            return (0,())

        num_steps,time_step,final_time = self._resolve_timestep_parameters(num_steps,time_step,final_time)

        #make end inclusive, use deltat/2 to prevent accidental additions in other point
        time_steps_at_chk_number: tuple[float] = tuple(np.arange(output_start_time,final_time + time_step / 2,output_frequency*time_step))
        chk_file_num: int = len(time_steps_at_chk_number) 

        return (chk_file_num,time_steps_at_chk_number)

    def _compute_chk_file_requirements_from_parameters(self) -> tuple[int,tuple[float,...]]:
        """Given PARAMETERS in session file, try and identify how many checkpoint files are generated.
        If IO_CheckSteps is 0, function returns safely. If IO_CheckSteps is not defined, function returns safely.
        If IO_CheckSteps is defined, but two of NumSteps,TimeStep,FinTime are not defined, then function will exit with exception.
        Otherwise, the number of checkpoint files to be generated is returned.

        Returns:
            tuple[int,tuple[float,...]]: Number of checkpoint files and a tuple contianing the expected time step at each point
        """
        with NekSessionFile(self.file_path) as f:
            params: dict[str,int | float] = f.get_parameters()

            checkpoint_steps: int = int(params.get("IO_CheckSteps", 0))
            num_steps: int = int(params.get("NumSteps", 0))
            time_step: float | None = params.get("TimeStep")
            final_time: float | None = params.get("FinTime")

        #if checkpoint_steps = 0 or is None, no information on checkpoint files from PARAMETERS
        if checkpoint_steps == 0:
            return (0,())
        
        warn_with_logging((f"You have specified checkpoint files via IO_CHECKSTEPS in PARAMETERS. "
                        f"This may be deprecated in future. Recommendation is to set checkpoint file "
                        f"output under FILTERS using <FILTER NAME='Checkpoint'>. See user documentation for more details."
        ))

        num_steps,time_step,final_time = self._resolve_timestep_parameters(num_steps,time_step,final_time)

        INITIAL_STATE_CHK_FILE: int = 1
        num_chk_files = num_steps // checkpoint_steps + INITIAL_STATE_CHK_FILE

        time_steps_at_chk_number: tuple[float,...] = tuple([chk_num * checkpoint_steps * time_step for chk_num in range(0,num_chk_files)])

        return (num_chk_files,time_steps_at_chk_number)
        
    def _resolve_timestep_parameters(self,num_steps:int | None,time_step:float | None,final_time:float | None) -> tuple[int,float,float]:
        """These parameters may or may not be explicitly defined. They therefore need to be resolved.
        If insufficient information to caclulate these values, throw an error.

        Args:
            num_steps (int): _description_
            time_step (float): _description_
            final_time (float): _description_

        Raises:
            SessionFileException: _description_
            SessionFileException: _description_

        Returns:
            tuple[int,float,float]: num_steps,time_step,final_time
        """
        
        #if total number of simulation steps not defined explicitly, 
        #then time_stpe and final_time must be defined
        if num_steps is None or num_steps == 0:
            if time_step is None or final_time is None:
                raise SessionFileException(self.file_path,(
                    "While attempting to identify the number of checkpoint files generated based on provided parameters, "
                    f"identified the following: NumSteps=None, TimeStep={time_step}, "
                    f"FinTime: {final_time}. Insufficient information to identify NumSteps from TimeStep and FinTime."
                ))
            else:
                num_steps = int(round(final_time / time_step))

        #if time step not defined explicitly, then num_steps and final_time should be defined
        if time_step is None:
            if num_steps is None or num_steps == 0 or final_time is None:
                raise SessionFileException(self.file_path,(
                    "While attempting to identify the number of checkpoint files generated based on provided parameters, "
                    f"identified the following: NumSteps={num_steps}, TimeStep={time_step}, "
                    f"FinTime: {final_time}. Insufficient information to identify TimeStep from NumSteps and FinTime."
                ))
            else:
                time_step = final_time / num_steps

        #if final time not defined explicitly, then num_steps and time_steps should be defined
        #if got to this point in code, already guaranteed that num_steps and time_steps are defined
        if not final_time:
            final_time = time_step * num_steps

        #finally, check that numbers are constistent
        #particularly important for when all three parameters are explicitly defined
        if abs(time_step * num_steps - final_time) > 1e-6:
            raise SessionFileException(self.file_path,(
                "While attempting to identify the number of checkpoint files generated based on provided parameters, "
                f"identified the following: NumSteps={num_steps}, TimeStep={time_step}, "
                f"FinTime: {final_time}. Inconsistency found between provided information. "
                f"NumSteps * TimeStep = FinTime => {num_steps * time_step} != {final_time}"
            ))
        return num_steps,time_step,final_time

    def check_expansion_definition(self,geometry_file:str) -> bool:
        """Check whether expansion definition reference the composite objects 
        defined in the geometry file

        Args:
            geometry_file (str): Path to geometry nekg file

        Returns:
            True: Valid
        """
        with NekSessionFile(self.file_path) as f:
            #this function indirectly checks that all expansions defined in session
            # are defined correctly in geometry
            f.get_expansions(geometry_file) 

        return True
    
    #TODO Refactor, quite ugly atm
    def check_consistent_output_shape(self,
                                    geometry_file:str,
                                    output_file:str,
                                    solver:SolverType,
                                    field_count:int=0) -> bool:
        with NekSessionFile(self.file_path) as f:
            composite_id_to_expansion: dict[int,list[ExpansionDefinition]] = f.get_expansions(geometry_file)
            eq_type: str = f.get_equation_type()
            dim,*_ = f.get_geometry_info()
            is_movement_exist: bool = f.is_movement()
            homogeneous_property: str = f.get_homogeneous_property()
            hom_y_modes,hom_z_modes = f.get_homogeneous_modes()
            homogeneous_coeffs_multiplier: int = 1
            #different flavours of the same thing, as specified in nektar/FieldUtils/Fields
            if (homogeneous_property == "1D" or homogeneous_property == "HOMOGENEOUS1D"
            or homogeneous_property == "Homogeneous1D" or homogeneous_property == "Homo1D"):
                homogeneous_coeffs_multiplier *= hom_z_modes
                dim = 3#recast as quasi-3D
            elif (homogeneous_property == "2D" or homogeneous_property == "HOMOGENEOUS2D"
            or homogeneous_property == "Homogeneous2D" or homogeneous_property == "Homo2D"):
                homogeneous_coeffs_multiplier *= (hom_z_modes * hom_y_modes)
                dim = 3#recast as quasi-3D
            
            IS_REFINEMENT_DEFINED = bool(f.get_refinements())
            IS_FORCING_DEFINED = f.is_forcing_defined()

        with NekGeometryFile(geometry_file) as f:
            composite_list: dict[int,CompositeDefinition] = f.get_composite_info()

        solver_info = SolverInfo(solver,dim,eq_type)
        num_fields_default = solver_info.get_var_num() if field_count == 0 else field_count

        num_unkown_coefficients: int = 0
        for composite_id,expansion_list in composite_id_to_expansion.items():
            composite: CompositeDefinition = composite_list[composite_id]

            #first find total number of fields and max element number for same composite
            #take larger coefficients, as padding is used
            num_fields_from_file = sum([len(expansion.fields) for expansion in expansion_list])
            max_num_coeffs = max([expansion.get_num_coefficients() for expansion in expansion_list])
            
            num_fields = 0
            if solver == SolverType.ADR_SOLVER:
                num_fields = num_fields_from_file
            else:
                num_fields = num_fields_default

            if is_movement_exist:
                num_fields += len(["gridVx","gridVy","gridVz"])
            num_unkown_coefficients += max_num_coeffs * composite.count * num_fields * homogeneous_coeffs_multiplier

        with NekOutputFile(output_file) as f:
            total_coeffs:int = f.get_total_coefficients() #this should be 1D
        
        try:
            if total_coeffs != num_unkown_coefficients:
                raise SessionFileException(self.file_path,(f"Based on session file, " 
                                                    f"there should be {num_unkown_coefficients} unknown coefficients."
                                                    f"Provided output file {output_file} contains {total_coeffs} calculated coefficients"))
        except SessionFileException as e:

            #if one of the unimplemented cases, skip, else raise
            if IS_FORCING_DEFINED:
                warn_with_logging(f"Due to presence of FORCING, which currently has unkown rules, "
                                f" failed validation will not cause hard failure. Administrators will "
                                f"check output file.")
                return True

            if IS_REFINEMENT_DEFINED:
                warn_with_logging((f"You have refinements in this file. Skipping output shape check as this "
                                "has not yet been implemented. "))
                return True
            
            raise

        return True

if __name__ == "__main__":
    f = "tests/datasets/IncNavierStokes/PlungingAirfoil_3DH1D_with_NACA0012_Re400"
    validator = ValidateSession(f"{f}.xml")
    validator.check_consistent_output_shape(f"{f}.nekg",f"{f}.fld",SolverType.INCOMPRESSIBLE_NAVIER_STOKES_SOLVER)