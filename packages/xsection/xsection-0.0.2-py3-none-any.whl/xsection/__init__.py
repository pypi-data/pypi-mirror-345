from ._types import SectionType
from .polygon import PolygonSection
# from .annulus import Annulus
from .composite import CompositeSection

class Material:
    E : float = 0
    G : float = 0
    Fy: float = 0

class Section(SectionType):
    _is_fiber:     bool
    _is_shape:     bool
    _is_model:     bool

    # For parsing
    def __init__(self,
                 elastic=None,
                 plastic=None,
                 composite=False,
                 fiber=None,
                 model=None,
                 mesh = None,
                 shape=None):
        pass

    def translate(self, location): ... 
    def rotate(self,    angle: float): ...

    def create_fibers(self, mesh_scale=None, **kwds): ...


    @property
    def u(self, args): pass

