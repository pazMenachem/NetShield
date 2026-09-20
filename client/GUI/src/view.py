import tkinter as tk
from tkinter import ttk
from .UI_callables import UI_callables
from .logger import setup_logger

APP_NAME = "NetShield"
WINDOW_SIZE = "500x400"

class Viewer(tk.Tk):
    """Main application window."""
    
    def __init__(self) -> None:
        """Initialize the main window."""
        super().__init__()

        self._callables = UI_callables()
        self._logger = setup_logger(__name__)

        # Shared UI variables
        self._selected_button = tk.StringVar(value="no_filter")
        self._curr_domain = tk.StringVar()
        
        self._init_ui()
    
    def _init_ui(self) -> None:
        """Initialize UI components."""
        self._create_main_frame()
        self._create_radio_buttons()
        self._create_domain_list()
        self._create_input_field()
        self._create_action_buttons()
        
    def _create_main_frame(self) -> None:
        """Create and configure the main frame."""
        # Configure window properties
        self.title(APP_NAME)
        self.geometry(WINDOW_SIZE)
        self.resizable(False, False)  # Disable window resizing

        self.main_frame = ttk.Frame(self, padding="20")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid weights for responsiveness
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

    def _create_radio_buttons(self) -> None:
        """Create and configure the radio button section."""
        radio_frame = ttk.LabelFrame(self.main_frame, text="Blocking Mode", padding="10")
        radio_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        # Create radio buttons with equal spacing
        ttk.Radiobutton(
            radio_frame,
            text="No Filter",
            value="no_filter",
            variable=self._selected_button,
            command=lambda: self._callables.filter_update(
                ads_filter=False,
                adult_filter=False
            )
        ).grid(row=0, column=0, padx=10)
        
        ttk.Radiobutton(
            radio_frame,
            text="Ad Block",
            value="ad_block",
            variable=self._selected_button,
            command=lambda: self._callables.filter_update(
                ads_filter=True,
                adult_filter=False
            )
        ).grid(row=0, column=1, padx=10)
        
        ttk.Radiobutton(
            radio_frame,
            text="Adult Block",
            value="adult_block",
            variable=self._selected_button,
            command=lambda: self._callables.filter_update(
                ads_filter=False,
                adult_filter=True
            )
        ).grid(row=0, column=2, padx=10)
        
        ttk.Radiobutton(
            radio_frame,
            text="Both Filters",
            value="both_filters",
            variable=self._selected_button,
            command=lambda: self._callables.filter_update(
                ads_filter=True,
                adult_filter=True
            )
        ).grid(row=0, column=3, padx=10)
    
    def _create_domain_list(self) -> None:
        """Create and configure the domain list section."""
        list_frame = ttk.LabelFrame(self.main_frame, text="Domain List", padding="10")
        list_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)
        
        # Listbox with scrollbar
        self.domain_list = tk.Listbox(
            list_frame,
            height=10,
            selectmode=tk.SINGLE
        )
        scrollbar = ttk.Scrollbar(
            list_frame,
            orient=tk.VERTICAL,
            command=self.domain_list.yview
        )
        self.domain_list.configure(yscrollcommand=scrollbar.set)
        
        self.domain_list.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
    
    def _create_input_field(self) -> None:
        """Create and configure the domain input field."""
        input_frame = ttk.Frame(self.main_frame)
        input_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        input_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(input_frame, text="Domain:").grid(row=0, column=0, padx=(0, 10))
        ttk.Entry(
            input_frame,
            textvariable=self._curr_domain
        ).grid(row=0, column=1, sticky="ew")
    
    def _create_action_buttons(self) -> None:
        """Create and configure the action buttons."""
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=3, column=0, sticky="ew")
        button_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Button(
            button_frame,
            text="Add Domain",
            command=lambda: self._callables.add_domain(
                domain=self._curr_domain.get()
            )
        ).grid(row=0, column=0, padx=(0, 10))
        
        ttk.Button(
            button_frame,
            text="Remove Domain",
            command=lambda: self._callables.remove_domain(
                domain=self._curr_domain.get()
            )
        ).grid(row=0, column=1, sticky="e")
    
    def run(self) -> None:
        """Start the application."""
        try:
            self.mainloop()
        except Exception as e:
            self._logger.error(e)
