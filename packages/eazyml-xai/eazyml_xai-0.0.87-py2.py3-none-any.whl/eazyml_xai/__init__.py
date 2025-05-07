import platform
import importlib

# Get the system and architecture
system = platform.system() # Get the sytem, e.g, 'Dawwin' or 'Linux'
arch = platform.machine() # Get the architeture, e.g, 'arm64' or 'x86_64'
# Construct the module name dynamically
module_name = f"{system}_{arch}"

# Dynamically import the module
try:
    imported_module = importlib.import_module(f".{module_name}", package=__name__)
    globals().update(vars(imported_module))  # Optionally import all symbols from the module
except ImportError as e:
    raise ImportError(f"Could not import module '{module_name}': {e}")
