import pytest
from NekUpload.manager import NekManager,OutputManager,GeometryManager,SessionManager
from NekUpload.metadata import *
from NekUpload.testutils import NekTestDataset,DATASETS,BOUNDARY_CONDITION_DATASETS,FILTERS_DATASETS
from NekUpload.NekData.data_type import SolverType

@pytest.fixture
def metadata() -> InvenioMetadata:
    title = "THIS IS A TEST: DELETE ON SIGHT"
    creator = InvenioPersonInfo("John","Doe")
    version = "1.0.0"
    publisher = "NekUpload"
    description = "DELETE ME NOW!!!"
    publication_date = "2020-01-01"

    metadata = InvenioMetadata(title,publication_date,[creator],ResourceType.DATASET)
    metadata.add_version(version)
    metadata.add_publisher(publisher)
    metadata.add_description(description)

    return metadata

###############################################################################
# Tests using the new testutils feature
###############################################################################
@pytest.mark.integration
@pytest.mark.parametrize("dataset",tuple(DATASETS),ids=str)
def test_nektar_datasets(dataset: NekTestDataset,metadata:InvenioMetadata):
    session: str = dataset.session
    geometry: str = dataset.geometry
    output: str = dataset.output
    checkpoints: list[str] = dataset.checkpoints
    filters: list[str] = dataset.filters
    input_supporting_files: list[str] = dataset.input_supporting_files

    #use same metadata instance, as not testing metadata
    geometry_manager = GeometryManager(geometry,metadata=metadata)
    session_manager = SessionManager(session,input_supporting_files,metadata=metadata)
    output_manager = OutputManager(output,checkpoints,filters,metadata=metadata)

    nek_manager = NekManager(geometry_manager,session_manager,output_manager)

    try:
        nek_manager.validate(dataset.solver_type)
    except Exception as e:
        #custom assert to make it clearer which dataset failed
        pytest.fail(f"While testing the dataset: {dataset}, an error occured: {e}")

@pytest.mark.integration
@pytest.mark.parametrize("dataset",tuple(BOUNDARY_CONDITION_DATASETS),ids=str)
def test_session_files_with_bc_files(dataset:NekTestDataset,metadata:InvenioMetadata):  
    session: str = dataset.session
    geometry: str = dataset.geometry
    output: str = dataset.output
    checkpoints: list[str] = dataset.checkpoints
    filters: list[str] = dataset.filters
    input_supporting_files: list[str] = dataset.input_supporting_files

    #use same metadata instance, as not testing metadata
    geometry_manager = GeometryManager(geometry,metadata=metadata)
    session_manager = SessionManager(session,input_supporting_files,metadata=metadata)
    output_manager = OutputManager(output,checkpoints,filters,metadata=metadata)

    nek_manager = NekManager(geometry_manager,session_manager,output_manager)
    
    #should raise no errors
    nek_manager.validate(dataset.solver_type)

@pytest.mark.integration
@pytest.mark.parametrize("dataset",tuple(BOUNDARY_CONDITION_DATASETS),ids=str)
def test_session_files_with_missing_bc_files(dataset:NekTestDataset,metadata:InvenioMetadata):  
    session: str = dataset.session
    geometry: str = dataset.geometry
    output: str = dataset.output
    checkpoints: list[str] = dataset.checkpoints
    boundary_conditions: list[str] = dataset.boundary_conditions
    filters: list[str] = dataset.filters
    input_supporting_files: list[str] = dataset.input_supporting_files

    #we will now remove boundary condition files
    for f in boundary_conditions:
        input_supporting_files.remove(f)

    #use same metadata instance, as not testing metadata
    geometry_manager = GeometryManager(geometry,metadata=metadata)
    session_manager = SessionManager(session,input_supporting_files,metadata=metadata)
    output_manager = OutputManager(output,checkpoints,filters,metadata=metadata)

    nek_manager = NekManager(geometry_manager,session_manager,output_manager)
    
    with pytest.raises(Exception):
        nek_manager.validate(dataset.solver_type)

@pytest.mark.integration
@pytest.mark.parametrize("dataset",tuple(FILTERS_DATASETS),ids=str)
def test_session_files_with_filter_outputs(dataset:NekTestDataset,metadata:InvenioMetadata):  
    session: str = dataset.session
    geometry: str = dataset.geometry
    output: str = dataset.output
    checkpoints: list[str] = dataset.checkpoints
    boundary_conditions: list[str] = dataset.boundary_conditions
    filters: list[str] = dataset.filters
    input_supporting_files: list[str] = dataset.input_supporting_files

    #we will now remove last filter file
    for f in filters:
        if not (f.endswith(".his") or f.endswith(".fce") or f.endswith(".chk")):
            pytest.skip(f"Skipping test for unsupported filter file extension: {f}")

    filters.pop()

    #use same metadata instance, as not testing metadata
    geometry_manager = GeometryManager(geometry,metadata=metadata)
    session_manager = SessionManager(session,input_supporting_files,metadata=metadata)
    output_manager = OutputManager(output,checkpoints,filters,metadata=metadata)

    nek_manager = NekManager(geometry_manager,session_manager,output_manager)

    with pytest.raises(Exception):
        nek_manager.validate(dataset.solver_type)

###############################################################################
@pytest.mark.integration
def test_ADR_invalid(ADR_dataset_abs_paths,metadata):
    ADR_datasets: list[dict[str, str | list[str] | None]] = ADR_dataset_abs_paths

    for dataset in ADR_datasets:
        #accidental mixup of files
        session: str = dataset["SESSION"]
        geometry: str = dataset["OUTPUT"]
        output: str = dataset["GEOMETRY"]
        checkpoints: list[str] = dataset["CHECKPOINT"]

        #use same metadata instance, as not testing metadata
        geometry_manager = GeometryManager(geometry,metadata=metadata)
        session_manager = SessionManager(session,metadata=metadata)
        output_manager = OutputManager(output,checkpoints,metadata=metadata)

        nek_manager = NekManager(geometry_manager,session_manager,output_manager)

        with pytest.raises(Exception):
            nek_manager.validate(SolverType.ADR_SOLVER)

@pytest.mark.integration
@pytest.mark.internet
def test_ADR_optional_validation(ADR_dataset_abs_paths,metadata):
    ADR_datasets: list[dict[str, str | list[str] | None]] = ADR_dataset_abs_paths

    for dataset in ADR_datasets:
        session: str = dataset["SESSION"]
        geometry: str = dataset["GEOMETRY"]
        output: str = dataset["OUTPUT"]
        checkpoints: list[str] = dataset["CHECKPOINT"]

        #use same metadata instance, as not testing metadata
        geometry_manager = GeometryManager(geometry,metadata=metadata)
        session_manager = SessionManager(session,metadata=metadata)
        output_manager = OutputManager(output,checkpoints,metadata=metadata)

        nek_manager = NekManager(geometry_manager,session_manager,output_manager)

        assert nek_manager.optional_validation(), "Optional validation failed for ADR dataset."

