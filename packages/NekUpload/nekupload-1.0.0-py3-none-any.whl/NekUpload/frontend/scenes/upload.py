import ttkbootstrap as ttk
import tkinter as tk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame
from .upload_widgets.geometry import UploadGeometryFrame
from .upload_widgets.basic import UploadInfoFrame
from .upload_widgets.files import FileUploadFrame
from NekUpload.frontend.components.settings_manager import SettingsManager
from NekUpload.metadata.metadata import InvenioMetadata
from NekUpload.metadata.identifier import Identifier,IdentifierType
from NekUpload.metadata.user import InvenioOrgInfo,InvenioPersonInfo
import logging
from NekUpload.manager import NekManager,GeometryManager,SessionManager,OutputManager
from NekUpload.upload.invenio_db import InvenioRDM
from NekUpload.frontend import style_guide
from NekUpload.metadata.data_types import ResourceType
from NekUpload.NekData.data_type import SolverType

class UploadScene(ScrolledFrame):
    def __init__(self,root,parent,setting_manager: SettingsManager):
        super().__init__(parent,autohide=True)

        self.root = root
        self.setting_manager = setting_manager#contains settings data

        self.rowconfigure(0,weight=1)
        self.rowconfigure(1,weight=1)
        self.rowconfigure(2,weight=1)
        self.columnconfigure(0,weight=1)

        about_section: ttk.Frame = self._add_upload_info_section(self)
        about_section.grid(row=0,column=0,sticky=(NSEW))

        self.basic_info_section= UploadInfoFrame(self,self,self.setting_manager)
        self.basic_info_section.grid(row=1,column=0,sticky=NSEW,padx=10,pady=5)
        self.geometry_section = UploadGeometryFrame(self)
        self.geometry_section.grid(row=2,column=0,sticky=(NSEW),padx=10,pady=5)
        self.file_section = FileUploadFrame(self)
        self.file_section.grid(row=5,column=0,sticky=(NSEW),padx=10,pady=5)

        self.bind("<Configure>", self.update_wraplength)

        #upload button
        submit_button = ttk.Button(
            master=self,
            bootstyle=PRIMARY,
            text="Upload Datasets",
            command=self._upload_datasets
        )
        submit_button.grid(row=10,column=0,columnspan=10,sticky=NSEW,padx=10,pady=5)

    def update_wraplength(self, event):
        # Dynamically set the wraplength based on the width of the parent frame
        # Subtract a little for padding and margin
        self.upload_description.config(wraplength=event.width - 20)
        pass

    def _add_upload_info_section(self,parent) -> ttk.Frame:

        frame = ttk.Frame(master=parent)

        # Create the label for the title
        self.upload_info_label = ttk.Label(
            master=frame,
            text="Uploading Nektar++ Datasets",
            font=("TkDefaultFont", 20, "bold", "underline"),
            anchor="w",
            bootstyle=PRIMARY
        )
        self.upload_info_label.grid(row=0, column=0, pady=5, sticky=W)

        # Create the description label
        self.upload_description = ttk.Label(
            master=frame,
            text=("A Nektar++ dataset consists of: \n\n"
                " - Geometry Files\n"
                " - Input Files\n"
                " - Output Files\n"
                "\n"
                "There are currently two ways of uploading. The traditional way is that you have all the geometry files, "
                "input files and output files to be uploaded. Another way is that the geometry file already exists in the "
                "database, and you wish to link your input and ouptut files against it. This prevents repeated instances of "
                "same geometry file."),
            font=("TKDefaultFont", 12),
            anchor="w",
            justify="left",
        )
        self.upload_description.grid(row=1, column=0, pady=10, sticky="nsew")

        return frame

    def _check_dataset_inputs(self) -> bool:
        """Check all entry data is present, if not change style

        Returns:
            bool: _description_
        """

        is_error = True

        #check geometry widgets
        if not self.geometry_section.geometry_dataset_title:
            is_error = False

        if not self.geometry_section.geometry_file_name:
            is_error = False

        self.geometry_section.add_error_style_to_mandatory_entries()

        #check file IO widgets
        if not self.file_section.dataset_title:
            is_error = False

        if not self.file_section.session_file_name:
            is_error = False
        
        if not self.file_section.output_file_name:
            is_error = False

        self.file_section.add_error_style_to_mandatory_entries()

        return is_error
    
    def _upload_datasets(self):
        try:
            is_all_info_entered = True

            if not self.basic_info_section.author_list:
                logging.error("No authors entered. Please add authors.")
                is_all_info_entered = False

            if not self._check_dataset_inputs():
                logging.error("Missing mandatory dataset inputs. Please see red highlighted entries.")
                is_all_info_entered = False

            #exit if mandatory inputs not filled
            if not is_all_info_entered:
                return

            logging.info("UPLOADING...")

            #get general info
            publication_date: str = self.basic_info_section.publication_date_iso
            COMMUNITY_SLUG: str = self.basic_info_section.community_slug
            URL: str = self.setting_manager.database_url

            #ASSIGN USERS
            author_list: list[InvenioOrgInfo | InvenioPersonInfo] = []
            for author in self.basic_info_section.author_list:
                author_info: InvenioOrgInfo | InvenioPersonInfo = None
                
                if author["type"] == "personal":
                    given_name = author["given_name"]
                    last_name = author["last_name"]
                    author_info = InvenioPersonInfo(given_name,last_name)
                elif author["type"] == "organizational":
                    name = author["name"]
                    author_info = InvenioOrgInfo(name)

                if author["id"] != "":
                    mapping = {"ORCID" : IdentifierType.ORCID}
                    id = Identifier(author["id"],mapping[author["id_type"]])
                    author_info.add_identifier(id)

                #also affiliations, but not supported in backend for now
                author_list.append(author_info)

            #titles for each dataset
            geometry_title = self.geometry_section.geometry_dataset_title
            input_title = self.file_section.dataset_title
            output_title = self.file_section.dataset_title

            #create metadata for each one
            metadata_geometry = InvenioMetadata(geometry_title,publication_date,author_list,ResourceType.PHYSICAL_OBJECT)
            metadata_input = InvenioMetadata(input_title,publication_date,author_list,ResourceType.DATASET)
            metadata_output = InvenioMetadata(output_title,publication_date,author_list,ResourceType.DATASET)

            metadata_geometry.add_publisher("NekRDM")
            metadata_input.add_publisher("NekRDM")
            metadata_output.add_publisher("NekRDM")

            if geometry_description := self.geometry_section.geometry_description:
                metadata_geometry.add_description(geometry_description)

            #get files
            geometry_file: str = self.geometry_section.geometry_file_name
            session_file: str = self.file_section.session_file_name
            output_file: str = self.file_section.output_file_name

            boundary_condition_file_list: list[str] = self.file_section.boundary_condition_file_name_list
            function_file_list: list[str] = self.file_section.function_file_name_list
            input_extra_file_list: list[str] = self.file_section.input_supporting_filename_list

            geometry_optional_files: list[str] = self.geometry_section.geometry_optional_files
            chk_file_list: list[str] = self.file_section.checkpoint_filename_list
            filter_file_list: list[str] = self.file_section.filter_filename_list
            output_extra_file_list: list[str] = self.file_section.output_supporting_filename_list

            solver_type: SolverType = self.file_section.solver_type

            #use geometry title for now
            extra_input_files = boundary_condition_file_list + function_file_list + input_extra_file_list 
            geometry_uploader = GeometryManager(geometry_file,geometry_optional_files,metadata_geometry,InvenioRDM())
            input_uploader = SessionManager(session_file,extra_input_files,metadata_input,InvenioRDM())
            output_uploader = OutputManager(output_file,
                                            output_chk_files=chk_file_list,
                                            filter_files=filter_file_list,
                                            supporting_files=output_extra_file_list,
                                            metadata=metadata_output,
                                            uploader=InvenioRDM())

            manager = NekManager(geometry_uploader,input_uploader,output_uploader)

            logging.info("Starting validation...")
            manager.validate(solver_type)
            logging.info("Successful Validation")
            manager.optional_validation()
            manager.execute_upload(URL,
                            self.setting_manager.token,
                            COMMUNITY_SLUG)
        except Exception as e:
            logging.error(e)