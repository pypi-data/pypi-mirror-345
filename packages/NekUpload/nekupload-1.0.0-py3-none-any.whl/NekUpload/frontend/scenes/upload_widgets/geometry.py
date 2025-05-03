import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import filedialog
from NekUpload.frontend.components.help import HelpNotification
from NekUpload.frontend import style_guide
from ttkbootstrap.scrolled import ScrolledText
from NekUpload.frontend.components.scrollbox import ScrolledListbox
from typing import List

class UploadGeometryFrame(ttk.LabelFrame):
    def __init__(self,parent):
        super().__init__(
            master=parent,
            text="Geometry",
            bootstyle=DANGER,
            padding=10
            )

        self.columnconfigure(0,weight=1)
        self.columnconfigure(1,weight=1)
        self.rowconfigure(0,weight=1)
        self.rowconfigure(1,weight=1)

        label = ttk.Label(
            master=self,
            text="Upload all geometry related files here.",
            font=("TKDefaultFont", 12),
            anchor="w",
            justify="left",
        )
        label.grid(row=0,column=0,columnspan=2,pady=2,sticky=(NSEW))

        n = ttk.Notebook(self,bootstyle=SECONDARY)
        n.grid(row=1,column=0,columnspan=2,sticky=NSEW)
        
        f1: ttk.Frame = self._upload_geometry(n)
        f2: ttk.Frame = self._link_geometry_to_existing_record(n)

        n.add(f1,text="Upload from Source")
        n.add(f2,text="Link to Existing Record")
    
    def _link_geometry_to_existing_record(self,parent) -> ttk.Frame:
        frame = ttk.Frame(master=parent)

        todo = ttk.Label(master=frame,
                        text="TBC",
                        bootstyle=DANGER,
                        anchor="w")
        todo.grid(row=0,column=0,sticky=NSEW)

        return frame
    
    def _upload_geometry(self,parent) -> ttk.Frame:
        frame = ttk.Frame(master=parent)

        frame.rowconfigure(0,weight=1)
        frame.rowconfigure(1,weight=1)
        frame.columnconfigure(0,weight=1)
        frame.columnconfigure(1,weight=1)

        geometry_file_frame: ttk.Labelframe = self._geometry_mandatory_info(frame)
        geometry_file_frame.grid(row=0,column=0,sticky=NSEW)
        geometry_optional_data_frame = self._optional_geometry_upload_frame(frame)
        geometry_optional_data_frame.grid(row=1,column=0,columnspan=2,sticky=NSEW)

        return frame
    
    def _geometry_mandatory_info(self,parent) -> ttk.Labelframe:
        geometry_file_frame= ttk.Labelframe(
            master=parent,
            text="Mandatory"
        )
        geometry_file_frame.columnconfigure(0,weight=1)
        geometry_file_frame.columnconfigure(1,weight=3)
        geometry_file_frame.columnconfigure(2,weight=1)
        geometry_file_frame.columnconfigure(3,weight=1)

        ################################
        # Ask for title
        title_label = ttk.Label(
            master=geometry_file_frame,
            text="Geometry Title: "
        )
        title_label.grid(row=0,column=0,sticky=NSEW)
        
        self._geometry_title = tk.StringVar()
        self.geometry_title_entry = ttk.Entry(
            master=geometry_file_frame,
            textvariable=self._geometry_title,
        )
        self.geometry_title_entry.grid(row=0,column=1,sticky=NSEW)
        
        #for highlighting missing fields and turning off red when user is inputting
        self.geometry_title_entry.bind("<FocusOut>",lambda event: style_guide.highlight_mandatory_entry_on_focus_out(self.geometry_title_entry))
        self.geometry_title_entry.bind("<FocusIn>",lambda event: style_guide.highlight_mandatory_entry_on_focus_in(self.geometry_title_entry))

        ################################
        # Ask for geometry file
        geometry_file_label = ttk.Label(
            master=geometry_file_frame,
            text="Select Geometry File: "
        )
        geometry_file_label.grid(row=1,column=0,sticky=NSEW)

        self._geometry_file = tk.StringVar()
        self.geometry_file_entry = ttk.Entry(
            master=geometry_file_frame,
            textvariable=self._geometry_file,
        )
        self.geometry_file_entry.grid(row=1,column=1,sticky=NSEW)

        #for highlighting missing fields and turning off red when user is inputting
        self.geometry_file_entry.bind("<FocusOut>",lambda event: style_guide.highlight_mandatory_entry_on_focus_out(self.geometry_file_entry))
        self.geometry_file_entry.bind("<FocusIn>",lambda event: style_guide.highlight_mandatory_entry_on_focus_in(self.geometry_file_entry))


        def browse_file():
            file_path = filedialog.askopenfilename(
                title="Select Geometry File",
                filetypes=(("Geometry Files",".nekg"),)
            )
            self._geometry_file.set(file_path)

        browse = ttk.Button(
            master=geometry_file_frame,
            text="Browse Files",
            command=browse_file
        )
        browse.grid(row=1,column=2,sticky=NSEW)

        help_logo:ttk.Label = HelpNotification(geometry_file_frame)
        help_logo.add_help_message("This will be the title of the geometry record")
        help_logo2:ttk.Label = HelpNotification(geometry_file_frame)
        help_logo2.add_help_message("Only HDF5 formatted geometry files are accepted")
        help_logo.grid(row=0, column=3, sticky=NSEW)
        help_logo2.grid(row=1, column=3, sticky=NSEW)

        return geometry_file_frame
    
    #OPTIONAL INFO
    def _optional_geometry_upload_frame(self,parent) -> ttk.Labelframe:
        frame = ttk.Labelframe(
            master=parent,
            bootstyle=DEFAULT,
            text="Optional"
        )

        frame.columnconfigure(0,weight=1)
        frame.columnconfigure(1,weight=1)
        frame.columnconfigure(2,weight=1)
        frame.columnconfigure(3,weight=1)
        frame.columnconfigure(4,weight=1)
        frame.columnconfigure(5,weight=1)

        label = ttk.Label(
            master=frame,
            bootstyle=DEFAULT,
            text="Description: ",
            anchor="w"
        )
        label.grid(row=0,column=0,sticky=EW)

        self._description_text = ScrolledText(
            master=frame,
            autohide=True,
            bootstyle=DEFAULT
        )
        self._description_text.text.configure(height=10)
        self._description_text.grid(row=1,column=0,columnspan=3,sticky=NSEW)

        optional_files = ttk.Label(
            master=frame,
            bootstyle=DEFAULT,
            text="Optional Files: ",
            anchor="w"
        )
        optional_files.grid(row=0,column=3,sticky=EW)

        optional_files_button = ttk.Button(
            master=frame,
            bootstyle=SUCCESS,
            text="Browse Files",
            command=self._select_files_listbox
        )
        optional_files_button.grid(row=0,column=4,padx=5,sticky=NSEW)

        optional_files_delete_button = ttk.Button(
            master=frame,
            bootstyle=(DANGER),
            text="Delete Files",
            command=self._delete_files_listbox
        )
        optional_files_delete_button.grid(row=0,column=5,padx=5,sticky=NSEW)

        #have a listbox to specify the creation
        self.optional_files_listbox_frame = ScrolledListbox(frame)
        self.optional_files_listbox = self.optional_files_listbox_frame.listbox
        self.optional_files_listbox_frame.grid(row=1,column=3,columnspan=3,rowspan=2,sticky=NSEW)

        return frame

    @property
    def geometry_file_name(self):
        return self._geometry_file.get()
    
    @property
    def geometry_dataset_title(self):
        return self._geometry_title.get()
    
    @property
    def geometry_description(self):
        return self._description_text.text.get("1.0", "end-1c")
    
    @property
    def geometry_optional_files(self):
        return [self.optional_files_listbox.get(i) for i in range(self.optional_files_listbox.size())]
    
    def add_error_style_to_mandatory_entries(self):
        if not self.geometry_file_entry.get():
            style_guide.show_error_in_entry(self.geometry_file_entry)

        if not self.geometry_title_entry.get():
            style_guide.show_error_in_entry(self.geometry_title_entry)

    def _select_files_listbox(self) -> None:
        """Add files selected from filedialogue into listbox, ensuring no duplication
        """
        filetype = ("All Files","*")
        selected_files = filedialog.askopenfilenames(title="Select Files", filetypes=(filetype,))

        if selected_files:
            existing_files = set(self.geometry_optional_files)  # Use a set for efficient lookup

            for file in selected_files:
                if file not in existing_files:  # Check for duplicates
                    self.optional_files_listbox.insert(END, file)
                    existing_files.add(file)  # Keep the set updated
                else:
                    print(f"Duplicate file: {file} - not added.")

            print(f"Files: {self.geometry_optional_files}")  # Print updated file list
        else:
            print("No Files Selected")

    def _delete_files_listbox(self) -> None:
        """Delete selected files in the listbox
        """
        selection_indices = self.optional_files_listbox.curselection()

        if selection_indices:
            # 1. Get the items to delete *before* modifying the listbox
            items_to_delete = [self.optional_files_listbox.get(index) for index in selection_indices]

            # 2. Delete from the listbox (reverse order to prevent issues with shifting indices)
            for index,item in zip(sorted(selection_indices, reverse=True),sorted(items_to_delete,reverse=True)):
                self.optional_files_listbox.delete(index)

            print(f"Deleted files. Remaining: {self.geometry_optional_files}")
