# NekUpload

**NekUpload** is a Python package designed to streamline the upload and data management process of Nektar++ datasets to AE Datastore. It automates the validation of simulation datasets to ensure consistency and completeness. Furthermore, it extracts relevant parameters embedded within the files, enriching database records with valuable metadata. This aligns with the FAIR principles (Findable, Accessible, Interoperable, Reusable), making your data accessible, understandable and compatible with other NekRDM tools.

# Installation

There are two installation methods. With pip:

```bash
pip install NekUpload
```

Or build from source:

```bash
git clone https://gitlab.nektar.info/shl21/NekUpload.git

#if just need the package as a user
pip install .
#if you want development tools too
pip install .[dev]
```

# User Guide

User guide can be found at https://nekupload.readthedocs.io/en/latest/.