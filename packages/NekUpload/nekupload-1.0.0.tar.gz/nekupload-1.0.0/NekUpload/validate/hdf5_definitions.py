from abc import ABC, abstractmethod
import h5py
from dataclasses import dataclass,field
from .exceptions import HDF5SchemaExistenceException,HDF5SchemaInconsistentException

class HDF5Definition(ABC):
    @abstractmethod
    def validate(self,h5py_file: h5py.File):
        pass

@dataclass(frozen=True)
class HDF5GroupDefinition(HDF5Definition):
    """Given an HDF5 file, responsible for checking group conforms to correct structure and contains
    the specified attributes. This is not an exclusive check, other non-specified attributes can also be present.
    All exceptions raised from this class are of type HDF5SchemaException or its children.
    """
    path: str
    attributes: list[str] = field(default_factory=list)

    def validate(self,f: h5py.File) -> bool:
        """Checks whether the defined HDF5 group is present and well-defined in the specified HDF5 file

        Args:
            f (h5py.File): HDF5 file

        Raises:
            HDF5SchemaException: _description_
            HDF5SchemaException: _description_
            HDF5SchemaException: _description_

        Returns:
            bool: _description_
        """
        if self.path not in f:
            raise HDF5SchemaExistenceException(f,f"HDF5 schema error, {self.path} is not in file")
        
        group: h5py.Group = f[self.path]
        if not isinstance(group, h5py.Group): 
            raise HDF5SchemaInconsistentException(f,f"HDF5 schema error, {self.path} is a {type(group)},not a group")

        #check attributes exist
        if not set(self.attributes).issubset(group.attrs.keys()):
            missing_attributes = set(self.attributes) - set(group.attrs.keys())
            if missing_attributes:
                raise HDF5SchemaInconsistentException(f, f"HDF5 schema error, missing attributes in {self.path}: {missing_attributes}")
    
        return True

    def __str__(self):
        return self.path

    def get_path(self):
        return self.path

@dataclass(frozen=True)
class HDF5DatasetDefinition(HDF5Definition):
    """Given an HDF5 file, responsible for checking if dataset conforms to schema expectations, such as shape constraints.
        All exceptions raised from this class are of type HDF5SchemaException or its children.
    """
    path: str
    dataset_shape: tuple[int,...] = ()

    def validate(self, f: h5py.File) -> bool:
        """Checks whether the defined HDF5 dataset is present and well-defined in the specified HDF5 file

        Args:
            f (h5py.File): _description_

        Raises:
            HDF5SchemaException: _description_
            HDF5SchemaException: _description_
            HDF5SchemaException: _description_
            HDF5SchemaException: _description_

        Returns:
            bool: _description_
        """
        if self.path not in f:
            raise HDF5SchemaExistenceException(f,f"HDF5 schema error, {self.path} is not in file")
        
        dataset: h5py.Dataset = f[self.path]
        if not isinstance(dataset,h5py.Dataset):
            raise HDF5SchemaInconsistentException(f,f"HDF5 schema error, {self.path} is a {type(dataset)}, not a dataset")
        
        #check dataset shape if it exists
        if self.dataset_shape:
            actual_shape: tuple[int,...] = dataset.shape
            
            #check expected dimension
            if len(actual_shape) != len(self.dataset_shape):
                raise HDF5SchemaInconsistentException(f,f"HDF5 schema error, {self.path} has dataset shape {actual_shape}, but expecting {self.dataset_shape}")
            
            for size,constrained_size in zip(actual_shape,self.dataset_shape):
                # negatives denotes no size restriction on dataset shape
                #so only positive ones are constraints
                if constrained_size >= 0 and constrained_size != size:
                    raise HDF5SchemaInconsistentException(f,f"HDF5 schema error, {self.path} has dataset shape {actual_shape}, but expecting {self.dataset_shape}")
                
        return True
    
    def __str__(self):
        return self.path

    def get_path(self):
        return self.path