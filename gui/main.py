"""
LLama Server GUI Manager
A graphical interface for configuring and managing llama-server
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
import threading
import os
import webbrowser
from datetime import datetime

from .config import (
    load_config,
    save_config,
    get_models_dir,
    DEFAULT_CONFIG,
    get_language,
    set_language,
)
from .server_manager import ServerManager
from .huggingface import HuggingFaceDownloader
from .collapsible_frame import CollapsibleFrame
from .search_box import SearchBox
from .param_widgets import ParamWidgets
from .params_db import (
    PARAMETER_GROUPS,
    ParamCategory,
    DEFAULT_CONFIG as PARAM_DEFAULT_CONFIG,
)
from .cmd_preview import CommandPreview
from .monitor.charts import MonitoringChart
from .i18n import Translator, _


class LlamaServerGUI(ctk.CTk):
    """Main GUI application for llama-server management"""

    def __init__(self):
        super().__init__()

        # Window setup
        self.title(_("app.title"))
        self.geometry("900x700")
        self.minsize(800, 600)

        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Load saved language and update the global translator
        saved_lang = get_language()
        _.set_language(saved_lang)

        # Language selector options (do NOT translate keys here; they must stay stable)
        self.lang_options = {
            "English": "en",
            "中文": "zh",
            "Deutsch": "de",
        }
        self.lang_reverse = {v: k for k, v in self.lang_options.items()}

        # Initialize variables first
        self.model_path_var = ctk.StringVar(value="")
        self.host_var = ctk.StringVar(value="0.0.0.0")
        self.port_var = ctk.StringVar(value="8080")
        self.context_size_var = ctk.StringVar(value="4096")
        self.threads_var = ctk.StringVar(value="")
        self.batch_size_var = ctk.StringVar(value="512")
        self.n_predict_var = ctk.StringVar(value="256")
        self.temperature_var = ctk.StringVar(value="0.7")
        self.n_gpu_layers_var = ctk.StringVar(value="0")
        self.cache_capacity_var = ctk.StringVar(value="2048MiB")
        self.flash_attn_var = ctk.BooleanVar(value=False)

        # Initialize managers
        self.server_manager = ServerManager()
        self.hf_downloader = HuggingFaceDownloader()

        # Setup callbacks
        self.server_manager.set_log_callback(self._add_log)
        self.server_manager.set_status_callback(self._update_status_label)

        # Create UI
        self._create_menu()
        self._create_ui()
        self._create_language_selector()

        # Load initial config
        self._load_config_to_ui()

        # Start status update loop
        self._update_status_loop()

    def _create_language_selector(self):
        lang_frame = ctk.CTkFrame(self, fg_color="transparent")
        lang_frame.pack(fill="x", padx=10, pady=(0, 5))

        lang_label = ctk.CTkLabel(
            lang_frame,
            text=_("language.label") + ":",
            width=80,
            anchor="e",
        )
        lang_label.pack(side="right", padx=(0, 5))

        current_lang_name = self.lang_reverse.get(_.lang, "English")
        self.lang_selector = ctk.CTkComboBox(
            lang_frame,
            values=list(self.lang_options.keys()),
            width=120,
            command=self._on_language_change,
        )
        self.lang_selector.set(current_lang_name)
        self.lang_selector.pack(side="right")

    def _on_language_change(self, choice: str):
        new_lang = self.lang_options.get(choice)
        if new_lang and new_lang != _.lang:
            set_language(new_lang)
            # Update global translator so all _() calls use the new language
            _.set_language(new_lang)
            messagebox.showinfo(
                _("dialogs.info", "Info"),
                _(
                    "dialogs.language_changed",
                    "Language changed. Please restart the application to apply all changes.",
                ),
            )

    def _create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=_("menu.file"), menu=file_menu)
        file_menu.add_command(label=_("menu.file.save"), command=self._save_config)
        file_menu.add_command(label=_("menu.file.reset"), command=self._reset_config)
        file_menu.add_separator()
        file_menu.add_command(label=_("menu.file.exit"), command=self.quit)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=_("menu.help"), menu=help_menu)
        help_menu.add_command(label=_("menu.help.about"), command=self._show_about)

    def _create_ui(self):
        """Create the main UI"""
        # Main container with tabs
        self.notebook = ctk.CTkTabview(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Create tabs
        self.tab_config = self.notebook.add(_("tabs.config"))
        self.tab_model = self.notebook.add(_("tabs.model"))
        self.tab_status = self.notebook.add(_("tabs.status"))
        self.tab_advanced = self.notebook.add(_("tabs.advanced"))
        self.tab_monitoring = self.notebook.add(_("tabs.monitoring"))

        self._create_config_tab()
        self._create_model_tab()
        self._create_status_tab()
        self._create_advanced_tab()
        self._create_monitoring_tab()

    def _create_config_tab(self):
        """Create server configuration tab"""
        # Scrollable frame for config
        self.config_scroll = ctk.CTkScrollableFrame(self.tab_config)
        self.config_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        row = 0

        # Model path
        self._create_file_field(
            self.config_scroll, _("lbl.model_file"), "", self._browse_model, row
        )
        row += 1

        # Host
        self._create_entry_field(self.config_scroll, _("lbl.host"), self.host_var, row)
        row += 1

        # Port
        self._create_entry_field(self.config_scroll, _("lbl.port"), self.port_var, row)
        row += 1

        # Context size
        self._create_entry_field(
            self.config_scroll, _("lbl.context_size"), self.context_size_var, row
        )
        row += 1

        # Threads
        self._create_entry_field(
            self.config_scroll, _("lbl.threads"), self.threads_var, row
        )
        row += 1

        # Batch size
        self._create_entry_field(
            self.config_scroll, _("lbl.batch_size"), self.batch_size_var, row
        )
        row += 1

        # N Predict
        self._create_entry_field(
            self.config_scroll, _("lbl.n_predict"), self.n_predict_var, row
        )
        row += 1

        # Temperature
        self._create_entry_field(
            self.config_scroll, _("lbl.temperature"), self.temperature_var, row
        )
        row += 1

        # GPU layers
        self._create_entry_field(
            self.config_scroll, _("lbl.gpu_layers"), self.n_gpu_layers_var, row
        )
        row += 1

        # Cache capacity
        self._create_entry_field(
            self.config_scroll, _("lbl.cache_capacity"), self.cache_capacity_var, row
        )
        row += 1

        # Flash attention
        flash_frame = ctk.CTkFrame(self.config_scroll)
        flash_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(flash_frame, text=_("lbl.flash_attention", "Flash Attention"), width=200, anchor="w").pack(
            side="left"
        )
        ctk.CTkCheckBox(flash_frame, variable=self.flash_attn_var).pack(
            side="left", padx=10
        )

        # Buttons frame
        btn_frame = ctk.CTkFrame(self.config_scroll)
        btn_frame.pack(fill="x", padx=10, pady=20)

        self.btn_start = ctk.CTkButton(
            btn_frame,
            text=_("btn.start_server"),
            command=self._start_server,
            fg_color="green",
        )
        self.btn_start.pack(side="left", padx=5)

        self.btn_stop = ctk.CTkButton(
            btn_frame,
            text=_("btn.stop_server"),
            command=self._stop_server,
            fg_color="red",
        )
        self.btn_stop.pack(side="left", padx=5)

        self.btn_restart = ctk.CTkButton(
            btn_frame,
            text=_("btn.restart"),
            command=self._restart_server,
            fg_color="orange",
        )
        self.btn_restart.pack(side="left", padx=5)

        self.btn_save = ctk.CTkButton(
            btn_frame, text=_("btn.save"), command=self._save_config
        )
        self.btn_save.pack(side="right", padx=5)

    def _create_model_tab(self):
        """Create model management tab"""
        # HuggingFace download section
        hf_frame = ctk.CTkFrame(self.tab_model)
        hf_frame.pack(fill="x", padx=10, pady=10)

        hf_title = ctk.CTkLabel(
            hf_frame,
            text=_("lbl.download_from_hf"),
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        hf_title.pack(padx=10, pady=5)

        # URL entry
        url_frame = ctk.CTkFrame(hf_frame)
        url_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(url_frame, text="HuggingFace URL:").pack(side="left", padx=5)
        self.hf_url_var = ctk.StringVar()
        self.hf_url_entry = ctk.CTkEntry(
            url_frame, textvariable=self.hf_url_var, width=500
        )
        self.hf_url_entry.pack(side="left", padx=5, fill="x", expand=True)

        # Examples button (correct parent frame; previously referenced undefined local_frame/repo)
        ctk.CTkButton(
            url_frame,
            text=_("btn.use_repo"),
            width=100,
            command=self._show_hf_examples,
        ).pack(side="left", padx=5)

        # Progress bar
        self.download_progress = ctk.CTkProgressBar(hf_frame)
        self.download_progress.pack(fill="x", padx=10, pady=5)
        self.download_progress.set(0)

        # Progress label
        self.download_progress_label = ctk.CTkLabel(hf_frame, text="")
        self.download_progress_label.pack(padx=10, pady=2)

        # Download buttons
        dl_btn_frame = ctk.CTkFrame(hf_frame)
        dl_btn_frame.pack(padx=10, pady=10)

        self.btn_download = ctk.CTkButton(
            dl_btn_frame,
            text=_("btn.start_download"),
            command=self._start_download,
            fg_color="blue",
        )
        self.btn_download.pack(side="left", padx=5)

        self.btn_cancel_download = ctk.CTkButton(
            dl_btn_frame,
            text=_("btn.cancel"),
            command=self._cancel_download,
            fg_color="gray",
        )
        self.btn_cancel_download.pack(side="left", padx=5)

        # Popular models
        popular_frame = ctk.CTkFrame(self.tab_model)
        popular_frame.pack(fill="both", expand=True, padx=10, pady=10)

        popular_title = ctk.CTkLabel(
            popular_frame,
            text=_("lbl.popular_models"),
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        popular_title.pack(padx=10, pady=5)

        self.popular_list = ctk.CTkScrollableFrame(popular_frame)
        self.popular_list.pack(fill="both", expand=True, padx=5, pady=5)

        self._populate_popular_models()

        # Local models list
        local_frame = ctk.CTkFrame(self.tab_model)
        local_frame.pack(fill="both", expand=True, padx=10, pady=10)

        local_title = ctk.CTkLabel(
            local_frame,
            text=_("lbl.local_models"),
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        local_title.pack(padx=10, pady=5)

        self.local_models_listbox = ctk.CTkScrollableFrame(local_frame)
        self.local_models_listbox.pack(fill="both", expand=True, padx=5, pady=5)

        self._refresh_local_models()

        # Refresh button
        ctk.CTkButton(
            local_frame,
            text=_("btn.refresh"),
            command=self._refresh_local_models,
            width=100,
        ).pack(pady=5)

    def _create_status_tab(self):
        """Create status monitoring tab"""
        # Status indicator
        status_frame = ctk.CTkFrame(self.tab_status)
        status_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            status_frame, text=_("lbl.server_status"), width=120, anchor="w"
        ).pack(side="left")
        self.status_label = ctk.CTkLabel(
            status_frame,
            text=_("status.stopped"),
            fg_color="gray",
            width=100,
            corner_radius=5,
        )
        self.status_label.pack(side="left", padx=10)

        self.pid_label = ctk.CTkLabel(status_frame, text="")
        self.pid_label.pack(side="right", padx=10)

        # Server info
        info_frame = ctk.CTkFrame(self.tab_status)
        info_frame.pack(fill="x", padx=10, pady=5)

        self.url_label = ctk.CTkLabel(info_frame, text=_("lbl.api_url"))
        self.url_label.pack(anchor="w", padx=10, pady=5)

        self.uptime_label = ctk.CTkLabel(info_frame, text=_("lbl.uptime"))
        self.uptime_label.pack(anchor="w", padx=10, pady=5)

        # Log viewer
        log_frame = ctk.CTkFrame(self.tab_status)
        log_frame.pack(fill="both", expand=True, padx=10, pady=10)

        log_title = ctk.CTkLabel(
            log_frame,
            text=_("lbl.server_logs"),
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        log_title.pack(padx=10, pady=5)

        self.log_text = ctk.CTkTextbox(log_frame)
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)

        # Log buttons
        log_btn_frame = ctk.CTkFrame(log_frame)
        log_btn_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkButton(
            log_btn_frame,
            text=_("btn.refresh_logs"),
            command=self._refresh_logs,
            width=100,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            log_btn_frame,
            text=_("btn.clear_logs"),
            command=self._clear_logs,
            fg_color="gray",
            width=100,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            log_btn_frame,
            text=_("btn.open_browser"),
            command=self._open_browser,
            width=100,
        ).pack(side="right", padx=5)

    def _create_advanced_tab(self):
        """Create advanced parameters tab with categorized collapsible sections"""
        # Scrollable frame for advanced parameters
        scroll_frame = ctk.CTkScrollableFrame(self.tab_advanced)
        scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Search box at top
        search_frame = ctk.CTkFrame(scroll_frame)
        search_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            search_frame,
            text=_("labels.search_params"),
            font=ctk.CTkFont(weight="bold"),
        ).pack(side="left", padx=5)

        self.advanced_search = SearchBox(
            search_frame,
            search_callback=self._filter_advanced_params,
            placeholder_text=_("placeholders.search_params"),
            width=400,
        )
        self.advanced_search.pack(side="left", padx=5, fill="x", expand=True)

        # Container for parameter categories
        self.advanced_params_container = ctk.CTkFrame(
            scroll_frame, fg_color="transparent"
        )
        self.advanced_params_container.pack(fill="x", expand=True, padx=5, pady=5)

        # Store parameter widgets for filtering
        self._advanced_param_widgets = {}
        self._category_frames = {}

        # Category display names mapping
        category_names = {
            ParamCategory.COMMON: _("labels.common_params"),
            ParamCategory.GPU_MEMORY: _("labels.gpu_memory_params"),
            ParamCategory.SERVER: _("labels.server_params"),
            ParamCategory.SAMPLING: _("labels.sampling_params"),
            ParamCategory.TURBOQUANT: _("labels.turboquant_params"),
        }

        # Create collapsible sections for each category
        row = 0
        for category in ParamCategory:
            params = PARAMETER_GROUPS.get(category, [])
            if not params:
                continue

            # Create collapsible frame for category
            cat_frame = CollapsibleFrame(
                self.advanced_params_container,
                title=category_names.get(category, category.value),
                expanded=True,
            )
            cat_frame.pack(fill="x", padx=5, pady=3)
            self._category_frames[category] = cat_frame

            # Create parameter widgets for this category
            param_widgets_factory = ParamWidgets(cat_frame.content_frame)

            for param_def in params:
                frame, widget = param_widgets_factory.create_widget(
                    param_def, row=row, column=0
                )
                # 将参数 frame 添加到标签页内容框中
                frame.pack(fill="x", padx=5, pady=2)
                self._advanced_param_widgets[param_def.name] = {
                    "widget": widget,
                    "frame": frame,
                    "category": category,
                    "param_def": param_def,
                }

        # Buttons frame
        btn_frame = ctk.CTkFrame(scroll_frame)
        btn_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(
            btn_frame,
            text=_("btn.apply_params"),
            command=self._apply_advanced_params,
            fg_color="green",
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text=_("btn.reset_defaults"),
            command=self._reset_advanced_params,
            fg_color="orange",
        ).pack(side="left", padx=5)

        ctk.CTkButton(btn_frame, text=_("btn.save"), command=self._save_config).pack(
            side="right", padx=5
        )

    def _filter_advanced_params(self, search_text: str):
        """Filter advanced parameters based on search text"""
        search_text = search_text.lower().strip()

        for param_name, info in self._advanced_param_widgets.items():
            param_def = info["param_def"]
            frame = info["frame"]
            category = info["category"]

            # Check if parameter matches search
            if search_text:
                matches = (
                    search_text in param_name.lower()
                    or search_text in param_def.description.lower()
                    or search_text in param_def.flag.lower()
                )
            else:
                matches = True

            # Show/hide parameter frame
            if matches:
                frame.pack(fill="x", padx=5, pady=3)
            else:
                frame.pack_forget()

        # Show/hide category frames based on whether they have visible params
        for category, cat_frame in self._category_frames.items():
            has_visible = False
            for param_name, info in self._advanced_param_widgets.items():
                if info["category"] == category:
                    if info["frame"].winfo_viewable():
                        has_visible = True
                        break

            if has_visible:
                cat_frame.pack(fill="x", padx=5, pady=3)
            else:
                cat_frame.pack_forget()

    def _apply_advanced_params(self):
        """Apply advanced parameters to configuration"""
        config_updates = {}

        for param_name, info in self._advanced_param_widgets.items():
            widget = info["widget"]
            value = widget.get_value()
            if value is not None:
                config_updates[param_name] = value

        # Update UI variables
        for key, value in config_updates.items():
            var_name = f"{key}_var"
            if hasattr(self, var_name):
                var = getattr(self, var_name)
                if isinstance(var, ctk.StringVar):
                    var.set(str(value))
                elif isinstance(var, ctk.BooleanVar):
                    var.set(bool(value))

        # Save config
        config = self._get_config_from_ui()
        config.update(config_updates)
        save_config(config)

        self._add_log(_("dialogs.params_applied"))

    def _reset_advanced_params(self):
        """Reset advanced parameters to defaults"""
        for param_name, info in self._advanced_param_widgets.items():
            widget = info["widget"]
            param_def = info["param_def"]
            widget.set_value(param_def.default)

        self._add_log(_("dialogs.params_reset"))

    def _create_monitoring_tab(self):
        """Create monitoring tab with real-time charts and command preview"""
        # Top section: Command Preview
        cmd_frame = ctk.CTkFrame(self.tab_monitoring)
        cmd_frame.pack(fill="x", padx=10, pady=5)

        self.command_preview = CommandPreview(
            cmd_frame,
            config=self._get_config_from_ui(),
            label=_("lbl.current_command"),
        )
        self.command_preview.pack(fill="x", padx=5, pady=5)

        # Update command preview button
        ctk.CTkButton(
            cmd_frame,
            text=_("btn.refreshPreview"),
            command=lambda: self.command_preview.update_from_config(
                self._get_config_from_ui()
            ),
            width=150,
        ).pack(side="right", padx=10, pady=5)

        # Bottom section: Charts
        charts_frame = ctk.CTkFrame(self.tab_monitoring)
        charts_frame.pack(fill="both", expand=True, padx=10, pady=5)

        charts_title = ctk.CTkLabel(
            charts_frame,
            text=_("lbl.realtime_monitoring"),
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        charts_title.pack(padx=10, pady=5)

        # Chart container
        self.chart_container = ctk.CTkFrame(charts_frame)
        self.chart_container.pack(fill="both", expand=True, padx=5, pady=5)

        # Create monitoring chart
        self.monitoring_chart = MonitoringChart(self.chart_container, buffer_size=100)

        # Control buttons
        chart_btn_frame = ctk.CTkFrame(charts_frame)
        chart_btn_frame.pack(fill="x", padx=5, pady=5)

        self.btn_start_monitoring = ctk.CTkButton(
            chart_btn_frame,
            text=_("btn.start_monitoring"),
            command=self._start_monitoring,
            fg_color="green",
            width=100,
        )
        self.btn_start_monitoring.pack(side="left", padx=5)

        self.btn_stop_monitoring = ctk.CTkButton(
            chart_btn_frame,
            text=_("btn.stop_monitoring"),
            command=self._stop_monitoring,
            fg_color="red",
            width=100,
        )
        self.btn_stop_monitoring.pack(side="left", padx=5)

        ctk.CTkButton(
            chart_btn_frame,
            text=_("btn.clear_data"),
            command=self._clear_monitoring_data,
            width=100,
        ).pack(side="left", padx=5)

        # Status label
        self.monitoring_status = ctk.CTkLabel(
            chart_btn_frame,
            text=_("lbl.monitoring_status") + ": " + _("status.stopped"),
            text_color="gray",
        )
        self.monitoring_status.pack(side="right", padx=10)

    def _start_monitoring(self):
        """Start monitoring data collection"""
        self.monitoring_chart.start_updating()
        self.monitoring_status.configure(
            text=_("status.monitoring_running"), text_color="green"
        )
        self._add_log(_("messages.monitoring_started"))

        # Start simulated data updates (in real implementation, this would connect to actual metrics)
        self._update_monitoring_data()

    def _stop_monitoring(self):
        """Stop monitoring data collection"""
        self.monitoring_chart.stop_updating()
        self.monitoring_status.configure(
            text=_("status.monitoring_stopped"), text_color="gray"
        )
        self._add_log(_("messages.monitoring_stopped"))

    def _clear_monitoring_data(self):
        """Clear monitoring chart data"""
        self.monitoring_chart.clear_data()
        self._add_log(_("messages.monitoring_data_cleared"))

    def _update_monitoring_data(self):
        """Update monitoring chart with simulated data"""
        if not self.monitoring_chart._is_updating:
            return

        # In real implementation, this would fetch actual metrics from the server
        # For now, generate simulated data for demonstration
        import random

        test_data = {
            "ram_mb": random.uniform(1000, 4000),
            "vram_mb": random.uniform(500, 2000) if random.random() > 0.3 else 0,
            "tokens_per_sec": random.uniform(5, 25),
        }
        self.monitoring_chart.update_data(test_data)

        # Schedule next update
        self.after(1000, self._update_monitoring_data)

    def _create_entry_field(self, parent, label, var, row):
        """Create a labeled entry field with StringVar binding"""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=10, pady=3)

        ctk.CTkLabel(frame, text=label, width=150, anchor="w").pack(side="left")

        entry = ctk.CTkEntry(frame, textvariable=var, width=200)
        entry.pack(side="right")

    def _create_file_field(self, parent, label, default, browse_cmd, row):
        """Create a labeled file field with browse button"""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(frame, text=label, width=150, anchor="w").pack(side="left")

        entry = ctk.CTkEntry(frame, textvariable=self.model_path_var, width=500)
        entry.pack(side="left", padx=5, fill="x", expand=True)

        ctk.CTkButton(frame, text=_("btn.browse", "Browse..."), width=60, command=browse_cmd).pack(
            side="left", padx=5
        )

    def _browse_model(self):
        """Open file dialog to select model"""
        models_dir = str(get_models_dir())
        filename = filedialog.askopenfilename(
            title=_("dialogs.select_model_file"),
            initialdir=models_dir,
            filetypes=[("GGUF files", "*.gguf"), ("All files", "*.*")],
        )
        if filename:
            self.model_path_var.set(filename)

    def _load_config_to_ui(self):
        """Load configuration from file to UI"""
        config = load_config()

        self.model_path_var.set(config.get("model_path", ""))
        self.host_var.set(config.get("host", "0.0.0.0"))
        self.port_var.set(str(config.get("port", 8080)))
        self.context_size_var.set(str(config.get("context_size", 4096)))
        self.threads_var.set(config.get("threads", ""))
        self.batch_size_var.set(str(config.get("batch_size", 512)))
        self.n_predict_var.set(str(config.get("n_predict", 256)))
        self.temperature_var.set(str(config.get("temperature", 0.7)))
        self.n_gpu_layers_var.set(str(config.get("n_gpu_layers", 0)))
        self.cache_capacity_var.set(config.get("cache_capacity", "2048MiB"))
        self.flash_attn_var.set(config.get("flash_attn", False))

        # Load advanced parameters if widgets are created
        if hasattr(self, "_advanced_param_widgets"):
            for param_name, info in self._advanced_param_widgets.items():
                if param_name in config:
                    info["widget"].set_value(config[param_name])

    def _get_config_from_ui(self):
        """Get current configuration from UI"""
        config = {}

        config["model_path"] = self.model_path_var.get()
        config["host"] = self.host_var.get()
        config["port"] = int(self.port_var.get()) if self.port_var.get() else 8080
        config["context_size"] = (
            int(self.context_size_var.get()) if self.context_size_var.get() else 4096
        )

        threads_val = self.threads_var.get()
        config["threads"] = (
            int(threads_val) if threads_val and threads_val != "None" else None
        )

        config["batch_size"] = (
            int(self.batch_size_var.get()) if self.batch_size_var.get() else 512
        )
        config["n_predict"] = (
            int(self.n_predict_var.get()) if self.n_predict_var.get() else 256
        )
        config["temperature"] = (
            float(self.temperature_var.get()) if self.temperature_var.get() else 0.7
        )
        config["n_gpu_layers"] = (
            int(self.n_gpu_layers_var.get()) if self.n_gpu_layers_var.get() else 0
        )
        config["cache_capacity"] = self.cache_capacity_var.get()
        config["flash_attn"] = self.flash_attn_var.get()

        # Add advanced parameters if widgets are created
        if hasattr(self, "_advanced_param_widgets"):
            for param_name, info in self._advanced_param_widgets.items():
                value = info["widget"].get_value()
                if value is not None:
                    config[param_name] = value

        return config

    def _save_config(self):
        """Save current configuration"""
        config = self._get_config_from_ui()
        if save_config(config):
            self._add_log(_("messages.config_saved_log"))
            messagebox.showinfo(_("dialogs.config_saved"), _("dialogs.config_saved"))
        else:
            messagebox.showerror(_("dialogs.save_failed"), _("dialogs.save_failed"))

    def _reset_config(self):
        """Reset configuration to defaults"""
        if messagebox.askyesno(_("dialogs.confirm_reset"), _("dialogs.confirm_reset")):
            for key, value in DEFAULT_CONFIG.items():
                var_name = f"{key}_var"
                if hasattr(self, var_name):
                    var = getattr(self, var_name)
                    if isinstance(var, ctk.BooleanVar):
                        var.set(value)
                    elif isinstance(var, ctk.StringVar):
                        var.set(str(value) if value is not None else "")
            self._add_log(_("messages.config_reset_log"))

    def _start_server(self):
        """Start the server"""
        # Save config first
        self._save_config()

        # Check if already running
        if self.server_manager.is_running():
            messagebox.showwarning(_("dialogs.warning"), _("dialogs.server_running"))
            return

        # Check if port is in use
        config = self._get_config_from_ui()
        port = config.get("port", 8080)
        if self.server_manager.is_server_running_on_port(port):
            response = messagebox.askyesno(
                _("dialogs.port_in_use_title"),
                _("dialogs.port_in_use").format(port=port),
            )
            if response:
                self._restart_server()
            return

        # Start in background thread
        def run_start():
            config = self._get_config_from_ui()
            success = self.server_manager.start(config)
            if not success:
                self.after(
                    0,
                    lambda: messagebox.showerror(_("status.error"), _("status.error")),
                )

        thread = threading.Thread(target=run_start, daemon=True)
        thread.start()

    def _stop_server(self):
        """Stop the server"""
        if not self.server_manager.is_running():
            # Check if any server on port
            config = self._get_config_from_ui()
            port = config.get("port", 8080)
            if not self.server_manager.is_server_running_on_port(port):
                messagebox.showinfo(
                    _("dialogs.server_not_running"), _("dialogs.server_not_running")
                )
                return

        response = messagebox.askyesno(
            _("dialogs.confirm_stop"), _("dialogs.confirm_stop")
        )
        if response:
            self.server_manager.stop()

    def _restart_server(self):
        """Restart the server"""
        response = messagebox.askyesno(
            _("dialogs.confirm_restart"), _("dialogs.confirm_restart")
        )
        if not response:
            return

        def run_restart():
            config = self._get_config_from_ui()
            self.server_manager.restart(config)

        thread = threading.Thread(target=run_restart, daemon=True)
        thread.start()

    def _start_download(self):
        """Start downloading a model"""
        url = self.hf_url_var.get().strip()
        if not url:
            messagebox.showwarning(_("dialogs.enter_url"), _("dialogs.enter_url"))
            return

        # Disable download button
        self.btn_download.configure(state="disabled")
        self.download_progress.set(0)
        self.download_progress_label.configure(text="Connecting...")

        def progress_callback(downloaded, total):
            if total > 0:
                progress = downloaded / total
                self.after(0, lambda: self.download_progress.set(progress))
                self.after(
                    0,
                    lambda: self.download_progress_label.configure(
                        text=f"{self._format_size(downloaded)} / {self._format_size(total)}"
                    ),
                )

        def log_callback(msg):
            self.after(
                0, lambda: self._add_log(f"[{_('messages.download_prefix')}] {msg}")
            )

        def on_complete(success, result):
            self.btn_download.configure(state="normal")
            if success:
                self.download_progress.set(1)
                self.download_progress_label.configure(text="Download complete!")
                self._add_log(f"Model saved to: {result}")
                self._refresh_local_models()
                messagebox.showinfo(
                    _("dialogs.download_complete"),
                    _("dialogs.download_saved_to").format(path=result),
                )
            else:
                self.download_progress.set(0)
                self.download_progress_label.configure(text="Download failed")
                if _("btn.cancel") not in result:
                    messagebox.showerror(_("dialogs.download_failed"), result)

        def run_download():
            success, result = self.hf_downloader.download(
                url, progress_callback, log_callback
            )
            self.after(0, lambda: on_complete(success, result))

        thread = threading.Thread(target=run_download, daemon=True)
        thread.start()

    def _cancel_download(self):
        """Cancel current download"""
        self.hf_downloader.set_cancel()
        self.btn_download.configure(state="normal")
        self.download_progress_label.configure(text=_("dialogs.download_cancelled"))

    def _show_hf_examples(self):
        """Show HuggingFace URL examples"""
        examples = _("dialogs.url_examples")
        messagebox.showinfo(_("dialogs.url_examples_title"), examples)

    def _populate_popular_models(self):
        """Populate popular models list"""
        repos = self.hf_downloader.get_popular_gguf_repos()

        for repo in repos:
            frame = ctk.CTkFrame(self.popular_list)
            frame.pack(fill="x", padx=5, pady=3)

            ctk.CTkLabel(frame, text=repo["name"], width=200, anchor="w").pack(
                side="left"
            )

            ctk.CTkButton(
                frame,
                text=_("btn.use_this_repo"),
                width=100,
                command=lambda r=repo["repo"]: self._use_popular_repo(r),
            ).pack(side="left", padx=5)

    def _use_popular_repo(self, repo: str):
        """Use a popular repository - show example files"""
        # For now, just set the repo in URL
        self.hf_url_var.set(f"{repo}/")
        self._add_log(f"已选择仓库：{repo}")

    def _refresh_local_models(self):
        """Refresh local models list"""
        # Clear current list
        for widget in self.local_models_listbox.winfo_children():
            widget.destroy()

        models_dir = get_models_dir()
        if not models_dir.exists():
            return

        gguf_files = sorted(models_dir.glob("*.gguf"))
        for gguf in gguf_files:
            frame = ctk.CTkFrame(self.local_models_listbox)
            frame.pack(fill="x", padx=5, pady=2)

            size_str = self._format_size(gguf.stat().st_size)
            ctk.CTkLabel(
                frame, text=f"{gguf.name} ({size_str})", width=400, anchor="w"
            ).pack(side="left")

            ctk.CTkButton(
                frame,
                text=_("btn.select_model"),
                width=100,
                command=lambda p=str(gguf): self._select_model(p),
            ).pack(side="left", padx=5)

    def _select_model(self, path: str):
        """Select a model from the list"""
        self.model_path_var.set(path)
        self.notebook.select(0)  # Switch to config tab
        self._add_log(f"已选择模型：{path}")

    def _refresh_logs(self):
        """Refresh log display"""
        self.log_text.delete("0.0", "end")
        logs = self.server_manager.get_logs()
        self.log_text.insert("0.0", logs)

    def _clear_logs(self):
        """Clear log display"""
        self.log_text.delete("0.0", "end")

    def _open_browser(self):
        """Open server URL in browser"""
        config = self._get_config_from_ui()
        host = config.get("host", "0.0.0.0")
        port = config.get("port", 8080)

        if host == "0.0.0.0":
            host = "localhost"

        url = f"http://{host}:{port}"
        webbrowser.open(url)
        self._add_log(f"打开浏览器：{url}")

    def _add_log(self, message: str):
        """Add a log message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"

        self.log_text.insert("end", log_entry)
        self.log_text.see("end")

    def _update_status_label(self, status: str):
        """Update the status indicator"""
        if status == _("status.running"):
            self.status_label.configure(text=_("status.running"), fg_color="green")
            self.pid_label.configure(
                text=f"PID: {self.server_manager.process.pid if self.server_manager.process else 'N/A'}"
            )
            config = self._get_config_from_ui()
            host = config.get("host", "0.0.0.0")
            port = config.get("port", 8080)
            if host == "0.0.0.0":
                host = "localhost"
            self.url_label.configure(text=f"API URL: http://{host}:{port}")
        elif status == _("status.stopped"):
            self.status_label.configure(text=_("status.stopped"), fg_color="red")
            self.pid_label.configure(text="")
            self.url_label.configure(text="API URL: -")
            self.uptime_label.configure(text="Uptime: -")
        elif status.startswith(_("status.error")):
            self.status_label.configure(text=_("status.error"), fg_color="orange")
        else:
            self.status_label.configure(text=status, fg_color="gray")

    def _update_status_loop(self):
        """Periodically update server status"""
        is_running = self.server_manager.is_running()

        if is_running:
            if self.status_label.cget("text") != _("status.running"):
                self._update_status_label(_("status.running"))
        else:
            # Check if server running on our port
            config = self._get_config_from_ui()
            port = config.get("port", 8080)
            if self.server_manager.is_server_running_on_port(port):
                pid = self.server_manager.get_server_pid_on_port(port)
                self.status_label.configure(
                    text=_("status.external"), fg_color="yellow"
                )
                self.pid_label.configure(text=f"External PID: {pid}")
            elif self.status_label.cget("text") == _("status.running"):
                self._update_status_label(_("status.stopped"))

        # Schedule next update
        self.after(2000, self._update_status_loop)

    def _show_about(self):
        """Show about dialog"""
        about_text = _("dialogs.about_text")
        messagebox.showinfo(_("dialogs.about_title"), about_text)

    def _format_size(self, size: int) -> str:
        """Format file size in human-readable format"""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024.0:
                return f"{size:.1f}{unit}"
            size /= 1024.0
        return f"{size:.1f}PB"


def main():
    """Main entry point"""
    app = LlamaServerGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
