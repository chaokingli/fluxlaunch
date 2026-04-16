"""
SearchBox component for llama-server GUI
A search input field with search/clear icons and real-time search callbacks
"""

import customtkinter as ctk


class SearchBox(ctk.CTkFrame):
    """
    A search input component with real-time search functionality.

    Features:
    - CTkEntry with search icon on the right
    - Clear button that appears when text is entered
    - Real-time search callback on text changes
    - Keyboard support (Enter for search, Escape to clear)
    - Customizable search callback function
    """

    def __init__(
        self,
        master: any,
        search_callback: callable = None,
        placeholder_text: str = "搜索...",
        width: int = 300,
        height: int = 32,
        **kwargs,
    ):
        """
        Initialize the search box.

        Args:
            master: Parent widget
            search_callback: Function to call when search text changes
            placeholder_text: Placeholder text shown when entry is empty
            width: Width of the widget in pixels
            height: Height of the widget in pixels
            **kwargs: Additional arguments passed to CTkFrame
        """
        # Extract custom parameters from kwargs
        self._search_callback = search_callback
        self._placeholder_text = placeholder_text

        # Default corner radius
        kwargs.setdefault("corner_radius", 8)
        kwargs.setdefault("border_width", 1)

        # Initialize parent frame
        super().__init__(master, **kwargs)

        # Store reference to callback
        self._search_callback = search_callback

        # Create StringVar for entry text
        self._search_text = ctk.StringVar()
        self._search_text.trace_add("write", self._on_text_changed)

        # Create entry widget
        self._entry = ctk.CTkEntry(
            self,
            textvariable=self._search_text,
            placeholder_text=placeholder_text,
            width=width - 70,  # Adjust for icon buttons
            height=height,
            corner_radius=6,
            border_width=1,
            font=ctk.CTkFont(size=12),
        )
        self._entry.pack(side="left", fill="x", expand=True, padx=(5, 0), pady=5)

        # Bind keyboard events
        self._entry.bind("<Return>", self._on_enter_pressed)
        self._entry.bind("<Escape>", self._on_escape_pressed)

        # Create icon frame for buttons
        self._icon_frame = ctk.CTkFrame(self, corner_radius=0, border_width=0)
        self._icon_frame.configure(fg_color="transparent")
        self._icon_frame.pack(side="right", fill="y", padx=(0, 5), pady=5)

        # Create search button (initially disabled, no icon)
        self._search_button = ctk.CTkButton(
            self._icon_frame,
            text="🔍",
            width=28,
            height=height - 10,
            corner_radius=4,
            state="disabled",
            command=self._on_search_click,
            fg_color=("gray70", "gray20"),
            hover_color=("gray50", "gray30"),
            font=ctk.CTkFont(size=14),
        )
        self._search_button.pack(side="left", padx=2)

        # Create clear button (initially hidden)
        self._clear_button = ctk.CTkButton(
            self._icon_frame,
            text="✕",
            width=28,
            height=height - 10,
            corner_radius=4,
            command=self._on_clear_click,
            fg_color=("gray70", "gray20"),
            hover_color=("red", "darkred"),
            font=ctk.CTkFont(size=14),
        )
        self._clear_button.pack(side="left", padx=2)
        self._clear_button.pack_forget()  # Hide initially

        # Update button states based on initial text
        self._update_buttons()

    def _on_text_changed(self, *args):
        """Callback when entry text changes"""
        self._update_buttons()

        # Call search callback if provided and text has changed
        if self._search_callback:
            self._search_callback(self.get_search_text())

    def _update_buttons(self):
        """Update search and clear button states based on entry content"""
        text = self.get_search_text()

        if text:
            # Enable search button and show clear button
            self._search_button.configure(state="normal")
            self._clear_button.pack(side="left", padx=2)
        else:
            # Disable search button and hide clear button
            self._search_button.configure(state="disabled")
            self._clear_button.pack_forget()

    def _on_search_click(self):
        """Callback when search button is clicked"""
        if self._search_callback:
            self._search_callback(self.get_search_text())

    def _on_clear_click(self):
        """Callback when clear button is clicked"""
        self._entry.delete(0, "end")
        self._entry.focus()

    def _on_enter_pressed(self, event):
        """Callback when Enter key is pressed"""
        if self._search_callback:
            self._search_callback(self.get_search_text())

    def _on_escape_pressed(self, event):
        """Callback when Escape key is pressed"""
        self._entry.delete(0, "end")
        self._entry.focus()

    def get_search_text(self) -> str:
        """
        Get the current search text.

        Returns:
            Current text in the entry widget
        """
        return self._search_text.get()

    def set_search_text(self, text: str):
        """
        Set the search text.

        Args:
            text: Text to set in the entry widget
        """
        self._search_text.set(text)
        # Update button states after setting text
        self._update_buttons()

    def clear(self):
        """Clear the search text"""
        self._entry.delete(0, "end")
        self._entry.focus()

    def focus(self):
        """Set focus to the entry widget"""
        self._entry.focus()

    def configure_search_callback(self, callback: callable):
        """
        Configure the search callback function.

        Args:
            callback: Function to call when search text changes
        """
        self._search_callback = callback
