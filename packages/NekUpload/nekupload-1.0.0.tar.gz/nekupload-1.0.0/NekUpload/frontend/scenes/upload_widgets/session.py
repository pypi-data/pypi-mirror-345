import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import filedialog
from NekUpload.frontend.components.help import HelpNotification
from NekUpload.frontend import style_guide

class UploadSessionFrame(ttk.LabelFrame):
    def __init__(self,parent):
        super().__init__(
            master=parent,
            text="Session",
            bootstyle=DANGER,
            padding=10
            )

        self.columnconfigure(0,weight=1)
        self.columnconfigure(1,weight=1)
        self.rowconfigure(0,weight=1)
        self.rowconfigure(1,weight=1)

        label = ttk.Label(
            master=self,
            text="Upload all input related files here.",
            font=("TKDefaultFont", 12),
            anchor="w",
            justify="left",
        )
        label.grid(row=0,column=0,columnspan=2,pady=2,sticky=(NSEW))

        n = ttk.Notebook(self,bootstyle=SECONDARY)
        n.grid(row=1,column=0,columnspan=2,sticky=NSEW)
        
        f1: ttk.Frame = self._upload_session(n)

        n.add(f1,text="Upload from Source")
    
    def _upload_session(self,parent) -> ttk.Frame:
        frame = ttk.Frame(master=parent)

        frame.rowconfigure(0,weight=1)
        frame.rowconfigure(1,weight=1)
        frame.columnconfigure(0,weight=1)
        frame.columnconfigure(1,weight=1)
        frame.columnconfigure(2,weight=1)

        session_file_frame: ttk.Labelframe = self._session_mandatory_info(frame)
        session_file_frame.grid(row=0,column=0,sticky=NSEW)

        return frame
    
    def _session_mandatory_info(self,parent) -> ttk.Labelframe:
        session_file_frame= ttk.Labelframe(
            master=parent,
            text="Mandatory"
        )
        session_file_frame.columnconfigure(0,weight=1)
        session_file_frame.columnconfigure(1,weight=3)
        session_file_frame.columnconfigure(2,weight=1)
        session_file_frame.columnconfigure(3,weight=1)

        ################################
        # Ask for title
        title_label = ttk.Label(
            master=session_file_frame,
            text="Session Title: "
        )
        title_label.grid(row=0,column=0,sticky=NSEW)
        
        self._session_title = tk.StringVar()
        self.session_title_entry = ttk.Entry(
            master=session_file_frame,
            textvariable=self._session_title,
        )
        self.session_title_entry.grid(row=0,column=1,sticky=NSEW)

        #for highlighting missing fields and turning off red when user is inputting
        self.session_title_entry.bind("<FocusOut>",lambda event: style_guide.highlight_mandatory_entry_on_focus_out(self.session_title_entry))
        self.session_title_entry.bind("<FocusIn>",lambda event: style_guide.highlight_mandatory_entry_on_focus_in(self.session_title_entry))

        ################################
        # Ask for session file
        session_file_label = ttk.Label(
            master=session_file_frame,
            text="Select Session File: "
        )
        session_file_label.grid(row=1,column=0,sticky=NSEW)

        self._session_file = tk.StringVar()
        self.session_file_entry = ttk.Entry(
            master=session_file_frame,
            textvariable=self._session_file,
        )
        self.session_file_entry.grid(row=1,column=1,sticky=NSEW)

        #for highlighting missing fields and turning off red when user is inputting
        self.session_file_entry.bind("<FocusOut>",lambda event: style_guide.highlight_mandatory_entry_on_focus_out(self.session_file_entry))
        self.session_file_entry.bind("<FocusIn>",lambda event: style_guide.highlight_mandatory_entry_on_focus_in(self.session_file_entry))

        def browse_file():
            file_path = filedialog.askopenfilename(
                title="Select Session File",
                filetypes=(("Session Files",".xml"),)
            )
            self._session_file.set(file_path)

        browse = ttk.Button(
            master=session_file_frame,
            text="Browse Files",
            command=browse_file
        )
        browse.grid(row=1,column=2,sticky=NSEW)

        help_logo:ttk.Label = HelpNotification(session_file_frame)
        help_logo.add_help_message("This will be the title of the session record")
        help_logo2:ttk.Label = HelpNotification(session_file_frame)
        help_logo2.add_help_message("Only XML formatted session files are accepted")
        help_logo.grid(row=0, column=3, sticky=NSEW)
        help_logo2.grid(row=1, column=3, sticky=NSEW)

        return session_file_frame
    
    @property
    def session_file_name(self):
        return self._session_file.get()
    
    @property
    def session_dataset_title(self):
        return self._session_title.get()
    
    def add_error_style_to_mandatory_entries(self):
        if not self.session_file_entry.get():
            print("H")
            style_guide.show_error_in_entry(self.session_file_entry)

        if not self.session_title_entry.get():
            style_guide.show_error_in_entry(self.session_title_entry)