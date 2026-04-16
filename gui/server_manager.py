"""
Server Manager - Process lifecycle for llama-server
Start, stop, restart, and monitor the server process
"""

import subprocess
import signal
import os
from typing import Optional, List, Callable, Dict, Any
from pathlib import Path
import threading
import time

from .config import load_config, get_llama_cpp_path, get_models_dir
from .params_db import param_to_flag
from .i18n import _


class ServerManager:
    """Manages the llama-server process lifecycle"""

    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.log_callback: Optional[Callable[[str], None]] = None
        self.status_callback: Optional[Callable[[str], None]] = None
        self._pid_file = Path("/tmp/llama-server.pid")
        self._log_file = Path.home() / "llama" / "logs" / "gui-server.log"

    def set_log_callback(self, callback: Callable[[str], None]):
        """Set callback for log messages"""
        self.log_callback = callback

    def set_status_callback(self, callback: Callable[[str], None]):
        """Set callback for status updates"""
        self.status_callback = callback

    def _log(self, message: str):
        """Log a message"""
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)

    def _update_status(self, status: str):
        """Update server status"""
        if self.status_callback:
            self.status_callback(status)

    def is_running(self) -> bool:
        """Check if server is currently running"""
        if self.process is None:
            return False

        # Check if process is still alive
        ret = self.process.poll()
        if ret is None:
            return True

        self.process = None
        return False

    def is_server_running_on_port(self, port: int) -> bool:
        """Check if any process is listening on the given port"""
        try:
            result = subprocess.run(
                ["lsof", "-i", f":{port}"], capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Try alternative method with ss
            try:
                result = subprocess.run(
                    ["ss", "-tlnp"], capture_output=True, text=True, timeout=5
                )
                return f":{port}" in result.stdout
            except (subprocess.TimeoutExpired, FileNotFoundError):
                return False

    def get_server_pid_on_port(self, port: int) -> Optional[int]:
        """Get PID of server running on the given port"""
        try:
            result = subprocess.run(
                ["lsof", "-ti", f":{port}"], capture_output=True, text=True, timeout=5
            )
            if result.stdout.strip():
                return int(result.stdout.strip())
        except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
            pass
        return None

    def stop(self) -> bool:
        """Stop the running server"""
        config = load_config()
        port = config.get("port", 8080)

        # First try to stop our managed process
        if self.process is not None:
            try:
                self._log(_("server.stopping", "Stopping server..."))
                self.process.terminate()
                try:
                    self.process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait()
                self._log(_("server.stopped", "Server stopped"))
                self.process = None
                self._update_status(_("server.status.stopped", "Stopped"))
                return True
            except Exception as e:
                self._log(_("server.stop_error", f"Error stopping server: {e}"))
                return False

        # Try to find and kill by port
        pid = self.get_server_pid_on_port(port)
        if pid:
            try:
                self._log(_("server.pid_stopping", f"Server running on PID={pid}, stopping..."))
                os.kill(pid, signal.SIGTERM)
                time.sleep(2)
                # Check if still running
                try:
                    os.kill(pid, 0)
                    # Still running, force kill
                    os.kill(pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                self._log(_("server.stopped", "Server stopped"))
                self._update_status(_("server.status.stopped", "Stopped"))
                return True
            except ProcessLookupError:
                self._log(_("server.process_not_found", "Server process not found"))
                return False
            except PermissionError:
                self._log(_("server.permission_denied", "Permission denied stopping server"))
                return False
            except Exception as e:
                self._log(_("server.stop_error", f"Error stopping server: {e}"))
                return False

        self._log(_("server.none_running", "No running server"))
        return True

    def _build_command_line(
        self, config: Dict[str, Any], enable_metrics: bool = True
    ) -> List[str]:
        """
        Build complete command line from config dictionary using param_to_flag()

        Args:
            config: Configuration dictionary with parameter values
            enable_metrics: Whether to add --metrics endpoint (default True)

        Returns:
            Complete command line list for llama-server
        """
        # Get llama-server path
        llama_cpp_path = get_llama_cpp_path()
        if not llama_cpp_path:
            return None
        server_bin = llama_cpp_path / "llama-server"
        if not server_bin.exists():
            return None

        # Start with server binary and model
        cmd = [str(server_bin), "--model", config.get("model_path", "")]

        # Process all parameters using param_to_flag()
        for param_name, value in config.items():
            # Skip model_path - already handled above
            if param_name == "model_path":
                continue

            # Convert parameter to CLI flag
            flag_str = param_to_flag(param_name, value)
            if flag_str:
                # Split flag and value if needed
                if " " in flag_str:
                    flag, value_part = flag_str.split(" ", 1)
                    cmd.extend([flag, value_part])
                else:
                    cmd.append(flag_str)

        # Add --metrics endpoint if enabled and not explicitly disabled
        if enable_metrics and not config.get("no_metrics", False):
            # Check if metrics is already in config (enabled or disabled explicitly)
            if "metrics" not in config or config.get("metrics", True):
                cmd.append("--metrics")

        return cmd

    def start(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Start the server with configuration

        Args:
            config: Configuration dictionary. If None, loads from config file.
                   Supports all 50+ parameters from params_db.
                   Use param_to_flag() to convert parameters to CLI flags.
                   Automatically adds --metrics endpoint unless disabled.

        Returns:
            True if server started successfully, False otherwise
        """
        if self.is_running():
            self._log(_("server.already_running", "Server is already running"))
            return False

        # Load config if not provided (backward compatible)
        if config is None:
            config = load_config()

        # Get llama-server path
        llama_cpp_path = get_llama_cpp_path()
        if not llama_cpp_path:
            self._log(_("server.error.not_found", "Error: llama-server not found"))
            self._update_status(_("server.error.not_found", "Error: llama-server not found"))
            return False

        server_bin = llama_cpp_path / "llama-server"
        if not server_bin.exists():
            self._log(_("server.error.binary_missing", f"Error: llama-server missing: {server_bin}"))
            self._update_status(_("server.error.binary_missing", "Error: llama-server missing"))
            return False

        # Validate model path
        model_path = config.get("model_path", "")
        if not model_path:
            self._log(_("server.error.no_model", "Error: no model selected"))
            self._update_status(_("server.error.no_model", "Error: no model selected"))
            return False

        if not Path(model_path).exists():
            self._log(_("server.error.model_missing", f"Error: model file missing: {model_path}"))
            self._update_status(_("server.error.model_missing", "Error: model file missing"))
            return False

        # Build complete command line using param_to_flag()
        cmd = self._build_command_line(config, enable_metrics=True)

        if not cmd:
            self._log(_("server.error.build_cmd", "Error: unable to build command line"))
            self._update_status(_("server.error.build_cmd", "Error: unable to build command line"))
            return False

        # Ensure log directory exists
        self._log_file.parent.mkdir(parents=True, exist_ok=True)

        # Start process
        try:
            self._log(_("server.starting_cmd", f"Starting server: {' '.join(cmd)}"))
            self._update_status(_("server.starting", "Starting..."))

            with open(self._log_file, "a") as log_f:
                self.process = subprocess.Popen(
                    cmd,
                    stdout=log_f,
                    stderr=subprocess.STDOUT,
                    preexec_fn=os.setsid,
                    cwd=str(Path.home() / "llama"),
                )

            # Save PID
            with open(self._pid_file, "w") as f:
                f.write(str(self.process.pid))

            self._log(_("server.started", f"Server started (PID: {self.process.pid})"))
            self._update_status(_("server.status.running", "Running"))

            # Verify server started
            time.sleep(2)
            if not self.is_running():
                self._log(_("server.start_failed", "Server failed to start"))
                self._update_status(_("server.start_failed", "Start failed"))
                return False

            return True

        except FileNotFoundError as e:
            self._log(_("server.error.program_missing", f"Error: program not found: {e}"))
            self._update_status(_("server.error", f"Error: {e}"))
            return False
        except PermissionError as e:
            self._log(_("server.error.permission", f"Error: permission denied: {e}"))
            self._update_status(_("server.error", f"Error: {e}"))
            return False
        except Exception as e:
            self._log(_("server.error.start", f"Error starting server: {e}"))
            self._update_status(_("server.error", f"Error: {e}"))
            return False

    def start_server(
        self, config: Optional[Dict[str, Any]] = None, enable_metrics: bool = True
    ) -> bool:
        """
        Start the server with full configuration (alias for start() with explicit metrics)

        Args:
            config: Configuration dictionary with all parameters.
                   If None, loads from config file.
                   All 50+ parameters from params_db are supported.
                   Uses param_to_flag() for parameter-to-flag conversion.
            enable_metrics: Whether to enable the /metrics endpoint.
                          Default: True. Set False to disable.

        Returns:
            True if server started successfully, False otherwise
        """
        return self.start(config)

    def restart(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Stop current server and restart with new configuration

        Args:
            config: Configuration dictionary. If None, loads from config file.
                   All 50+ parameters from params_db are supported.

        Returns:
            True if server restarted successfully, False otherwise
        """
        self._log(_("server.restarting", "Restarting server..."))
        self.stop()
        time.sleep(1)
        return self.start(config)

    def get_logs(self, lines: int = 100) -> str:
        """Get recent server logs"""
        if not self._log_file.exists():
            return _("server.no_logs", "No logs available")

        try:
            with open(self._log_file, "r") as f:
                all_lines = f.readlines()
                return "".join(all_lines[-lines:])
        except Exception as e:
            return _("server.log_read_error", f"Failed to read logs: {e}")
