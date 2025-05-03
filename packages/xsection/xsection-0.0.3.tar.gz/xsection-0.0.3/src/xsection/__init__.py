from dataclasses import dataclass, fields
from collections.abc import Mapping
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


@dataclass
class PlasticConstants(Mapping):
    Zy: float
    Zz: float
    Sy: float
    Sz: float

    def __getitem__(self, key):
        # Allows accessing attributes by key.
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(key)

    def __iter__(self):
        # Iterate over field names.
        return (f.name for f in fields(self))

    def __len__(self):
        # Number of fields.
        return len(fields(self))


@dataclass
class ElasticConstants(Mapping):
    Iy: float
    Iz: float
    A:  float
    Ay: float 
    Az: float
    J:  float
    E:  float
    G:  float = 0

    Iyz: float = 0

    def __getitem__(self, key):
        # Allows accessing attributes by key.
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(key)

    def __iter__(self):
        # Iterate over field names.
        return (f.name for f in fields(self))

    def __len__(self):
        # Number of fields.
        return len(fields(self))

    def centroid(self):
        pass

    def translate(self, location):
        pass