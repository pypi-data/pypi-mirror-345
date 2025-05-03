# Claudio Perez
"""
A patch is used to generate a number of fibers over a cross-sectional area. 
Currently there are three types of patches that fibers can be generated over: 
quadrilateral, rectangular and circular.

"""
import sys
from dataclasses import dataclass
from shps.frame import WarpingSection
from opensees.library.ast import Tag, Num, Blk, Ref, Flg, Map
from ..polygon import PolygonSection

from opensees.library.ast import Grp, Num, Ref
import numpy as np

class Material: pass
class Backbone: pass

@dataclass
class _Fiber:
    """
    This class represents a single fiber in an enclosing `FiberSection`
    """
    tag_space = None
    # fiber $yLoc $zLoc $A $material
    _args = [
        Grp("coord", args=[Num("x"), Num("y")], reverse=True,
            about="$x$ and $y$ coordinate of the fiber in the section "\
                  "(local coordinate system)"),
        Num("area", about="area of the fiber."),
        Ref("material", type=Material,
            about="material tag associated with this fiber (UniaxialMaterial tag"\
                  "for a FiberSection and NDMaterial tag for use in an NDFiberSection)."),
    ]
    
    @property
    def fibers(self):
        yield self

_eps = 0.00001
_huge = sys.float_info.max
_tiny = sys.float_info.min


def _distance(a,b):
    return np.linalg.norm(a-b)


def _clip_sections(sections):
    """
    Preprocess a list of section objects by resolving overlaps using z-order priority.

    Parameters
    ----------
    sections : list
        Section-like objects with methods:
          - exterior() -> (N,2) array
          - interior() -> list of (M,2) arrays
          - material : int
          - z : int (optional, defaults to 0)

    Returns
    -------
    list
        List of non-overlapping PolygonSection objects with resolved priority.
    """
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    from collections import defaultdict
    import numpy as np

    # Group by z-level
    grouped = defaultdict(list)
    for section in sections:
        z = getattr(section, "z", 0)
        grouped[z].append(section)

    # Process from highest to lowest z
    output = []
    current_union = None

    for z in sorted(grouped.keys(), reverse=True):
        for section in grouped[z]:
            shell = section.exterior()
            holes = section.interior()
            poly = Polygon(shell, holes)

            # Step 1: add this section as-is (always)
            if not poly.is_empty:
                for geom in (poly.geoms if poly.geom_type == "MultiPolygon" else [poly]):
                    ext = np.array(geom.exterior.coords)
                    ints = [np.array(ring.coords) for ring in geom.interiors]
                    new_section = PolygonSection(ext, ints,
                                                 mesh_size=section.mesh_size,
                                                 material=section.material)
                    output.append(new_section)

            # Step 2: update the union mask *after* adding this
            current_union = poly if current_union is None else unary_union([current_union, poly])

        # Step 3: clip lower-z sections (in next iteration) against updated union

    return output


def _mesh_cytri(sections, mesh_size=0.05, min_angle=25.0, coarse=False):
    """
    Generate a triangular mesh with material interfaces preserved using Shewchuk's Triangle.

    Parameters
    ----------
    sections : list
        List of section-like objects, each with:
          - exterior() -> (N,2) array
          - interior() -> list of (M,2) arrays
          - material : int
    mesh_size : float or dict[int, float]
        Target element size(s), either a uniform float or a dict mapping material -> size.
    min_angle : float
        Minimum angle constraint (in degrees).
    coarse : bool
        If True, use a coarse mesh with no quality or area constraints.

    Returns
    -------
    dict
        Mesh dictionary with 'vertices', 'triangles', etc., and preserved material interfaces.
    """
    import cytriangle as triangle
    import numpy as np

    vertex_map = {}
    points = []
    facets = []
    holes = []
    control_points = []
    mesh_sizes = []

    def get_vertex_index(pt):
        key = tuple(np.round(pt, 12))  # prevent numerical duplicates
        if key in vertex_map:
            return vertex_map[key]
        idx = len(points)
        points.append(key)
        vertex_map[key] = idx
        return idx

    for region_id, section in enumerate(sections):
        ext = section.exterior()
        interiors = section.interior()
        material = section.material

        # Exterior
        ext_idx = [get_vertex_index(p) for p in ext]
        facets.extend([(ext_idx[i], ext_idx[(i + 1) % len(ext_idx)]) for i in range(len(ext_idx))])

        # Interiors (holes)
        for hole in interiors:
            hole_idx = [get_vertex_index(p) for p in hole]
            facets.extend([(hole_idx[i], hole_idx[(i + 1) % len(hole_idx)]) for i in range(len(hole_idx))])
            holes.append(tuple(np.mean(hole, axis=0)))

        # Control point for region interior
        control_points.append(tuple(np.mean(ext, axis=0)))

        # Region mesh size
        if isinstance(mesh_size, dict):
            mesh_sizes.append(mesh_size.get(material, 0.05))
        else:
            mesh_sizes.append(mesh_size)

    # Prepare Triangle input
    tri = {
        "vertices": points,
        "segments": facets,
        "holes": holes,
        "regions": [
            [cp[0], cp[1], i, mesh_sizes[i][0]]
            for i, cp in enumerate(control_points)
        ]
    }
    for i, r in enumerate(tri["regions"]):
        if len(r) != 4 or not all(isinstance(v, (float, int)) for v in r):
            raise ValueError(f"Bad region entry at index {i}: {r}")

    opts = "pA" if coarse else f"pq{min_angle:.1f}Aa"
    if False:
        # Quadratic (6-node) triangles
        opts += "o2"

    data = triangle.triangulate(tri, opts)


    points = np.array(data["vertices"], dtype=np.float64)

    # Quadratic triangles are 6-node triangles (3 vertices + 3 mid-side nodes)
    # Meshio uses "triangle6" for this
    cells = [("triangle6", np.array(data["triangles"], dtype=np.int32))]

    # Optional cell data (e.g., region markers)
    cell_data = {}
    if "triangle_attributes" in data:
        triangle_attr = np.array(data["triangle_attributes"]).flatten()
        cell_data = {"region": [triangle_attr]}
    import meshio
    return meshio.Mesh(
        points=points,
        cells=cells,
        cell_data=cell_data
    )
    return mesh



def _create_mesh_cyt(
    points: list[tuple[float, float]],
    facets: list[tuple[int, int]],
    holes: list[tuple[float, float]],
    control_points: list[tuple[float, float]],
    mesh_sizes: list[float] | float,
    min_angle: float,
    coarse: bool,
) -> dict[str, list[list[float]] | list[list[int]]]:
    """Generates a triangular mesh.

    Creates a quadratic triangular mesh using the ``CyTriangle`` module, which utilises
    the code ``Triangle``, by Jonathan Shewchuk.

    Args:
        points: List of points (``x``, ``y``) defining the vertices of the cross-section
        facets: List of point index pairs (``p1``, ``p2``) defining the edges of the
            cross-section
        holes: List of points (``x``, ``y``) defining the locations of holes within the
            cross-section. If there are no holes, provide an empty list [].
        control_points: A list of points (``x``, ``y``) that define different regions of
            the cross-section. A control point is an arbitrary point within a region
            enclosed by facets.
        mesh_sizes: List of maximum element areas for each region defined by a control
            point
        min_angle: The meshing algorithm adds vertices to the mesh to ensure that no
            angle smaller than the minimum angle (in degrees, rounded to 1 decimal
            place). Note that small angles between input segments cannot be eliminated.
            If the minimum angle is 20.7 deg or smaller, the triangulation algorithm is
            theoretically guaranteed to terminate (given sufficient precision). The
            algorithm often doesn't terminate for angles greater than 33 deg. Some
            meshes may require angles well below 20 deg to avoid problems associated
            with insufficient floating-point precision.
        coarse: If set to True, will create a coarse mesh (no area or quality
            constraints)

    Returns:
        Dictionary containing mesh data
    """
    import cytriangle as triangle
    if not isinstance(mesh_sizes, list):
        mesh_sizes = [mesh_sizes]

    tri = {}                  # create tri dictionary
    tri["vertices"] = points  # set point
    tri["segments"] = facets  # set facets

    if holes:
        tri["holes"] = holes  # set holes

    # prepare regions
    regions = []

    for i, cp in enumerate(control_points):
        rg = [cp[0], cp[1], i, mesh_sizes[i]]
        regions.append(rg)

    tri["regions"] = regions  # set regions

    # generate mesh
    if coarse:
        mesh = triangle.triangulate(tri, "pAo2")
    else:
        mesh = triangle.triangulate(tri, f"pq{min_angle:.1f}Aao2")

    return mesh

class CompositeSection(WarpingSection):

    def __init__(self, patches, **kwds):
        self._patches = _clip_sections(patches)
        self._fibers = None
        self._mesh_size = [min(patch.mesh_size for patch in patches),
                           min(patch.mesh_size for patch in patches)]
        self._mesher = kwds.get("mesher", "gmsh")
        self._c_model = None
        self._area   = None
        if "material" in kwds:
            mat = kwds["material"]
            for i in self._patches:
                if i.material is None:
                    i.material = mat

    def add_patch(self, patch):
        self._fibers = None
        self._patches.append(patch)

    def add_patches(self, patch):
        self._fibers = None
        self._patches.extend(patch)

    def exterior(self):

        import shapely.geometry
        from shapely.ops import unary_union

        shapes = []

        for patch in self._patches:
            shapes.append(shapely.geometry.Polygon(patch.exterior(),
                                                   patch.interior()))
            
        if len(shapes) > 1:
            return unary_union(shapes).exterior.coords
        else:
            return shapes[0].exterior.coords

    @property 
    def model(self):
        if self._c_model is None:
            self._c_model = self._create_mesh(self._mesh_size, engine=self._mesher) 
        return self._c_model

    def _create_mesh(self, mesh_size: list=None, engine=None):
        patches = self._patches

        if engine is None:
            engine = "gmsh"
        # points = np.array(
        #     [*self.exterior()]+sum([list(p.interior()) for p in self._patches], [])
        # )
        mesh = _mesh_cytri(self._patches, mesh_size=mesh_size, min_angle=25.0)

        # if engine == "gmsh":
        #     from ._meshing import sect2gmsh
        #     mesh = sect2gmsh(patches, mesh_size)

        # elif engine == "dmsh":
        #     from ._meshing import sect2dmsh
        #     mesh = sect2dmsh(patches, mesh_size)

        # elif engine == "meshpy":
        #     from ._meshing import sect2meshpy
        #     mesh = sect2meshpy(patches, mesh_size)

        from shps.frame.solvers import TriangleModel
        return TriangleModel.from_meshio(mesh)

    @property
    def patches(self):
        return [p for p in self._patches if p.get_cmd()[0] == "patch"]

    @property
    def fibers(self):
        if self._fibers is None:
            self._fibers = [
             f for a in (a.fibers if hasattr(a,"fibers") else [a] for a in self._patches)
                for f in a
            ]
        return self._fibers

    @property
    def area(self):
        if self._area is None:
            self._area = sum(i.area for i in self._patches)
        return self._area


    @property
    def ixc(self):
        # TODO: cache
        yc = self.centroid[1]
        return sum(
            p.ixc + (p.centroid[1] - yc)**2*p.area for p in self._patches
        )

    @property
    def iyc(self):
        # TODO: cache
        xc = self.centroid[0]
        return sum(
            p.iyc + (p.centroid[0]-xc)**2*p.area for p in self._patches
        )

    @property
    def moic(self):
        # TODO: cache
        return [
            [p.moi[i] + p.centroid[i]**2*p.area for i in range(2)] + [p.moi[-1]]
            for p in self._patches
        ]

    def __contains__(self, point):
        return any(point in area for area in self._shapes)