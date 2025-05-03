from __future__ import annotations
from dataclasses import dataclass,field
from typing import Callable,Optional
import os
from types import MappingProxyType
import logging

from NekUpload.NekData.data_type import SolverType
from NekUpload.NekData.expansions import ExpansionDefinition

"""Handles autodiscovery of test datasets. Provides decorators which can be used
to specify which tests datasets can be run for
"""

###############################################################################
# Data types
###############################################################################
@dataclass(frozen=True)
class NekTestDataset:
    """Defines a Nektar++ dataset

    Raises:
        FileNotFoundError: _description_
        FileNotFoundError: _description_
        FileNotFoundError: _description_
        FileNotFoundError: _description_
        FileNotFoundError: _description_
        FileNotFoundError: _description_

    Returns:
        _type_: _description_
    """
    solver_type: SolverType
    session: str
    geometry: str
    output: str
    checkpoints: list[str] = field(default_factory=list)
    filters: list[str] = field(default_factory=list)
    boundary_conditions: list[str] = field(default_factory=list)
    functions: list[str] = field(default_factory=list)

    @property
    def input_supporting_files(self) -> list[str]:
        return self.boundary_conditions + self.functions

    def __post_init__(self):
        if not os.path.exists(self.session):
            raise FileNotFoundError(f"Session file does not exist: {self.session}")
        if not os.path.exists(self.geometry):
            raise FileNotFoundError(f"Geometry file does not exist: {self.geometry}")
        if not os.path.exists(self.output):
            raise FileNotFoundError(f"Output file does not exist: {self.output}")
        for checkpoint in self.checkpoints:
            if not os.path.exists(checkpoint):
                raise FileNotFoundError(f"Checkpoint file does not exist: {checkpoint}")
        for filter_file in self.filters:
            if not os.path.exists(filter_file):
                raise FileNotFoundError(f"Filter file does not exist: {filter_file}")
        for bc_file in self.boundary_conditions:
            if not os.path.exists(bc_file):
                raise FileNotFoundError(f"Boundary condition file does not exist: {bc_file}")

    def __str__(self):
        return f"NekDataset: {os.path.basename(self.session)}"

@dataclass(frozen=True)
class NekTestGeometryComposite:
    """Maps NEKTAR/GEOMETRY/MAPS/COMPOSITE -> NEKTAR/GEOMETRY/MESH/COMPOSITE
    """
    composite_id_to_definition_map: dict[int,str]
    dim: int
    description: str="" #description of what is this testing

    @property
    def boundary_composite_id_to_definition_map(self) -> dict[int,str]:
        if self.dim == 2:
            return {idx: definition for idx, definition 
                    in self.composite_id_to_definition_map.items() if 'E' in definition}
        if self.dim == 3:
            return {idx: definition for idx, definition 
                    in self.composite_id_to_definition_map.items() if 'F' in definition}
        return {}

@dataclass(frozen=True)
class NekTestSessionExpansion:
    composite_id_to_expansion_definitions_map: dict[int,list[ExpansionDefinition]]
    description: int="" #description of what is this testing

###############################################################################
# Variables for export
###############################################################################
DATASETS: list[NekTestDataset] = []
ACOUSTIC_SOLVER_DATASETS: list[NekTestDataset] = []
ADR_SOLVER_DATASETS: list[NekTestDataset] = []
CARDIAC_EPS_SOLVER_DATASETS: list[NekTestDataset] = []
COMPRESSIBLE_SOLVER_DATASETS: list[NekTestDataset] = []
DIFFUSION_SOLVER_DATASETS: list[NekTestDataset] = []
IMAGE_WARPING_SOLVER_DATASETS: list[NekTestDataset] = []
INC_NAVIER_STOKES_SOLVER_DATASETS: list[NekTestDataset] = []
LINEAR_ELASTIC_SOLVER_DATASETS: list[NekTestDataset] = []
MMF_SOLVER_DATASETS: list[NekTestDataset] = []
PULSE_WAVE_SOLVER_DATASETS: list[NekTestDataset] = []
SHALLOW_WATER_SOLVER_DATASETS: list[NekTestDataset] = []
VORTEX_WAVE_INTERACTION_SOLVER_DATASETS: list[NekTestDataset] = []

BOUNDARY_CONDITION_DATASETS: list[NekTestDataset] = []
FUNCTIONS_DATASETS: list[NekTestDataset] = []
FILTERS_DATASETS: list[NekTestDataset] = []

GEOMETRY_COMPOSITE_DATASETS: list[tuple[NekTestDataset,NekTestGeometryComposite]] = [] #for tests requiring comparing composite information
SESSION_EXPANSION_DATASETS: list[tuple[NekTestDataset,NekTestSessionExpansion]] = [] #for tests requiring comparing expansion information

###############################################################################
# Decorators to call
###############################################################################
_dataset_map: MappingProxyType[SolverType,list[NekTestDataset]] = MappingProxyType({
    SolverType.ADR_SOLVER: ADR_SOLVER_DATASETS,
    SolverType.ACOUSTIC_SOLVER: ACOUSTIC_SOLVER_DATASETS,
    SolverType.CARDIAC_EPS_SOLVER: CARDIAC_EPS_SOLVER_DATASETS,
    SolverType.COMPRESSIBLE_FLOW_SOLVER: COMPRESSIBLE_SOLVER_DATASETS,
    SolverType.DIFFUSION_SOLVER: DIFFUSION_SOLVER_DATASETS,
    SolverType.IMAGE_WARPING_SOLVER: IMAGE_WARPING_SOLVER_DATASETS,
    SolverType.INCOMPRESSIBLE_NAVIER_STOKES_SOLVER: INC_NAVIER_STOKES_SOLVER_DATASETS,
    SolverType.LINEAR_ELASTIC_SOLVER: LINEAR_ELASTIC_SOLVER_DATASETS,
    SolverType.MMF_SOLVER: MMF_SOLVER_DATASETS,
    SolverType.PULSE_WAVE_SOLVER: PULSE_WAVE_SOLVER_DATASETS,
    SolverType.SHALLOW_WATER_SOLVER: SHALLOW_WATER_SOLVER_DATASETS,
    SolverType.VORTEX_WAVE_INTERACTION_SOLVER: VORTEX_WAVE_INTERACTION_SOLVER_DATASETS
})

def dataset(func):
    dataset_instance = func()  # Execute at import time
    if isinstance(dataset_instance, NekTestDataset):
        DATASETS.append(dataset_instance)

        #add to other groups if necessary
        if dataset_instance.boundary_conditions:
            BOUNDARY_CONDITION_DATASETS.append(dataset_instance)

        if dataset_instance.functions:
            FUNCTIONS_DATASETS.append(dataset_instance)

        if dataset_instance.filters:
            FILTERS_DATASETS.append(dataset_instance)

        _dataset_map[dataset_instance.solver_type].append(dataset_instance)

        logging.debug(f"Registered dataset: {dataset_instance.session}")  # Debug output
    else:
        raise TypeError(f"@dataset expects a function returning NekDataset, got {type(dataset_instance)}")

    return func  # Return the original function

def boundary_condition(func):
    dataset_instance = func()
    logging.debug(dataset_instance)
    if isinstance(dataset_instance,NekTestDataset):
        BOUNDARY_CONDITION_DATASETS.append(dataset_instance)
    else:
        raise TypeError(f"@boundary_condition expects a function returning NekDataset, got {type(dataset_instance)}")

    return func

def geometry_composite_info(func: Optional[Callable[[], NekTestDataset]] = None, *, geom_info: Optional[NekTestGeometryComposite] = None):
    # If used without parentheses, func is provided directly
    if callable(func):
        if geom_info is None:
            raise TypeError("@geometry_composite_info expects geometry_composite_info to be defined when used with arguments")

        dataset_instance = func()  # Execute at import time
        if isinstance(dataset_instance, NekTestDataset) and isinstance(geom_info, NekTestGeometryComposite):
            GEOMETRY_COMPOSITE_DATASETS.append((dataset_instance, geom_info))
            logging.debug(f"Registered dataset: {dataset_instance.session}")  # Debug output
        else:
            raise TypeError(f"@geometry_composite_info expects a function returning NekDataset, got {type(dataset_instance)}")

        return func  # Return the original function

    # If used with arguments, return a decorator
    def decorator(inner_func: Callable[[], NekTestDataset]) -> Callable[[], NekTestDataset]:
        return geometry_composite_info(inner_func, geom_info=geom_info)

    return decorator

def session_expansion_info(func: Optional[Callable[[], NekTestDataset]] = None, *, exp_info: Optional[NekTestSessionExpansion] = None):
    # If used without parentheses, func is provided directly
    if callable(func):
        if exp_info is None:
            raise TypeError("@session_expansion_info expects session_expansion_info to be defined when used with arguments")

        dataset_instance = func()  # Execute at import time
        if isinstance(dataset_instance, NekTestDataset) and isinstance(exp_info, NekTestSessionExpansion):
            SESSION_EXPANSION_DATASETS.append((dataset_instance, exp_info))
            logging.debug(f"Registered dataset: {dataset_instance.session}")  # Debug output
        else:
            raise TypeError(f"@session_expansion_info expects a function returning NekDataset, got {type(dataset_instance)}")

        return func  # Return the original function

    # If used with arguments, return a decorator
    def decorator(inner_func: Callable[[], NekTestDataset]) -> Callable[[], NekTestDataset]:
        return session_expansion_info(inner_func, exp_info=exp_info)

    return decorator
