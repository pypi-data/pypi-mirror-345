import importlib.metadata

__author__ = "Ivan Zanardi"
__email__ = "ivan.zanardi.us@gmail.com"
__url__ = "https://github.com/ivanZanardi/pyharmx"
__license__ = "NCSA Open Source License"
__version__ = importlib.metadata.version("pyharmx")
__all__ = ["PolyHarmInterpolator"]

from .interpolator import PolyHarmInterpolator
