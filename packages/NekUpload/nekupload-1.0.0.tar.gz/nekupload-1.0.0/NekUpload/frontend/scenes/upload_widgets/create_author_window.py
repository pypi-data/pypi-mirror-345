import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
from typing import Callable
from ttkbootstrap.window import Toplevel
from NekUpload.frontend import style_guide

class CreateAuthorPersonWindow(Toplevel):
    """Window containing form to create author (person)

    Args:
        Toplevel (_type_): tkinter Window object
    """
    def __init__(self,root, submit_function: Callable):
        """
        Initializes the CreateAuthorWindow.
        Args:
            root (Tk): The root window of the Tkinter application.
            submit_function (Callable): The function to be called when the submit button is pressed.
        """
        super().__init__(root)

        self.title("Specify Author Information") 
        self.grid_rowconfigure(0,weight=1)
        self.grid_columnconfigure(0,weight=1)

        content_frame = ttk.Frame(self,padding=20)
        content_frame.grid(column=0, row=0, sticky=(N, W, E, S))
        content_frame.grid_rowconfigure(0,weight=1)
        content_frame.grid_columnconfigure(0,weight=1)

        title_label = ttk.Label(content_frame,text="Add Person Info")
        title_label.grid(row=0,column=0)

        ####### Mandatory Info
        mandatory_frame = ttk.Labelframe(content_frame,text="Mandatory Info")
        mandatory_frame.grid(column=0,row=1,sticky=(N,W,E,S))

        #ask for given name
        given_name_label = ttk.Label(mandatory_frame,text="Given Name: ")
        given_name_label.grid(row=1,column=0)
        self._given_name = tk.StringVar()
        self.given_name_entry = ttk.Entry(mandatory_frame,textvariable=self._given_name)
        self.given_name_entry.grid(row=1,column=1)

        #for highlighting missing fields and turning off red when user is inputting
        self.given_name_entry.bind("<FocusOut>",lambda event: style_guide.highlight_mandatory_entry_on_focus_out(self.given_name_entry))
        self.given_name_entry.bind("<FocusIn>",lambda event: style_guide.highlight_mandatory_entry_on_focus_in(self.given_name_entry))

        #ask for last name
        last_name_label = ttk.Label(mandatory_frame,text="Last Name: ")
        last_name_label.grid(row=2,column=0)
        self._last_name = tk.StringVar()
        self.last_name_entry = ttk.Entry(mandatory_frame,textvariable=self._last_name)
        self.last_name_entry.grid(row=2,column=1)

        #for highlighting missing fields and turning off red when user is inputting
        self.last_name_entry.bind("<FocusOut>",lambda event: style_guide.highlight_mandatory_entry_on_focus_out(self.last_name_entry))
        self.last_name_entry.bind("<FocusIn>",lambda event: style_guide.highlight_mandatory_entry_on_focus_in(self.last_name_entry ))

        #########Optional
        #optional arguments: ORCID and affiliations
        optional_frame = ttk.Labelframe(content_frame,text="Optional")
        optional_frame.grid(column=0,row=2,sticky=(N,W,E,S))
        
        affiliation_label = ttk.Label(optional_frame,text="Affiliation(s): ")
        affiliation_label.grid(row=3,column=0)
        self._affiliation = tk.StringVar()
        affiliation_entry = ttk.Entry(optional_frame,textvariable=self._affiliation)
        affiliation_entry.grid(row=3,column=1)

        self._id_type = tk.StringVar()
        id_type_combobox = ttk.Combobox(optional_frame,
                                        textvariable=self._id_type,
                                        values=('ORCID',),
                                        state="readonly")
        id_type_combobox.grid(row=4,column=0)
        self.after(1, lambda: id_type_combobox.current(0))
        self._id = tk.StringVar()
        id_entry = ttk.Entry(optional_frame,textvariable=self._id)
        id_entry.grid(row=4,column=1)

        submit_button = ttk.Button(content_frame,text="Submit",command=lambda: self._on_submit(submit_function))
        submit_button.grid(row=10,column=0,pady=10)

    def _on_submit(self,submit_function: Callable):
        """Wrapper enforcing validation before submit callable is executed

        Args:
            submit_function (Callable): Callable to be executed upon hitting submit
        """
        #enforce mandatory fields
        #don't return immediately so all incomplete fields highlighted together
        is_first_name_bad = False
        is_last_name_bad = False
        if not self._given_name.get():
            style_guide.show_error_in_entry(self.given_name_entry)
            is_first_name_bad = True
        
        if not self._last_name.get():
            style_guide.show_error_in_entry(self.last_name_entry)
            is_last_name_bad = True
        
        is_exit = is_first_name_bad or is_last_name_bad
        #exit now
        if is_exit:
            return
        
        submit_function()

    @property
    def given_name(self):
        return self._given_name.get()

    @property
    def last_name(self):
        return self._last_name.get()

    @property
    def affiliation(self):
        return self._affiliation.get()

    @property
    def id_type(self):
        return self._id_type.get()
    
    @property
    def id(self):
        return self._id.get()

class CreateAuthorOrgWindow(Toplevel):
    """Window containing form to create author (organisation)

    Args:
        Toplevel (_type_): tkinter Window object
    """
    def __init__(self,root, submit_function: Callable):
        """
        Initializes the CreateAuthorWindow.
        Args:
            root (Tk): The root window of the Tkinter application.
            submit_function (Callable): The function to be called when the submit button is pressed.
        """
        super().__init__(root)

        self.title("Specify Author Information") 
        self.grid_rowconfigure(0,weight=1)
        self.grid_columnconfigure(0,weight=1)

        content_frame = ttk.Frame(self,padding=20)
        content_frame.grid(column=0, row=0, sticky=(N, W, E, S))
        content_frame.grid_rowconfigure(0,weight=1)
        content_frame.grid_columnconfigure(0,weight=1)

        title_label = ttk.Label(content_frame,text="Add Organisation Info")
        title_label.grid(row=0,column=0)

        ####### Mandatory Info
        mandatory_frame = ttk.Labelframe(content_frame,text="Mandatory Info")
        mandatory_frame.grid(column=0,row=1,sticky=(N,W,E,S))

        #ask for org name
        name_label = ttk.Label(mandatory_frame,text="Name: ")
        name_label.grid(row=1,column=0)
        self._org_name = tk.StringVar()
        self.name_entry = ttk.Entry(mandatory_frame,textvariable=self._org_name)
        self.name_entry.grid(row=1,column=1)

        #for highlighting missing fields and turning off red when user is inputting
        self.name_entry.bind("<FocusOut>",lambda event: style_guide.highlight_mandatory_entry_on_focus_out(self.name_entry))
        self.name_entry.bind("<FocusIn>",lambda event: style_guide.highlight_mandatory_entry_on_focus_in(self.name_entry))

        #########Optional
        #optional arguments: ORCID and affiliations
        optional_frame = ttk.Labelframe(content_frame,text="Optional")
        optional_frame.grid(column=0,row=2,sticky=(N,W,E,S))
        
        affiliation_label = ttk.Label(optional_frame,text="Affiliation(s): ")
        affiliation_label.grid(row=3,column=0)
        self._affiliation = tk.StringVar()
        affiliation_entry = ttk.Entry(optional_frame,textvariable=self._affiliation)
        affiliation_entry.grid(row=3,column=1)

        self._id_type = tk.StringVar()
        id_type_combobox = ttk.Combobox(optional_frame,
                                        textvariable=self._id_type,
                                        values=('ORCID',),
                                        state="readonly")
        id_type_combobox.grid(row=4,column=0)
        self.after(1, lambda: id_type_combobox.current(0))
        self._id = tk.StringVar()
        id_entry = ttk.Entry(optional_frame,textvariable=id)
        id_entry.grid(row=4,column=1)

        submit_button = ttk.Button(content_frame,text="Submit",command=lambda: self._on_submit(submit_function))
        submit_button.grid(row=10,column=0,pady=10)

    def _on_submit(self,submit_function: Callable):
        """Wrapper enforcing validation before submit callable is executed

        Args:
            submit_function (Callable): Callable to be executed upon hitting submit
        """
        #enforce mandatory fields, show missing field
        if not self._org_name.get():
            style_guide.show_error_in_entry(self.name_entry)
            return
        
        submit_function()

    @property
    def name(self):
        return self._org_name.get()

    @property
    def affiliation(self):
        return self._affiliation.get()

    @property
    def id_type(self):
        return self._id_type.get()
    
    @property
    def id(self):
        return self._id.get()