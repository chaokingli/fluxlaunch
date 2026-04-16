"""
Command Preview Component - Real-time display of llama-server command line
"""

import customtkinter as ctk
from typing import Optional

from .params_db import param_to_flag, PARAMETER_DATABASE
from .i18n import _


class CommandPreview(ctk.CTkFrame):
    """
    Component to display and copy the complete llama-server command line.

    Features:
    - Real-time display of full command from config dict
    - One-click copy to clipboard using pyperclip
    - Auto-wrapping and scrollbar for long commands
    - Integrates with params_db.param_to_flag() for parameter conversion
    """

    def __init__(
        self,
        parent: ctk.CTkBaseClass,
        config: Optional[dict] = None,
        label: str = "Server Command:",
        **kwargs,
    ):
        """
        Initialize CommandPreview component.

        Args:
            parent: Parent container
            config: Initial configuration dict (optional)
            label: Label text to display above command
            **kwargs: Additional CTkFrame arguments
        """
        super().__init__(parent, **kwargs)

        self.label_text = label

        # Model path from config
        self._model_path = ""

        # Command preview label
        self._create_widgets()

        # Update if initial config provided
        if config:
            self.update_from_config(config)

    def _create_widgets(self):
        """Create UI widgets for command preview"""
        # Label
        ctk.CTkLabel(
            self, text=self.label_text, font=ctk.CTkFont(weight="bold"), anchor="w"
        ).pack(anchor="w", padx=5, pady=(5, 2))

        # Text widget for command display (read-only, auto-wrap)
        self.command_text = ctk.CTkTextbox(
            self,
            wrap="word",  # Auto-wrap long commands
            state="disabled",
            font=ctk.CTkFont(family="Courier", size=10),
            height=100,
            fg_color=("gray95", "gray15"),
            corner_radius=4,
            border_width=1,
            border_color=("gray70", "gray30"),
        )
        self.command_text.pack(fill="x", padx=5, pady=(2, 5), expand=True)

        # Scrollbar for text widget
        scrollbar = ctk.CTkScrollbar(self, command=self.command_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.command_text.configure(yscrollcommand=scrollbar.set)

        # Button frame
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=5, pady=5)

        # Copy button
        self.copy_button = ctk.CTkButton(
            btn_frame,
            text=_("btn.copy_command", "Copy Command"),
            width=100,
            command=self._copy_command,
        )
        self.copy_button.pack(side="left", padx=5)

        # Update status label
        self.status_label = ctk.CTkLabel(btn_frame, text="", text_color="green")
        self.status_label.pack(side="left", padx=5)

    def _copy_command(self):
        """Copy command to clipboard using pyperclip"""
        try:
            import pyperclip

            command = self.command_text.get("1.0", "end-1c")
            if command:
                pyperclip.copy(command)
                self._show_status(_("status.copied_clipboard", "Copied to clipboard!"), "green")
        except ImportError:
            self._show_status(_("error.install_pyperclip", "pyperclip is required"), "orange")
        except Exception as e:
            self._show_status(_("error.copy_failed", f"Copy failed: {e}"), "red")

    def _show_status(self, message: str, color: str = "green"):
        """Show temporary status message"""
        self.status_label.configure(text=message, text_color=color)
        # Clear status after 2 seconds
        self.after(
            2000, lambda: self.status_label.configure(text="", text_color="green")
        )

    def update_from_config(self, config: dict):
        """
        Update command display from configuration dictionary.

        Args:
            config: Configuration dict containing model_path and parameters
        """
        self._model_path = config.get("model_path", "")

        # Build command line
        command_parts = self._build_command(config)
        command_str = " ".join(command_parts)

        # Display command
        self.command_text.configure(state="normal")
        self.command_text.delete("1.0", "end")
        self.command_text.insert("1.0", command_str)
        self.command_text.configure(state="disabled")
        self.command_text.see("end")

    def _build_command(self, config: dict) -> list[str]:
        """
        Build complete llama-server command from config.

        Args:
            config: Configuration dict

        Returns:
            List of command parts
        """
        command_parts = ["llama-server", "--model", self._model_path]

        # Process all parameters from config
        for param_name, value in config.items():
            # Skip model_path as it's already added
            if param_name == "model_path":
                continue

            # Convert parameter to flag using param_to_flag
            flag_str = param_to_flag(param_name, value)

            if flag_str:
                # Split flag and value for proper command construction
                if " " in flag_str:
                    # Flag has value: "--flag value"
                    flag, val = flag_str.split(" ", 1)
                    command_parts.extend([flag, val])
                else:
                    # Boolean flag: "--flag"
                    command_parts.append(flag_str)

        return command_parts

    def get_command(self) -> str:
        """
        Get current command string.

        Returns:
            Full command line string
        """
        return self.command_text.get("1.0", "end-1c").strip()

    def clear(self):
        """Clear command display"""
        self.command_text.configure(state="normal")
        self.command_text.delete("1.0", "end")
        self.command_text.configure(state="disabled")


# Test standalone when run directly
if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("CommandPreview Test")
    root.geometry("600x300")

    # Sample config
    test_config = {
        "model_path": "/home/cklee/llama/models/llama.gguf",
        "host": "0.0.0.0",
        "port": 8080,
        "context_size": 4096,
        "threads": 8,
        "n_predict": 256,
        "temperature": 0.7,
        "flash_attn": True,
    }

    frame = CommandPreview(root, config=test_config)
    frame.pack(fill="both", expand=True, padx=20, pady=20)

    root.mainloop()
