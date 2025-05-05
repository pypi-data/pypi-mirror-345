import os
import sys

utils_dir = os.path.dirname(os.path.abspath(__file__))
if utils_dir not in sys.path:
    sys.path.append(utils_dir)