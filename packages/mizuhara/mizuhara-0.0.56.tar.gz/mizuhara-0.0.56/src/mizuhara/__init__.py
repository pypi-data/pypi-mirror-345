from .config_loader import load_config

# Load config when `mizuhara` is imported
try :
    config = load_config()

# add exception handler to avoid exception during creating project or app
except FileNotFoundError:
    pass
