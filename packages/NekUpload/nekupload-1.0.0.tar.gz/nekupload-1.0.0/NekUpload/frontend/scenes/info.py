import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame

class InfoScene(ScrolledFrame):
    def __init__(self, parent):
        super().__init__(parent, autohide=True)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        self.LEFT_MARGIN = 5

        self._add_about_section()
        self._add_capabilities_section()
        self._add_getting_started_section()

        self.bind("<Configure>", self.update_wraplength)

    def update_wraplength(self, event):
        # Dynamically set the wraplength based on the width of the parent frame
        # Subtract a little for padding and margin
        self.about_description.config(wraplength=event.width - 20)
        self.capability_description.config(wraplength=event.width - 20)
        self.get_started_description.config(wraplength=event.width - 20)

    def _add_about_section(self):
        # Create the label for the title
        about_label = ttk.Label(
            master=self,
            text="What is NekUpload?",
            font=("TkDefaultFont", 20, "bold", "underline"),
            anchor="center",
            bootstyle=PRIMARY
        )
        about_label.grid(row=0, column=0, pady=5, padx=self.LEFT_MARGIN, sticky=W)

        # Create the description label
        self.about_description = ttk.Label(
            master=self,
            text=("NekUpload is designed to enforce a consistent upload format for Nektar++ datasets. "
                "This program removes the burden of data management from the user, ensuring files are uploaded in a defined format. "
                "This ensures that data management best practices are enforced, and that users can easily find their files, "
                "which are hosted on an online repository. This also ensures that the online post-processing programs can function correctly."),
            font=("TKDefaultFont", 12),
            anchor="w",
            justify="left",
        )
        self.about_description.grid(row=1, column=0, padx=self.LEFT_MARGIN, pady=10, sticky="nsew")

    def _add_capabilities_section(self):
        # Create the label for the title
        capability_label = ttk.Label(
            master=self,
            text="Capabilities",
            font=("TkDefaultFont", 20, "bold", "underline"),
            anchor="center",
            bootstyle=SECONDARY
        )
        capability_label.grid(row=2, column=0, pady=5, padx=self.LEFT_MARGIN, sticky=W)

        # Create the description label
        self.capability_description = ttk.Label(
            master=self,
            text=("This program currently contains the following capabilities:\n\n"
                " - Upload Nektar++ datasets\n"
                " - Validate datasets are self-consistent and in correct format\n"
                " - Auto-extraction of existing metadata in file to annotate the datasets\n"
                " - Linking of datasets with pre-existing datasets on the database"),
            font=("TKDefaultFont", 12),
            anchor="w",
            justify="left",
        )
        self.capability_description.grid(row=3, column=0, padx=self.LEFT_MARGIN, pady=10, sticky="nsew")

    def _add_getting_started_section(self):
        get_started_label = ttk.Label(
            master=self,
            text="Getting Started",
            font=("TkDefaultFont", 20, "bold", "underline"),
            anchor="center",
            bootstyle=PRIMARY
        )
        get_started_label.grid(row=4, column=0, pady=5, padx=self.LEFT_MARGIN, sticky=W)

        # Create the description label
        self.get_started_description = ttk.Label(
            master=self,
            text=("To get started with this program, first you must know the host name of the online repository and have an API token"
                "This program currently supports two defaults: one for a demo instance of InvenioRDM and another for the AE Datastore. "
                "Please configure your settings before proceeding."),
            font=("TKDefaultFont", 12),
            anchor="w",
            justify="left",
        )
        self.get_started_description.grid(row=5, column=0, padx=self.LEFT_MARGIN, pady=10, sticky="nsew")
