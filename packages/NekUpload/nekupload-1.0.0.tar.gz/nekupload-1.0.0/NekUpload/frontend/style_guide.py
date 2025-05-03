from ttkbootstrap import Style
from ttkbootstrap.constants import DANGER, DEFAULT
from ttkbootstrap.widgets import Entry

def get_styles() -> Style:
    """Get all defined styling using ttkbootstrap.

    Returns:
        Style: Bootstrap style object
"""
    style = Style()
    style.configure("Error.TEntry",
                    fieldbackground="lightcoral",  # Always red
                    borderwidth=2,
                    relief="solid",
                    foreground="black")
    return style

def highlight_mandatory_entry_on_focus_out(entry: Entry):
    """Highlights a ttk.Entry in red (DANGER) when clicking out of focus if field is empty.

    Args:
        entry (Entry): Entry widget to be modified
    """
    get_styles()
    if entry.get():
        entry.config(bootstyle=DEFAULT)
    else:
        entry.config(style="Error.TEntry")

def highlight_mandatory_entry_on_focus_in(entry: Entry):
    """Changes ttk.Entry back to default settings.

    Args:
        entry (Entry): Entry widget to be modified
    """ 
    entry.config(bootstyle=DEFAULT)

def show_error_in_entry(entry: Entry):
    """Changes ttk.Entry widget to highlight with Bootstrap DANGER style.

    Args:
        entry (Entry): Entry widget to be modified
    """
    get_styles()
    entry.config(style="Error.TEntry")