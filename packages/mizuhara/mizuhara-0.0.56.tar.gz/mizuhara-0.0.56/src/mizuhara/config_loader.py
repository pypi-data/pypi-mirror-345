import importlib.util
import os
import sys

CONFIG_NAME = "config.py"

def find_config():
    """Search for config.py in the user's project."""
    for path in sys.path:
        config_path = os.path.join(path, CONFIG_NAME)

        if os.path.exists(config_path):
            return config_path
    return None

def load_config():
    """Dynamically import config.py if it exists."""
    config_path = find_config()
    if not config_path:
        raise FileNotFoundError("No config.py found. Please create one in your project root.")

    # create a module specification for config.py with naming config
    # importlib.util.spec_from_file_location(module name, import path)
    # type = ModuleSpec
    spec = importlib.util.spec_from_file_location("config", config_path)

    # create an empty module class instance from specification.
    # importlib.util.module_from_spec(spec)
    config = importlib.util.module_from_spec(spec)

    # execute an empty module
    # load and execute config.py from config
    spec.loader.exec_module(config)

    # Inject into `sys.modules` as `mizuhara.config`
    sys.modules["mizuhara.config"] = config
    return config