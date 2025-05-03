from __future__ import annotations
from typing import Type, Any
import h5py
import os

from .exceptions import HDF5ReaderException

class HDF5Reader():
    def __init__(self,filename: str, mode: str="r") -> None:
        self.filename = filename
        self.mode = mode
        self.file: h5py.File | None = None
    
    def __enter__(self) -> HDF5Reader:
        try:
            self.file = h5py.File(self.filename,self.mode)
            return self #Return HDF5Reader instance
        except Exception as e:
            raise e
        
    def __exit__(self, exc_type: Type[BaseException] | None, exc_val: BaseException | None, exc_tb: Type[BaseException] | None) -> None:
        if self.file:
            self.file.close()
            self.file = None
    
    def get_keys(self) -> dict[str, str]:
        """
        Recursively retrieves all keys in the HDF5 file and categorizes them as 'GROUP', 'DATASET', or 'ATTRIBUTE'.
        
        Returns:
            dict[str, str]: A dictionary mapping keys (HDF5 paths) to their types.
        """
        if not self.file:
            msg = f"{self.filename} HDF5 file is not open."
            raise HDF5ReaderException(msg)

        key_dict = {}

        def get_keys_helper(group: h5py.Group, prefix: str = "") -> None:
            """Recursive function to traverse HDF5 groups and datasets."""
            for key in group.keys():
                full_key = f"{prefix}/{key}".lstrip("/")  # Ensure proper formatting
                
                obj = group[key]
                if isinstance(obj, h5py.Group):
                    key_dict[full_key] = "GROUP"
                    get_keys_helper(obj, full_key)  # Recurse into sub-groups
                elif isinstance(obj, h5py.Dataset):
                    key_dict[full_key] = "DATASET"

                # Add attributes (only at current level, not recursive)
                for attr_name in obj.attrs.keys():
                    attr_key = f"{full_key}/@{attr_name}"
                    key_dict[attr_key] = "ATTRIBUTE"

        get_keys_helper(self.file)
        return key_dict
    
    def get_dataset(self, dataset_key: str) -> h5py.Dataset | None:
        """
        Reads a dataset from the HDF5 file.

        Args:
            dataset_key (str): The name of the dataset to read.

        Returns:
            Optional[h5py.Dataset]: The dataset object if found, otherwise None.
        """
        if not self.file:
            msg = f"{self.filename} HDF5 file is not open."
            raise HDF5ReaderException(msg)

        try:
            dataset = self.file[dataset_key]
            if isinstance(dataset, h5py.Dataset):
                return dataset
            else:
                msg = f"{dataset_key} is not a dataset."
                raise HDF5ReaderException(msg)
        except KeyError:
            msg = f"Dataset {dataset_key} not found in the file."
            raise HDF5ReaderException(msg)

    def get_attributes(self, key: str) -> dict[str, Any]:
        """
        Retrieves attributes for a given key in the HDF5 file.

        Args:
            key (str): The key for which to retrieve attributes.

        Returns:
            dict[str, Any]: A dictionary of attribute names and their values.
        """
        if not self.file:
            msg = f"{self.filename} HDF5 file is not open."
            raise HDF5ReaderException(msg)

        try:
            obj = self.file[key]
            return {attr_name: obj.attrs[attr_name] for attr_name in obj.attrs.keys()}
        except KeyError:
            msg = f"Key {key} not found in the file."
            raise HDF5ReaderException(msg)

    def dump_to_plain_file(self, target_file_name: str) -> None:
        """Convert HDF5 contents to a formatted plain-text representation."""
        if not self.file:
            raise HDF5ReaderException("HDF5 file is not open.")
        
        output_lines = self._dump_group(self.file)

        with open(target_file_name, "w") as f:
            f.write("\n".join(output_lines))
        print(f"HDF5 content saved to {target_file_name}")

    def summary(self) -> dict[str, str]:
        if not self.file:
            raise HDF5ReaderException("HDF5 file is not open.")

        summary_dict = {
            "File Name": self.filename,
            "File Size": f"{os.path.getsize(self.filename)} bytes",
            "Groups": 0,
            "Datasets": 0,
            "Attributes": 0
        }

        def summary_helper(group: h5py.Group) -> None:
            """Recursive function to count groups, datasets, and attributes."""
            for key, obj in group.items():
                if isinstance(obj, h5py.Group):
                    summary_dict["Groups"] += 1
                    summary_helper(obj)  # Recurse into sub-groups
                elif isinstance(obj, h5py.Dataset):
                    summary_dict["Datasets"] += 1
                
                # Count attributes for both groups and datasets
                summary_dict["Attributes"] += len(obj.attrs)

        summary_helper(self.file)
        return summary_dict

    def get_dtype(self, dataset_path: str) -> str | None:
        """
        Retrieves the data type of a dataset in the HDF5 file.

        Args:
            dataset_path (str): The path to the dataset.

        Returns:
            Optional[str]: The data type of the dataset if found, otherwise None.
        """
        if not self.file:
            msg = f"{self.filename} HDF5 file is not open."
            raise HDF5ReaderException(msg)

        try:
            dataset = self.file[dataset_path]
            if isinstance(dataset, h5py.Dataset):
                return str(dataset.dtype)
            else:
                msg = f"{dataset_path} is not a dataset."
                raise HDF5ReaderException(msg)
        except KeyError:
            msg = f"Dataset {dataset_path} not found in the file."
            raise HDF5ReaderException(msg)

    def get_shape(self, dataset_path: str) -> tuple[int,...] | None:
        """
        Retrieves the shape of a dataset in the HDF5 file.

        Args:
            dataset_path (str): The path to the dataset.

        Returns:
            Optional[tuple]: The shape of the dataset if found, otherwise None.
        """
        if not self.file:
            msg = f"{self.filename} HDF5 file is not open."
            raise HDF5ReaderException(msg)

        try:
            dataset = self.file[dataset_path]
            if isinstance(dataset, h5py.Dataset):
                return dataset.shape
            else:
                msg = f"{dataset_path} is not a dataset."
                raise HDF5ReaderException(msg)
        except KeyError:
            msg = f"Dataset {dataset_path} not found in the file."
            raise HDF5ReaderException(msg)

    def _dump_group(self, group: h5py.Group, indent: int = 0) -> list[str]:
        """Recursively process an HDF5 group and return its content as a string."""
        lines = []
        indent_str = "    " * indent

        # Group name
        lines.append(f"{indent_str} Group: {group.name}")
        if group.attrs:
            lines.append(f"{indent_str} Attributes:")
            for key, value in group.attrs.items():
                lines.append(f"{indent_str}    - {key}: {value}")

        # Iterate through datasets and groups
        for name, item in group.items():
            if isinstance(item, h5py.Group):
                lines.extend(self._dump_group(item, indent + 1))  # Recursive call
            elif isinstance(item, h5py.Dataset):
                lines.append(f"{indent_str} Dataset: {name}")
                if item.attrs:
                    lines.append(f"{indent_str} Attributes:")
                    for key, value in item.attrs.items():
                        lines.append(f"{indent_str}      - {key}: {value}")
                lines.append(f"{indent_str} Shape: {item.shape}")
                lines.append(f"{indent_str} Dtype: {item.dtype}")
                lines.append(f"{indent_str} Data: {item[...]}")

        return lines
