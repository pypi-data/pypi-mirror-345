import ttkbootstrap as ttk
from ttkbootstrap.constants import *
class ReviewScene(ttk.Frame):
    def __init__(self,parent):
        super().__init__(parent)

        self.rowconfigure(0,weight=1)
        self.rowconfigure(1,weight=1)
        self.rowconfigure(2,weight=1)
        self.columnconfigure(0,weight=1)
        self.columnconfigure(1,weight=1)
        self.columnconfigure(2,weight=1)

        self.placeholder = ttk.Label(
            master=self,
            text="REVIEW HERE",
            font=("TkDefaultFont", 20),
            anchor="center"
        )

        self.placeholder.grid(row=1,column=1,sticky=(NSEW))
        