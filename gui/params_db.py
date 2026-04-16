"""
Parameter definition database for llama-server
Contains 50+ parameters organized by category with dataclass structure
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional, Union


class ParamCategory(Enum):
    """Parameter categories for organization"""

    COMMON = "common"
    GPU_MEMORY = "gpu_memory"
    SERVER = "server"
    SAMPLING = "sampling"
    TURBOQUANT = "turboquant"


class UIType(Enum):
    """UI control types for parameter display"""

    ENTRY = "entry"  # Text input
    SPINBOX = "spinbox"  # Numeric input with spin buttons
    CHECKBOX = "checkbox"  # Boolean toggle
    COMBOBOX = "combobox"  # Dropdown selection
    SLIDER = "slider"  # Range slider


@dataclass(frozen=True)
class ParamDef:
    """
    Definition of a single llama-server parameter

    Attributes:
        name: Internal parameter name (used as config key)
        flag: Command line flag (e.g., "--threads", "-c")
        param_type: Python type for validation/conversion
        default: Default value (None means use llama.cpp default)
        description: Human-readable description
        ui_type: UI control type for GUI
        category: Parameter category for grouping
        min_val: Minimum value for numeric parameters (optional)
        max_val: Maximum value for numeric parameters (optional)
        choices: Valid choices for combobox parameters (optional)
        validator: Custom validation function (optional)
    """

    name: str
    flag: str
    param_type: type
    default: Any
    description: str
    ui_type: UIType
    category: ParamCategory
    min_val: Optional[Union[int, float]] = None
    max_val: Optional[Union[int, float]] = None
    choices: Optional[list] = None
    validator: Optional[Callable[[Any], bool]] = None

    def __post_init__(self):
        """Validate that choices are provided for combobox types"""
        if self.ui_type == UIType.COMBOBOX and self.choices is None:
            raise ValueError(
                f"ParamDef '{self.name}' has UIType.COMBOBOX but no choices"
            )


# Parameter definitions organized by category
# Common parameters
COMMON_PARAMS = [
    ParamDef(
        name="threads",
        flag="--threads",
        param_type=int,
        default=None,
        description="Number of threads to use during generation (-1 = auto)",
        ui_type=UIType.SPINBOX,
        category=ParamCategory.COMMON,
        min_val=-1,
        max_val=256,
    ),
    ParamDef(
        name="threads_batch",
        flag="--threads-batch",
        param_type=int,
        default=None,
        description="Number of threads to use during batch processing (-1 = auto)",
        ui_type=UIType.SPINBOX,
        category=ParamCategory.COMMON,
        min_val=-1,
        max_val=256,
    ),
    ParamDef(
        name="context_size",
        flag="--ctx-size",
        param_type=int,
        default=4096,
        description="Context window size (0 = from model)",
        ui_type=UIType.SPINBOX,
        category=ParamCategory.COMMON,
        min_val=0,
        max_val=32768,
    ),
    ParamDef(
        name="n_predict",
        flag="--n-predict",
        param_type=int,
        default=256,
        description="Maximum number of tokens to predict (-1 = infinite)",
        ui_type=UIType.SPINBOX,
        category=ParamCategory.COMMON,
        min_val=-1,
        max_val=8192,
    ),
    ParamDef(
        name="batch_size",
        flag="--batch-size",
        param_type=int,
        default=512,
        description="Logical batch size for prompt processing",
        ui_type=UIType.SPINBOX,
        category=ParamCategory.COMMON,
        min_val=1,
        max_val=8192,
    ),
    ParamDef(
        name="ubatch_size",
        flag="--ubatch-size",
        param_type=int,
        default=512,
        description="Physical batch size for prompt processing",
        ui_type=UIType.SPINBOX,
        category=ParamCategory.COMMON,
        min_val=1,
        max_val=8192,
    ),
    ParamDef(
        name="keep",
        flag="--keep",
        param_type=int,
        default=0,
        description="Number of tokens to keep from the initial prompt",
        ui_type=UIType.SPINBOX,
        category=ParamCategory.COMMON,
        min_val=0,
        max_val=8192,
    ),
    ParamDef(
        name="flash_attn",
        flag="--flash-attn",
        param_type=bool,
        default=False,
        description="Enable Flash Attention optimization",
        ui_type=UIType.CHECKBOX,
        category=ParamCategory.COMMON,
    ),
    ParamDef(
        name="memory_f16",
        flag="--memory-f16",
        param_type=bool,
        default=True,
        description="Use f16 instead of f32 for memory kv",
        ui_type=UIType.CHECKBOX,
        category=ParamCategory.COMMON,
    ),
    ParamDef(
        name="embeddings",
        flag="--embeddings",
        param_type=bool,
        default=False,
        description="Enable embedding output",
        ui_type=UIType.CHECKBOX,
        category=ParamCategory.COMMON,
    ),
    ParamDef(
        name="prompt_cache",
        flag="--prompt-cache",
        param_type=str,
        default="",
        description="Path to file to cache prompt state",
        ui_type=UIType.ENTRY,
        category=ParamCategory.COMMON,
    ),
    ParamDef(
        name="prompt_cache_all",
        flag="--prompt-cache-all",
        param_type=bool,
        default=False,
        description="Cache all prompt states (including intermediate)",
        ui_type=UIType.CHECKBOX,
        category=ParamCategory.COMMON,
    ),
    ParamDef(
        name="dump_kv_cache",
        flag="--dump-kv-cache",
        param_type=bool,
        default=False,
        description="Dump KV cache to file",
        ui_type=UIType.CHECKBOX,
        category=ParamCategory.COMMON,
    ),
    ParamDef(
        name="cache_capacity",
        flag="--cache-capacity",
        param_type=str,
        default="2048MiB",
        description="Capacity of the KV cache (e.g., '2048MiB', '4GiB')",
        ui_type=UIType.ENTRY,
        category=ParamCategory.COMMON,
    ),
]

# GPU/Memory parameters
GPU_MEMORY_PARAMS = [
    ParamDef(
        name="n_gpu_layers",
        flag="--n-gpu-layers",
        param_type=int,
        default=0,
        description="Number of layers to offload to GPU",
        ui_type=UIType.SPINBOX,
        category=ParamCategory.GPU_MEMORY,
        min_val=0,
        max_val=1000,
    ),
    ParamDef(
        name="split_mode",
        flag="--split-mode",
        param_type=str,
        default="layer",
        description="How to split tensors across GPUs",
        ui_type=UIType.COMBOBOX,
        category=ParamCategory.GPU_MEMORY,
        choices=["none", "layer", "row"],
    ),
    ParamDef(
        name="tensor_split",
        flag="--tensor-split",
        param_type=str,
        default="",
        description="Comma-separated list of tensor split fractions",
        ui_type=UIType.ENTRY,
        category=ParamCategory.GPU_MEMORY,
    ),
    ParamDef(
        name="main_gpu",
        flag="--main-gpu",
        param_type=int,
        default=0,
        description="Main GPU index",
        ui_type=UIType.SPINBOX,
        category=ParamCategory.GPU_MEMORY,
        min_val=0,
        max_val=16,
    ),
    ParamDef(
        name="device",
        flag="--device",
        param_type=str,
        default="",
        description="Device list for GPU inference",
        ui_type=UIType.ENTRY,
        category=ParamCategory.GPU_MEMORY,
    ),
    ParamDef(
        name="mmap",
        flag="--mmap",
        param_type=bool,
        default=True,
        description="Use memory mapping for model loading",
        ui_type=UIType.CHECKBOX,
        category=ParamCategory.GPU_MEMORY,
    ),
    ParamDef(
        name="no_mmap",
        flag="--no-mmap",
        param_type=bool,
        default=False,
        description="Disable memory mapping",
        ui_type=UIType.CHECKBOX,
        category=ParamCategory.GPU_MEMORY,
    ),
    ParamDef(
        name="numa",
        flag="--numa",
        param_type=bool,
        default=False,
        description="Optimize memory access for NUMA systems",
        ui_type=UIType.CHECKBOX,
        category=ParamCategory.GPU_MEMORY,
    ),
    ParamDef(
        name="cpu_mask",
        flag="--cpu-mask",
        param_type=str,
        default="",
        description="CPU affinity mask (hexadecimal)",
        ui_type=UIType.ENTRY,
        category=ParamCategory.GPU_MEMORY,
    ),
    ParamDef(
        name="cpu_strict",
        flag="--cpu-strict",
        param_type=bool,
        default=False,
        description="Use strict CPU placement",
        ui_type=UIType.CHECKBOX,
        category=ParamCategory.GPU_MEMORY,
    ),
    ParamDef(
        name="gpu_tensor_split",
        flag="--gpu-tensor-split",
        param_type=str,
        default="",
        description="GPU tensor split configuration",
        ui_type=UIType.ENTRY,
        category=ParamCategory.GPU_MEMORY,
    ),
]

# Server parameters
SERVER_PARAMS = [
    ParamDef(
        name="host",
        flag="--host",
        param_type=str,
        default="0.0.0.0",
        description="Host address to bind server to",
        ui_type=UIType.ENTRY,
        category=ParamCategory.SERVER,
    ),
    ParamDef(
        name="port",
        flag="--port",
        param_type=int,
        default=8080,
        description="Port number to bind server to",
        ui_type=UIType.SPINBOX,
        category=ParamCategory.SERVER,
        min_val=1,
        max_val=65535,
    ),
    ParamDef(
        name="api_key",
        flag="--api-key",
        param_type=str,
        default="",
        description="API key for authentication (empty = disabled)",
        ui_type=UIType.ENTRY,
        category=ParamCategory.SERVER,
    ),
    ParamDef(
        name="timeout",
        flag="--timeout",
        param_type=int,
        default=600,
        description="Server timeout in seconds",
        ui_type=UIType.SPINBOX,
        category=ParamCategory.SERVER,
        min_val=1,
        max_val=86400,
    ),
    ParamDef(
        name="parallel",
        flag="--parallel",
        param_type=int,
        default=-1,
        description="Number of parallel slots (-1 = auto)",
        ui_type=UIType.SPINBOX,
        category=ParamCategory.SERVER,
        min_val=-1,
        max_val=128,
    ),
    ParamDef(
        name="threads_http",
        flag="--threads-http",
        param_type=int,
        default=-1,
        description="Number of HTTP handling threads (-1 = auto)",
        ui_type=UIType.SPINBOX,
        category=ParamCategory.SERVER,
        min_val=-1,
        max_val=128,
    ),
    ParamDef(
        name="metrics",
        flag="--metrics",
        param_type=bool,
        default=False,
        description="Enable /metrics endpoint for monitoring",
        ui_type=UIType.CHECKBOX,
        category=ParamCategory.SERVER,
    ),
    ParamDef(
        name="slots",
        flag="--slots",
        param_type=bool,
        default=True,
        description="Enable /slots endpoint for slot monitoring",
        ui_type=UIType.CHECKBOX,
        category=ParamCategory.SERVER,
    ),
    ParamDef(
        name="no_slots",
        flag="--no-slots",
        param_type=bool,
        default=False,
        description="Disable /slots endpoint",
        ui_type=UIType.CHECKBOX,
        category=ParamCategory.SERVER,
    ),
    ParamDef(
        name="props",
        flag="--props",
        param_type=bool,
        default=False,
        description="Enable /props endpoint for properties",
        ui_type=UIType.CHECKBOX,
        category=ParamCategory.SERVER,
    ),
    ParamDef(
        name="chat_template",
        flag="--chat-template",
        param_type=str,
        default="",
        description="Path to chat template file",
        ui_type=UIType.ENTRY,
        category=ParamCategory.SERVER,
    ),
    ParamDef(
        name="system_prompt",
        flag="--system-prompt",
        param_type=str,
        default="",
        description="System prompt to use for chat completions",
        ui_type=UIType.ENTRY,
        category=ParamCategory.SERVER,
    ),
    ParamDef(
        name="log_disable",
        flag="--log-disable",
        param_type=bool,
        default=False,
        description="Disable logging",
        ui_type=UIType.CHECKBOX,
        category=ParamCategory.SERVER,
    ),
    ParamDef(
        name="ssl_cert",
        flag="--ssl-cert",
        param_type=str,
        default="",
        description="SSL certificate file path",
        ui_type=UIType.ENTRY,
        category=ParamCategory.SERVER,
    ),
    ParamDef(
        name="ssl_key",
        flag="--ssl-key",
        param_type=str,
        default="",
        description="SSL private key file path",
        ui_type=UIType.ENTRY,
        category=ParamCategory.SERVER,
    ),
]

# Sampling parameters
SAMPLING_PARAMS = [
    ParamDef(
        name="temperature",
        flag="--temp",
        param_type=float,
        default=0.8,
        description="Temperature for sampling (higher = more random)",
        ui_type=UIType.SPINBOX,
        category=ParamCategory.SAMPLING,
        min_val=0.0,
        max_val=2.0,
    ),
    ParamDef(
        name="top_k",
        flag="--top-k",
        param_type=int,
        default=40,
        description="Top-K sampling (0 = disabled)",
        ui_type=UIType.SPINBOX,
        category=ParamCategory.SAMPLING,
        min_val=0,
        max_val=100,
    ),
    ParamDef(
        name="top_p",
        flag="--top-p",
        param_type=float,
        default=0.9,
        description="Top-P (nucleus) sampling (1.0 = disabled)",
        ui_type=UIType.SPINBOX,
        category=ParamCategory.SAMPLING,
        min_val=0.0,
        max_val=1.0,
    ),
    ParamDef(
        name="min_p",
        flag="--min-p",
        param_type=float,
        default=0.0,
        description="Min-P sampling threshold",
        ui_type=UIType.SPINBOX,
        category=ParamCategory.SAMPLING,
        min_val=0.0,
        max_val=1.0,
    ),
    ParamDef(
        name="repeat_penalty",
        flag="--repeat-penalty",
        param_type=float,
        default=1.0,
        description="Penalty for repeated tokens",
        ui_type=UIType.SPINBOX,
        category=ParamCategory.SAMPLING,
        min_val=0.0,
        max_val=2.0,
    ),
    ParamDef(
        name="presence_penalty",
        flag="--presence-penalty",
        param_type=float,
        default=0.0,
        description="Penalty for presence of tokens",
        ui_type=UIType.SPINBOX,
        category=ParamCategory.SAMPLING,
        min_val=0.0,
        max_val=2.0,
    ),
    ParamDef(
        name="frequency_penalty",
        flag="--frequency-penalty",
        param_type=float,
        default=0.0,
        description="Penalty based on token frequency",
        ui_type=UIType.SPINBOX,
        category=ParamCategory.SAMPLING,
        min_val=0.0,
        max_val=2.0,
    ),
    ParamDef(
        name="seed",
        flag="--seed",
        param_type=int,
        default=-1,
        description="Random seed (-1 = random)",
        ui_type=UIType.SPINBOX,
        category=ParamCategory.SAMPLING,
        min_val=-1,
        max_val=2147483647,
    ),
    ParamDef(
        name="ignore_eos",
        flag="--ignore-eos",
        param_type=bool,
        default=False,
        description="Ignore end-of-sequence token",
        ui_type=UIType.CHECKBOX,
        category=ParamCategory.SAMPLING,
    ),
    ParamDef(
        name="logit_bias",
        flag="--logit-bias",
        param_type=str,
        default="",
        description="Logit bias in format 'token_id:bonus'",
        ui_type=UIType.ENTRY,
        category=ParamCategory.SAMPLING,
    ),
    ParamDef(
        name="mirostat",
        flag="--mirostat",
        param_type=int,
        default=0,
        description="Mirostat sampling (0 = disabled, 1 = Mirostat, 2 = Mirostat 2.0)",
        ui_type=UIType.SPINBOX,
        category=ParamCategory.SAMPLING,
        min_val=0,
        max_val=2,
    ),
    ParamDef(
        name="mirostat_tau",
        flag="--mirostat-tau",
        param_type=float,
        default=5.0,
        description="Mirostat target entropy",
        ui_type=UIType.SPINBOX,
        category=ParamCategory.SAMPLING,
        min_val=0.0,
        max_val=10.0,
    ),
    ParamDef(
        name="mirostat_eta",
        flag="--mirostat-eta",
        param_type=float,
        default=0.1,
        description="Mirostat learning rate",
        ui_type=UIType.SPINBOX,
        category=ParamCategory.SAMPLING,
        min_val=0.0,
        max_val=1.0,
    ),
]

# TurboQuant parameters
TURBOQUANT_PARAMS = [
    ParamDef(
        name="cache_type_k",
        flag="--cache-type-k",
        param_type=str,
        default="q8_0",
        description="KV cache type for K (keys) - use q8_0 for safe compression, turbo3/turbo4 for extreme compression",
        ui_type=UIType.COMBOBOX,
        category=ParamCategory.TURBOQUANT,
        choices=[
            "f16",
            "q8_0",
            "q4_0",
            "q4_1",
            "turbo2",
            "turbo3",
            "turbo4",
            "turbo2_0",
            "turbo3_0",
            "turbo4_0",
            "tbq2_0",
            "tbq3_0",
            "tbq4_0",
        ],
    ),
    ParamDef(
        name="cache_type_v",
        flag="--cache-type-v",
        param_type=str,
        default="turbo4",
        description="KV cache type for V (values) - V compression has minimal quality impact, turbo4 recommended",
        ui_type=UIType.COMBOBOX,
        category=ParamCategory.TURBOQUANT,
        choices=[
            "f16",
            "q8_0",
            "q4_0",
            "q4_1",
            "turbo2",
            "turbo3",
            "turbo4",
            "turbo2_0",
            "turbo3_0",
            "turbo4_0",
            "tbq2_0",
            "tbq3_0",
            "tbq4_0",
        ],
    ),
    ParamDef(
        name="turbocomp",
        flag="--turbocomp",
        param_type=bool,
        default=False,
        description="Enable TurboComp compression",
        ui_type=UIType.CHECKBOX,
        category=ParamCategory.TURBOQUANT,
    ),
    ParamDef(
        name="turbocomp_level",
        flag="--turbocomp-level",
        param_type=int,
        default=3,
        description="TurboComp compression level",
        ui_type=UIType.SPINBOX,
        category=ParamCategory.TURBOQUANT,
        min_val=1,
        max_val=9,
    ),
    ParamDef(
        name="turboquant_v2",
        flag="--turboquant-v2",
        param_type=bool,
        default=False,
        description="Enable TurboQuant v2 features",
        ui_type=UIType.CHECKBOX,
        category=ParamCategory.TURBOQUANT,
    ),
    ParamDef(
        name="turboquant_threads",
        flag="--turboquant-threads",
        param_type=int,
        default=-1,
        description="Threads for TurboQuant operations",
        ui_type=UIType.SPINBOX,
        category=ParamCategory.TURBOQUANT,
        min_val=-1,
        max_val=128,
    ),
]


# Complete parameter database
PARAMETER_DATABASE = {
    **{param.name: param for param in COMMON_PARAMS},
    **{param.name: param for param in GPU_MEMORY_PARAMS},
    **{param.name: param for param in SERVER_PARAMS},
    **{param.name: param for param in SAMPLING_PARAMS},
    **{param.name: param for param in TURBOQUANT_PARAMS},
}

# Grouped by category for easier access
PARAMETER_GROUPS = {
    ParamCategory.COMMON: COMMON_PARAMS,
    ParamCategory.GPU_MEMORY: GPU_MEMORY_PARAMS,
    ParamCategory.SERVER: SERVER_PARAMS,
    ParamCategory.SAMPLING: SAMPLING_PARAMS,
    ParamCategory.TURBOQUANT: TURBOQUANT_PARAMS,
}

# Default configuration compatible with existing config.py
DEFAULT_CONFIG = {
    param.name: param.default
    for param in PARAMETER_DATABASE.values()
    if param.default is not None
}

# Add backward compatibility keys
DEFAULT_CONFIG.update(
    {
        "model_path": "",
    }
)


def get_param_by_name(name: str) -> Optional[ParamDef]:
    """Get parameter definition by name"""
    return PARAMETER_DATABASE.get(name)


def get_params_by_category(category: ParamCategory) -> list[ParamDef]:
    """Get all parameters in a specific category"""
    return PARAMETER_GROUPS.get(category, [])


def validate_param_value(param_name: str, value: Any) -> bool:
    """Validate a parameter value against its definition"""
    param_def = get_param_by_name(param_name)
    if not param_def:
        return False

    # Type validation
    if not isinstance(value, param_def.param_type):
        try:
            # Try to convert the value
            converted_value = param_def.param_type(value)
            if param_def.param_type == bool and isinstance(value, str):
                # Special handling for boolean strings
                if value.lower() not in ("true", "false", "1", "0", ""):
                    return False
            value = converted_value
        except (ValueError, TypeError):
            return False

    # Range validation for numeric types
    if param_def.param_type in (int, float) and isinstance(value, (int, float)):
        if param_def.min_val is not None and value < param_def.min_val:
            return False
        if param_def.max_val is not None and value > param_def.max_val:
            return False

    # Choices validation
    if param_def.choices is not None:
        if value not in param_def.choices:
            return False

    # Custom validator
    if param_def.validator is not None:
        return param_def.validator(value)

    return True


def param_to_flag(param_name: str, value: Any) -> Optional[str]:
    """Convert parameter name and value to command line flag"""
    param_def = get_param_by_name(param_name)
    if not param_def:
        return None

    if value is None or value == "":
        return None

    if param_def.param_type == bool:
        if value:
            return param_def.flag
        else:
            # For boolean false values, check if there's a negative flag
            if param_name.startswith("no_"):
                # This is already a negative flag, so don't include when False
                return None
            elif f"no_{param_name}" in PARAMETER_DATABASE:
                # There's a corresponding negative flag
                return None
            else:
                # Just omit the flag when False
                return None
    else:
        return f"{param_def.flag} {value}"


if __name__ == "__main__":
    # Quick validation that we have 50+ parameters
    print(f"Total parameters: {len(PARAMETER_DATABASE)}")
    for category, params in PARAMETER_GROUPS.items():
        print(f"{category.value}: {len(params)} parameters")
