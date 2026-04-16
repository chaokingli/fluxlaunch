"""
CollapsibleFrame component for llama-server GUI
A foldable panel with expand/collapse functionality
"""

import customtkinter as ctk
from typing import Optional


class CollapsibleFrame(ctk.CTkFrame):
    """
    A collapsible frame component with title bar and expand/collapse functionality.

    Features:
    - Title bar with arrow indicator
    - Toggle button to expand/collapse
    - Content container for child widgets
    - Automatic height adjustment when toggled
    - Support for nesting
    """

    def __init__(self, master: any, title: str = "", expanded: bool = True, **kwargs):
        """
        Initialize the collapsible frame.

        Args:
            master: Parent widget
            title: Title text to display in the title bar
            expanded: Initial expand state (True = expanded, False = collapsed)
            **kwargs: Additional arguments passed to CTkFrame
        """
        # Extract custom parameters from kwargs
        self._title = title
        self._expanded = expanded

        # Default width and height if not provided
        kwargs.setdefault("corner_radius", 8)
        kwargs.setdefault("border_width", 1)

        # Initialize parent frame
        super().__init__(master, **kwargs)

        # Create title bar frame
        self._title_frame = ctk.CTkFrame(self, corner_radius=0, border_width=0)
        self._title_frame.pack(fill="x", side="top")

        # Make title frame transparent
        self._title_frame.configure(fg_color="transparent")

        # Create toggle button with arrow indicator
        self._toggle_button = ctk.CTkButton(
            self._title_frame,
            text="▼" if expanded else "▶",
            width=30,
            height=28,
            corner_radius=0,
            command=self.toggle,
            fg_color=("gray70", "gray20"),
            hover_color=("gray50", "gray30"),
        )
        self._toggle_button.pack(side="left", padx=5)

        # Create title label
        self._title_label = ctk.CTkLabel(
            self._title_frame, text=title, font=ctk.CTkFont(weight="bold")
        )
        self._title_label.pack(side="left", padx=5, anchor="w")

        # Create content container frame
        self._content_frame = ctk.CTkFrame(self, corner_radius=0, border_width=0)
        self._content_frame.configure(fg_color="transparent")

        # Store reference to content frame for external access
        self.content_frame = self._content_frame

        # Initial layout based on expanded state
        if expanded:
            self._content_frame.pack(fill="x", side="top", anchor="w")
        else:
            self._content_frame.pack_forget()

        # Bind events for consistent behavior
        self._title_label.bind("<Button-1>", lambda e: self.toggle())
        self._title_frame.bind("<Button-1>", lambda e: self.toggle())

    def toggle(self) -> None:
        """Toggle the expand/collapse state of the frame."""
        if self._expanded:
            self.collapse()
        else:
            self.expand()

    def expand(self) -> None:
        """Expand the frame to show content."""
        if not self._expanded:
            self._expanded = True
            self._toggle_button.configure(text="▼")
            self._content_frame.pack(fill="x", side="top", anchor="w")
            # Force layout update to ensure proper sizing
            self.update_idletasks()

    def collapse(self) -> None:
        """Collapse the frame to hide content."""
        if self._expanded:
            self._expanded = False
            self._toggle_button.configure(text="▶")
            self._content_frame.pack_forget()
            # Force layout update to ensure proper sizing
            self.update_idletasks()

    def is_expanded(self) -> bool:
        """Check if the frame is currently expanded."""
        return self._expanded

    def set_title(self, title: str) -> None:
        """Update the title text."""
        self._title = title
        self._title_label.configure(text=title)

    def get_title(self) -> str:
        """Get the current title text."""
        return self._title

    def destroy(self) -> None:
        """Clean up before destroying."""
        # Unbind events to prevent memory leaks
        self._title_label.unbind("<Button-1>")
        self._title_frame.unbind("<Button-1>")
        super().destroy()
