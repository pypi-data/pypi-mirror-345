from __future__ import annotations
from dataclasses import dataclass
from abc import ABC
from types import MappingProxyType
from typing import Any,Callable
import os

"""
Currently only implemented filters of interest
"""
class NekFilter(ABC):
    output_file: str 

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if 'output_file' not in cls.__annotations__:
            raise TypeError(f"{cls.__name__} must define 'output_file'")
        
@dataclass(frozen=True)
class AerodynamicForcesFilter(NekFilter):
    boundary: str #should be of form B[...]
    output_file: str
    output_frequency: int=1
    pivot_point: tuple[float,float,float]=(0.0,0.0,0.0)

@dataclass(frozen=True)
class CheckpointFilter(NekFilter):
    output_frequency: int
    output_file: str
    output_start_time: float = 0.0
    
@dataclass(frozen=True)
class HistoryPointsFilter(NekFilter):
    output_file: str
    output_frequency: int=1
    output_one_file: bool=True
    
    #homogeneous simulation params
    #need way to check with __post_init at some point
    output_plane: int=-1
    wave_space: bool=False
    points: tuple[float,...]=()
    line: tuple[float,...]=()
    plane: tuple[float,...]=()
    box: tuple[float,...]=()

#currently only used for getting expected file name
#TODO but in future can be expandwed to include more rigorous checks
class NekFilterFactory:
    #allows lazy loading in of filters
    _filter_registry: MappingProxyType[str, Callable[[dict[str, Any], str], NekFilter]] = MappingProxyType({
        "AeroForces": lambda params, session_name: AerodynamicForcesFilter(
            output_file=add_extension_if_needed(params.get("OutputFile", session_name),"fce"),
            output_frequency=int(params.get("OutputFrequency",1)),
            boundary=params.get("Boundary",""),
            pivot_point=tuple(params.get("PivotPoint",(0,0,0)))
        ),#TODO aeorforces should also be capable of parsing the string "0.0 0.0 0.0" -> (0.0,0.0,0.0)
        "Checkpoint": lambda params, session_name: CheckpointFilter(
            output_frequency=int(params.get("OutputFrequency",1)),
            output_file=add_extension_if_needed(params.get("OutputFile", session_name),"chk"),
            output_start_time=float(params.get("OutputStartTime",0.0))
        ),
        "HistoryPoints": lambda params, session_name: HistoryPointsFilter(
            output_file=add_extension_if_needed(params.get("OutputFile",session_name),"his"),
            output_frequency=int(params.get("OutputFrequency",1)),
            output_one_file=bool(params.get("OutputOneFile",False)),
            output_plane=int(params.get("OutputPlane",-1)),
            wave_space=bool(params.get("WaveSpace",False)),
            line=params.get("Line",()),
            plane=params.get("Plane",()),
            box=params.get("Box",())
        )
    })

    @classmethod
    def get_filter(cls, name: str, params: dict[str, Any], session_file: str) -> NekFilter | None:
        """Get the Nektar filter

        Args:
            name (str): Name/Type of filter
            params (dict[str, Any]): Parameters associated with this filter
            session_file (str): Path or name of the sesison file

        Returns:
            NekFilter | None: NekFilter object
        """
        session_name = os.path.basename(session_file).split(".")[0] #remove any extensions at end
        filter_constructor = cls._filter_registry.get(name, None)
        return filter_constructor(params, session_name) if filter_constructor else None

def add_extension_if_needed(name: str, extension: str) -> str:
    """Only adds extension to the name if no extension exists.

    Args:
        name (str): _description_
        extension (str): _description_

    Returns:
        str: _description_
    """
    name_split = name.split(".")
    if len(name_split) > 1:
        return name

    return f"{name}.{extension}"