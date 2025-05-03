import matplotlib.projections as proj

from . import colors, io, orbit, shapes
from .oifits import Oifits

proj.register_projection(Oifits)

__version__ = "1.2.3"
__all__ = ["io", "colors", "oifits", "orbit", "shapes"]
