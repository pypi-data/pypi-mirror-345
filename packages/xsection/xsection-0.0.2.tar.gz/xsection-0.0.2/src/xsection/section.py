from dataclasses import dataclass, fields
from collections.abc import Mapping



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

    @property
    def centroid(self):
        pass

    def translate(self, location):
        pass