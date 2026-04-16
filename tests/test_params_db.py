"""
Test suite for params_db.py
Verifies parameter definitions, data structures, and functionality
"""

import sys
import os

# Add the project root to the path so we can import the module directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../gui"))

import params_db

ParamDef = params_db.ParamDef
ParamCategory = params_db.ParamCategory
UIType = params_db.UIType
PARAMETER_DATABASE = params_db.PARAMETER_DATABASE
PARAMETER_GROUPS = params_db.PARAMETER_GROUPS
DEFAULT_CONFIG = params_db.DEFAULT_CONFIG
get_param_by_name = params_db.get_param_by_name
get_params_by_category = params_db.get_params_by_category
validate_param_value = params_db.validate_param_value
param_to_flag = params_db.param_to_flag


def test_imports():
    """Test that all required classes and functions can be imported"""
    assert ParamDef is not None
    assert ParamCategory is not None
    assert UIType is not None
    assert PARAMETER_DATABASE is not None
    assert PARAMETER_GROUPS is not None
    assert DEFAULT_CONFIG is not None


def test_parameter_count():
    """Test that we have 50+ parameters"""
    assert len(PARAMETER_DATABASE) >= 50, (
        f"Expected 50+ parameters, got {len(PARAMETER_DATABASE)}"
    )

    # Verify category counts
    categories = {
        ParamCategory.COMMON: 13,
        ParamCategory.GPU_MEMORY: 11,
        ParamCategory.SERVER: 15,
        ParamCategory.SAMPLING: 13,
        ParamCategory.TURBOQUANT: 6,
    }

    total_expected = sum(categories.values())
    assert len(PARAMETER_DATABASE) == total_expected, (
        f"Expected {total_expected} parameters, got {len(PARAMETER_DATABASE)}"
    )


def test_param_def_structure():
    """Test that ParamDef has correct structure"""
    # Test a common parameter
    threads_param = get_param_by_name("threads")
    assert threads_param is not None
    assert threads_param.name == "threads"
    assert threads_param.flag == "--threads"
    assert threads_param.param_type == int
    assert threads_param.category == ParamCategory.COMMON
    assert threads_param.ui_type == UIType.SPINBOX


def test_enum_values():
    """Test that enums have correct values"""
    assert ParamCategory.COMMON.value == "common"
    assert ParamCategory.GPU_MEMORY.value == "gpu_memory"
    assert ParamCategory.SERVER.value == "server"
    assert ParamCategory.SAMPLING.value == "sampling"
    assert ParamCategory.TURBOQUANT.value == "turboquant"

    assert UIType.ENTRY.value == "entry"
    assert UIType.SPINBOX.value == "spinbox"
    assert UIType.CHECKBOX.value == "checkbox"
    assert UIType.COMBOBOX.value == "combobox"
    assert UIType.SLIDER.value == "slider"


def test_parameter_groups():
    """Test that parameters are correctly grouped by category"""
    common_params = get_params_by_category(ParamCategory.COMMON)
    assert len(common_params) == 13

    gpu_params = get_params_by_category(ParamCategory.GPU_MEMORY)
    assert len(gpu_params) == 11

    server_params = get_params_by_category(ParamCategory.SERVER)
    assert len(server_params) == 15

    sampling_params = get_params_by_category(ParamCategory.SAMPLING)
    assert len(sampling_params) == 13

    turboquant_params = get_params_by_category(ParamCategory.TURBOQUANT)
    assert len(turboquant_params) == 6

    # Verify all parameters in groups exist in main database
    all_grouped_params = []
    for category, params in PARAMETER_GROUPS.items():
        all_grouped_params.extend(params)

    assert len(all_grouped_params) == len(PARAMETER_DATABASE)


def test_default_config():
    """Test that DEFAULT_CONFIG is properly constructed"""
    assert "host" in DEFAULT_CONFIG
    assert "port" in DEFAULT_CONFIG
    assert "context_size" in DEFAULT_CONFIG
    assert "temperature" in DEFAULT_CONFIG
    assert "model_path" in DEFAULT_CONFIG  # Backward compatibility
    assert "cache_capacity" in DEFAULT_CONFIG  # Backward compatibility


def test_validation():
    """Test parameter validation"""
    # Valid integer parameter
    assert validate_param_value("threads", 4) == True
    assert validate_param_value("threads", -1) == True
    assert validate_param_value("threads", "4") == True  # String should convert

    # Invalid integer parameter
    assert validate_param_value("threads", 300) == False  # Above max
    assert validate_param_value("threads", -5) == False  # Below min

    # Valid float parameter
    assert validate_param_value("temperature", 0.7) == True
    assert validate_param_value("temperature", "0.8") == True

    # Invalid float parameter
    assert validate_param_value("temperature", 2.5) == False  # Above max
    assert validate_param_value("temperature", -0.1) == False  # Below min

    # Valid boolean parameter
    assert validate_param_value("flash_attn", True) == True
    assert validate_param_value("flash_attn", False) == True
    assert validate_param_value("flash_attn", "true") == True
    assert validate_param_value("flash_attn", "false") == True

    # Valid combobox parameter
    assert validate_param_value("cache_type_k", "f16") == True
    assert validate_param_value("cache_type_k", "turbo3") == True
    assert validate_param_value("cache_type_k", "invalid") == False


def test_param_to_flag():
    """Test conversion of parameters to command line flags"""
    # Boolean true
    assert param_to_flag("flash_attn", True) == "--flash-attn"
    assert param_to_flag("flash_attn", False) is None

    # Integer parameter
    assert param_to_flag("threads", 8) == "--threads 8"
    assert param_to_flag("threads", None) is None
    assert param_to_flag("threads", "") is None

    # Float parameter
    assert param_to_flag("temperature", 0.7) == "--temp 0.7"

    # String parameter
    assert param_to_flag("host", "localhost") == "--host localhost"


def test_backward_compatibility():
    """Test backward compatibility with existing config.py"""
    # These keys should exist in DEFAULT_CONFIG for compatibility
    assert "model_path" in DEFAULT_CONFIG
    assert "cache_capacity" in DEFAULT_CONFIG
    assert DEFAULT_CONFIG["model_path"] == ""
    assert DEFAULT_CONFIG["cache_capacity"] == "2048MiB"


if __name__ == "__main__":
    # Run all tests
    test_imports()
    test_parameter_count()
    test_param_def_structure()
    test_enum_values()
    test_parameter_groups()
    test_default_config()
    test_validation()
    test_param_to_flag()
    test_backward_compatibility()

    print("All tests passed!")
    print(f"Total parameters: {len(PARAMETER_DATABASE)}")
