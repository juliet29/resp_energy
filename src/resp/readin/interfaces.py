import networkx as nx
import shapely as sp
from pydantic import BaseModel, ConfigDict
from typing import Literal, get_args


RoomType = Literal[
    "bedroom",
    "kitchen",
    "living",
    "bathroom",
    "storage",
    "veranda",
    "balcony",
    "stair",
]
AdjacencyType = Literal["door", "window", "front_door"]


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

    @property
    def string_id(self):
        return str(self.id)

    @property
    def adjacency_types(self):
        return get_args(AdjacencyType)

    @property
    def room_types(self):
        return get_args(RoomType)

    def get_rooms_of_type(self, room_type: RoomType):
        return self.__getattribute__(room_type)

    def get_adjacencies_of_type(self, adjacancy_type: AdjacencyType):
        return self.__getattribute__(adjacancy_type)

    # def get_rooms(self):
    #     return {k: self.__getattribute__(k) for k in self.room_types}
