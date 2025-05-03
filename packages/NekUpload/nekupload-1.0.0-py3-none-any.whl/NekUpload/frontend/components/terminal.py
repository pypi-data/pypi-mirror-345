import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledText
from ttkbootstrap.constants import *

import logging

class TerminalHandler(logging.Handler):
    """Custom logging handler

    Args:
        logging (_type_): _description_
    """
    def __init__(self, terminal: 'TerminalWidget'):
        super().__init__()
        self.terminal = terminal

    def emit(self, record):
        """Writes a log to the terminal

        Args:
            record (_type_): _description_
        """
        msg = self.format(record)
        level = record.levelname  # Get the log level

        tag = None  # Default tag
        if level == "ERROR":  # Check for ERROR level
            tag = "error"  # Use the "error" tag
        elif level == "WARNING":
            tag = "warn"

        self.terminal.write(msg + "\n", tag=tag)  # Pass the tag to write()
        self.terminal.terminal.update_idletasks()

class TerminalWidget(ttk.Frame):
    """Terminal widget to emulate a terminal

    Args:
        ttk (_type_): _description_
    """
    def __init__(self, parent, height=10, **kwargs):
        """Creates a widget containing a text terminal

        Args:
            parent (ttk.Frame): Parent frame
            height (int, optional): Height of terminal. Defaults to 10.
        """
        super().__init__(parent, **kwargs)

        self.terminal = ScrolledText(
            master=self, 
            wrap=tk.WORD,
            state=tk.DISABLED,
            height=height,
            bootstyle=INFO,
            autohide=True
        )
        self.terminal.pack(fill=tk.BOTH, expand=True)

        # Configure the "error" tag for red text
        self.terminal.text.tag_configure("error", foreground="red")  # Set foreground to red
        self.terminal.text.tag_configure("warn", foreground="blue")  # Set foreground to red

    def write(self, text: str, tag=None):
        """Appends text to the terminal.

        Args:
            text: The text to add.
            tag: An optional tag to apply to the text (for styling).
        """
        self.terminal.text.config(state=tk.NORMAL)
        self.terminal.text.insert(tk.END, text, tag)  # Use the tag here
        self.terminal.text.see(tk.END)
        self.terminal.text.config(state=tk.DISABLED)

    def clear(self):
        """Clears the terminal content."""
        self.terminal.text.config(state=tk.NORMAL)
        self.terminal.text.delete(1.0, tk.END)  # Delete from beginning to end
        self.terminal.text.config(state=tk.DISABLED)

    def tag_configure(self, tag, **kwargs):
        """Configures a tag for styling text."""
        self.terminal.text.tag_configure(tag, **kwargs)