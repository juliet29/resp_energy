import networkx as nx
import shapely as sp
from pydantic import BaseModel, ConfigDict


class InputResplan(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    balcony: sp.MultiPolygon
    bathroom: sp.MultiPolygon
    bedroom: sp.MultiPolygon
    door: sp.MultiPolygon
    garden: sp.MultiPolygon
    inner: sp.MultiPolygon
    parking: sp.MultiPolygon
    pool: sp.MultiPolygon
    stair: sp.MultiPolygon
    veranda: sp.MultiPolygon
    wall: sp.MultiPolygon
    window: sp.MultiPolygon
    front_door: sp.Polygon
    # might be an enum
    unitType: str
    id: int
    kitchen: sp.MultiPolygon
    land: sp.MultiPolygon
    net_area: float
    area: float
    neighbor: list[sp.MultiPolygon | sp.Polygon]
    living: sp.MultiPolygon
    wall_depth: float
    storage: sp.MultiPolygon
    graph: nx.Graph
