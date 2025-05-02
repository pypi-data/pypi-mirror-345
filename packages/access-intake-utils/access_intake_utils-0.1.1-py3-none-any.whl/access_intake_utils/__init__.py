# ACDtools/__init__.py

# 1. Import necessary submodules or functions to expose them at the package level
# from .module1 import main_function
# from .module2 import helper_function
from . import _version

__version__ = _version.get_versions()["version"]
