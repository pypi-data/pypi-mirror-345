import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import filedialog

from NekUpload.frontend.components.help import HelpNotification
from NekUpload.frontend.components.scrollbox import ScrolledListbox,UploadingScrolledListBox
from NekUpload.frontend import style_guide
from NekUpload.NekData.data_type import SolverType

class FileUploadFrame(ttk.LabelFrame):
    def __init__(self,parent):
        super().__init__(
            master=parent,
            text="Simulation Dataset (Excluding Geometry)",
            bootstyle=DANGER,
            padding=10
            )

        self.columnconfigure(0,weight=1)
        self.columnconfigure(1,weight=1)
        self.rowconfigure(0,weight=1)
        self.rowconfigure(1,weight=1)
        self.rowconfigure(2,weight=1)
        self.rowconfigure(3,weight=1)
        self.rowconfigure(4,weight=1)

        label = ttk.Label(
            master=self,
            text="Upload all Nektar session files and output files related files here.",
            font=("TKDefaultFont", 12),
            anchor="w",
            justify="left",
        )
        label.grid(row=0,column=0,columnspan=2,pady=2,sticky=(NSEW))

        basic_info_frame = self.basic_info_block()
        basic_info_frame.grid(row=1,column=0,sticky=NSEW)

        n = ttk.Notebook(self,bootstyle=SECONDARY)
        n.grid(row=2,column=0,columnspan=4,sticky=NSEW)

        f1: ttk.Frame = self._upload_input_frame(n)
        f2: ttk.Frame = self._upload_output_frame(n)
        n.add(f1,text="Inputs")
        n.add(f2,text="Outputs")
        """f2: ttk.Frame = self._link_geometry_to_existing_record(n)

        n.add(f2,text="Link to Existing Record")
        """
    
    def basic_info_block(self) -> ttk.Frame:
        frame = ttk.Frame(master=self)
        frame.columnconfigure(0,weight=1)
        frame.columnconfigure(1,weight=1)
        frame.rowconfigure(0,weight=1)
        frame.rowconfigure(1,weight=1)

        #title of dataset
        title_label = ttk.Label(master=frame,text="Dataset Title: ",bootstyle=PRIMARY,padding=10,anchor="w")
        title_label.grid(row=0,column=0,sticky=W)
        self._title = tk.StringVar()
        self.title_entry = ttk.Entry(master=frame,textvariable=self._title,bootstyle=PRIMARY)
        self.title_entry.grid(row=0,column=1,sticky=EW)
        
        #combobox for solver type
        solver_label = ttk.Label(master=frame,text="Solver Type: ",bootstyle=PRIMARY,padding=10,anchor="w")
        solver_label.grid(row=1,column=0,sticky=W)
        solver_type_list: list[str] = [solver.value for solver in SolverType]
        self.solver_type_combobox = ttk.Combobox(master=frame,
                                                values=solver_type_list,
                                                state="readonly")
        self.solver_type_combobox.set(solver_type_list[0])#set default
        self.solver_type_combobox.grid(row=1,column=1,sticky=EW)

        # Event bindings
        self.title_entry.bind(
            "<FocusOut>",
            lambda event: style_guide.highlight_mandatory_entry_on_focus_out(self.title_entry)
        )
        self.title_entry.bind(
            "<FocusIn>",
            lambda event: style_guide.highlight_mandatory_entry_on_focus_in(self.title_entry)
        )
        return frame

    def _upload_input_frame(self, parent) -> ttk.Frame:
        frame = ttk.Frame(master=parent)
        
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=3)
        frame.columnconfigure(2, weight=1)
        frame.columnconfigure(3, weight=1)

        descriptor = ttk.Label(
            frame,
            text=(
                "Files such as session file, boundary condition files and "
                "function forcing files should be uploaded here. Note that "
                "although geometry file is part of input, it is uploaded separately."
            )
        )
        descriptor.grid(row=0, column=0, columnspan=4, sticky=W)  # Span all columns

        # Ask for session file
        session_file_label = ttk.Label(
            master=frame,
            text="Select Session File: ",
            justify="left"
        )
        session_file_label.grid(row=1, column=0, sticky=W)

        self._session_file = tk.StringVar()
        self.session_file_entry = ttk.Entry(
            master=frame,
            textvariable=self._session_file,
        )
        self.session_file_entry.grid(row=1, column=1, sticky=EW)

        # Event bindings
        self.session_file_entry.bind(
            "<FocusOut>",
            lambda event: style_guide.highlight_mandatory_entry_on_focus_out(self.session_file_entry)
        )
        self.session_file_entry.bind(
            "<FocusIn>",
            lambda event: style_guide.highlight_mandatory_entry_on_focus_in(self.session_file_entry)
        )

        def browse_file():
            file_path = filedialog.askopenfilename(
                title="Select Session File",
                filetypes=(("Session File",(".xml",)),)
            )
            self._session_file.set(file_path)

        browse = ttk.Button(
            master=frame,
            text="Browse Files",
            command=browse_file
        )
        browse.grid(row=1,column=2,sticky=NSEW)

        help_logo:ttk.Label = HelpNotification(frame)
        help_logo.add_help_message("XML session file expected here. Other files should be placed under supporting")
        help_logo.grid(row=1,column=4,sticky=W)
        
        ######
        extra_files_frame = ttk.Frame(master=frame)
        extra_files_frame.grid(row=2,column=0,columnspan=4,sticky=NSEW)
        extra_files_frame.columnconfigure(0,weight=1)
        extra_files_frame.columnconfigure(1,weight=1)
        extra_files_frame.columnconfigure(2,weight=1)
        extra_files_frame.rowconfigure(0,weight=1)

        self.boundary_conditions_frame = UploadingScrolledListBox(extra_files_frame,"Boundary Conditions Files",(
            ("Boundary Conditions Files",("*.bc","*.bce")),("Other Files",("*"))))
        self.boundary_conditions_frame.grid(row=0,column=0,sticky=NSEW)

        self.function_frame = UploadingScrolledListBox(extra_files_frame,"Function Files",(("Function File","*"),))
        self.function_frame.grid(row=0,column=1,sticky=NSEW)

        self.input_supporting_files_frame = UploadingScrolledListBox(extra_files_frame,"Supporting Files")
        self.input_supporting_files_frame.grid(row=0,column=2,sticky=NSEW)

        return frame

    def _upload_output_frame(self, parent) -> ttk.Frame:
        frame = ttk.Frame(master=parent)
        
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=3)
        frame.columnconfigure(2, weight=1)
        frame.columnconfigure(3, weight=1)

        descriptor = ttk.Label(
            frame,
            text=(
                "Files such as output field file, output checkpoint files,"
                "history files and other outputted files should be uploaded here."
                "If you have other images and pdfs that will support the record," \
                "please also upload under the supporting section."
            )
        )
        descriptor.grid(row=0, column=0, columnspan=4, sticky=W)  # Span all columns

        # Ask for session file
        output_file_label = ttk.Label(
            master=frame,
            text="Select Session File: ",
            justify="left"
        )
        output_file_label.grid(row=1, column=0, sticky=W)

        self._output_file = tk.StringVar()
        self.output_file_entry = ttk.Entry(
            master=frame,
            textvariable=self._output_file,
        )
        self.output_file_entry.grid(row=1, column=1, sticky=EW)

        # Event bindings
        self.output_file_entry.bind(
            "<FocusOut>",
            lambda event: style_guide.highlight_mandatory_entry_on_focus_out(self.output_file_entry)
        )
        self.output_file_entry.bind(
            "<FocusIn>",
            lambda event: style_guide.highlight_mandatory_entry_on_focus_in(self.output_file_entry)
        )

        def browse_file():
            file_path = filedialog.askopenfilename(
                title="Select Output File",
                filetypes=(("Output File",(".fld",)),)
            )
            self._output_file.set(file_path)

        browse = ttk.Button(
            master=frame,
            text="Browse Files",
            command=browse_file
        )
        browse.grid(row=1,column=2,sticky=NSEW)

        help_logo:ttk.Label = HelpNotification(frame)
        help_logo.add_help_message("HDF5 output file expected here. Other files should be placed under supporting")
        help_logo.grid(row=1,column=4,sticky=W)

        ###########
        extra_files_frame = ttk.Frame(master=frame)
        extra_files_frame.grid(row=2,column=0,columnspan=4,sticky=NSEW)
        extra_files_frame.columnconfigure(0,weight=1)
        extra_files_frame.columnconfigure(1,weight=1)
        extra_files_frame.columnconfigure(2,weight=1)
        extra_files_frame.rowconfigure(0,weight=1)

        self.checkpoint_files_frame = UploadingScrolledListBox(extra_files_frame,"Checkpoint Files",(("Checkpoint Files","*.chk"),))
        self.checkpoint_files_frame.grid(row=0,column=0,sticky=NSEW)

        self.filter_files_frame = UploadingScrolledListBox(extra_files_frame,"Filter Files",(
                            ("AeroForces","*.fce"),("History","*.his"),
                            ("Other Filter Files","*")))
        self.filter_files_frame.grid(row=0,column=1,sticky=NSEW)

        self.output_supporting_files_frame = UploadingScrolledListBox(extra_files_frame,"Supporting Files")
        self.output_supporting_files_frame.grid(row=0,column=2,sticky=NSEW)

        return frame

    def add_error_style_to_mandatory_entries(self):
        if not self.title_entry.get():
            style_guide.show_error_in_entry(self.title_entry)

        if not self.session_file_entry.get():
            style_guide.show_error_in_entry(self.session_file_entry)

        if not self.output_file_entry.get():
            style_guide.show_error_in_entry(self.output_file_entry)

    @property
    def session_file_name(self) -> str:
        return self._session_file.get()

    @property
    def output_file_name(self) -> str:
        return self._output_file.get()

    @property
    def dataset_title(self) -> str:
        return self._title.get()

    @property
    def checkpoint_filename_list(self) -> list[str]:
        return self.checkpoint_files_frame.filename_list

    @property
    def filter_filename_list(self) -> list[str]:
        return self.filter_files_frame.filename_list

    @property
    def output_supporting_filename_list(self) -> list[str]:
        return self.output_supporting_files_frame.filename_list

    @property
    def boundary_condition_file_name_list(self) -> list[str]:
        return self.boundary_conditions_frame.filename_list
    
    @property
    def function_file_name_list(self) -> list[str]:
        return self.function_frame.filename_list
    
    @property
    def input_supporting_filename_list(self) -> list[str]:
        return self.input_supporting_files_frame.filename_list

    @property
    def solver_type(self) -> SolverType:
        return SolverType(self.solver_type_combobox.get())