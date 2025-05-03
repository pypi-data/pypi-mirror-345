import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog

class ScrolledListbox(ttk.Frame):
    def __init__(self,parent):
        super().__init__(
            master=parent
        )

        self.rowconfigure(0,weight=1)
        self.columnconfigure(0,weight=1)

        self._listbox = tk.Listbox(self,selectmode=EXTENDED)
        scrollbar_y= ttk.Scrollbar(self,command=self._listbox.yview)
        scrollbar_x = ttk.Scrollbar(self,command=self._listbox.xview,orient=HORIZONTAL)
        self._listbox.config(yscrollcommand=scrollbar_y.set,xscrollcommand=scrollbar_x)
        scrollbar_y.config(command=self._listbox.yview)
        scrollbar_x.config(command=self._listbox.xview)

        self._listbox.grid(row=0,column=0,sticky=(NSEW))
        scrollbar_x.grid(row=1,column=0,sticky=(W,E))
        scrollbar_y.grid(row=0,column=1,sticky=(N,S,W))

    @property
    def listbox(self):
        return self._listbox

class UploadingScrolledListBox(ttk.Labelframe):
    def __init__(self,parent,label_frame_title:str,filetypes: tuple[tuple[str,str]]=(("All Files","*"),)):
        super().__init__(master=parent,text=label_frame_title)
        self.filetypes = filetypes

        self.rowconfigure(0,weight=1)
        self.rowconfigure(1,weight=1)
        self.columnconfigure(0,weight=1)
        self.columnconfigure(1,weight=1)
        
        self._scrolled_listbox = ScrolledListbox(self)
        self._scrolled_listbox.grid(row=1,column=0,columnspan=2,sticky=NSEW)
        self.listbox = self._scrolled_listbox.listbox

        add_button = ttk.Button(
            master=self,
            bootstyle=SUCCESS,
            text="Add Files",
            command=self._select_files_listbox
        )
        add_button.grid(row=0,column=0,sticky=NSEW)

        delete_button = ttk.Button(
            master=self,
            bootstyle=DANGER,
            text="Delete Files",
            command=self._delete_files_listbox
        )
        delete_button.grid(row=0,column=1,sticky=NSEW)

    def _select_files_listbox(self) -> None:
        """Add files selected from filedialogue into listbox, ensuring no duplication
        """
        selected_files = filedialog.askopenfilenames(title="Select Files", filetypes=self.filetypes)

        if selected_files:
            existing_files = set(self.filename_list)  # Use a set for efficient lookup

            for file in selected_files:
                if file not in existing_files:  # Check for duplicates
                    self.listbox.insert(END, file)
                    existing_files.add(file)  # Keep the set updated
                else:
                    print(f"Duplicate file: {file} - not added.")

            print(f"Files: {self.filename_list}")  # Print updated file list
        else:
            print("No Files Selected")

    def _delete_files_listbox(self) -> None:
        """Delete selected files in the listbox
        """
        selection_indices = self.listbox.curselection()

        if selection_indices:
            # 1. Get the items to delete *before* modifying the listbox
            items_to_delete = [self.listbox.get(index) for index in selection_indices]

            # 2. Delete from the listbox (reverse order to prevent issues with shifting indices)
            for index,item in zip(sorted(selection_indices, reverse=True),sorted(items_to_delete,reverse=True)):
                self.listbox.delete(index)

            print(f"Deleted files. Remaining: {self.filename_list}")

    @property
    def filename_list(self) -> list[str]:
        return [self.listbox.get(i) for i in range(self.listbox.size())]
