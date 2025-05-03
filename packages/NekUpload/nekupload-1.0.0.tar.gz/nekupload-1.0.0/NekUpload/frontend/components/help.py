import tkinter as tk
from ttkbootstrap.icons import Icon
import ttkbootstrap as ttk
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.constants import *
from typing import Tuple

class HelpNotification(ttk.Label):
    def __init__(self,parent):
        self.img = tk.PhotoImage(data=Icon.question)
        super().__init__(master=parent,
                        image=self.img,
                        anchor="center")

    def add_help_message(self,msg: str,bootstyle: str | Tuple[str,...]=(SECONDARY,INVERSE)):
        ToolTip(self,
                text=msg,
                bootstyle=bootstyle)
