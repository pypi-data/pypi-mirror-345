import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class Header(ttk.Frame):
    def __init__(self,parent):
        super().__init__(parent)

        self.configure(bootstyle=PRIMARY)
        self.columnconfigure(0,weight=1)

        logo_text = ttk.Label(
            master = self,
            text = "NekUpload",
            font = ("TkDefaultFixed",30),
            bootstyle=(INVERSE, PRIMARY)
        )

        logo_text.grid(row=0,column=0,pady=5)

        description = ttk.Label(
            master = self,
            text = "NekUpload is a utility tool that handles the upload and review process of Nektar++ datasets to AE Datastore",
            font = ("TkDefaultFixed",15),
            bootstyle=(INVERSE, PRIMARY)
        )

        description.grid(row=1,column=0,pady=10)