import os, glob

from .HyHelper_traj import *
from .HyHelper_plot import *
from .HyHelper_filters import *
from .AutoSplit import *

print('All files imported successfully. Welcome to HyHelper!')

#modules = glob.glob(os.path.join(os.path.dirname(__file__), "*.py"))
#__all__ = [os.path.basename(f)[:-3] for f in modules if not f.endswith("__init__.py")]
#__version__ = "0.0.1"