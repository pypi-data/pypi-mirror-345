import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from typing import Callable, Dict
from pathlib import Path
from ttkbootstrap.scrolled import ScrolledFrame

PATH = Path(__file__).parent.parent / "assets"

class Menu(ScrolledFrame):
    """A menu frame with buttons for various actions."""

    def __init__(self, parent):
        """Initializes the Menu frame."""
        super().__init__(parent, autohide=True,width=150)
        
        self.columnconfigure(0, weight=1)

        self.button_data: Dict[str, Dict] = {
            "INFO": {"row": 0, 
                    "command": None,
                    "icon": ttk.PhotoImage(
                        name="image_icon",
                        file=PATH / "info.png"
                    )},
            "UPLOAD": {"row": 1, 
                    "command": None,
                    "icon": ttk.PhotoImage(
                        name="upload_icon",
                        file=PATH / "upload.png"
                    )},
            "REVIEW": {"row": 2, 
                    "command": None,
                    "icon": ttk.PhotoImage(
                        name="review_icon",
                        file=PATH / "review.png"
                    )},
            "EXPLORE": {"row": 3, 
                    "command": None,
                    "icon": ttk.PhotoImage(
                        name="explore_icon",
                        file=PATH / "explore.png"
                    )},
            "HELP": {"row": 4, 
                    "command": None,
                    "icon": ttk.PhotoImage(
                        name="help_icon",
                        file=PATH / "help.png"
                    )},
            "SETTINGS": {"row": 5,
                    "command": None,
                    "icon": ttk.PhotoImage(
                        name="settings_icon",
                        file=PATH / "settings.png"
                    )}
        }

        self.button_map: Dict[str, ttk.Button] = {}
        self._create_buttons()

    def _create_buttons(self) -> None:
        """Creates the menu buttons."""
        
        for text, data in self.button_data.items():
            button = ttk.Button(
                master=self,
                text=text,
                compound=TOP,
                image=data.get("icon",None),
                bootstyle=(PRIMARY,OUTLINE),
                command=data["command"]
            )
            button.grid(row=data["row"], column=0, padx=0, pady=0, sticky=NSEW)
            self.button_map[text] = button

            button.bind("<Enter>",lambda event, button=button: button.config(cursor="hand2"))
            button.bind("<Leave>",lambda event, button=button: button.config(cursor=""))

    def add_link_to_button(self, button_text: str, on_click_command: Callable) -> None:
        """Adds a click command to a button.

        Args:
            button_text (str): The text of the button to link.
            on_click_command (Callable): The function to execute on click.
        """
        if button_text in self.button_map:
            self.button_map[button_text].config(command=on_click_command)
        else:
            print(f"Warning: Button '{button_text}' not found.")