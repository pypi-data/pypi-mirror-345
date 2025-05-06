import os
import sys

# Ensure DLL search path is correct (Python >=3.8)
if sys.version_info >= (3, 8):
    os.add_dll_directory(os.path.dirname(__file__))

from .z3scn import *  # This imports all public functions and classes

__all__ = ['init', 'terminate', 'get_device_info', 'go_home', 'go_center', 'go_position', 'load_position', 'check_scn', 'submit_check', 'submit', 'set_speed', 'set_accel', 'set_default_speed', 'set_speed_accel']
