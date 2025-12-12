from typing import get_args

from polymap.geometry.ortho import FancyOrthoDomain
from polymap.layout.interfaces import Layout
from pydantic import BaseModel
from replan2eplus.geometry.coords import Coord
from replan2eplus.geometry.ortho_domain import OrthoDomain
from replan2eplus.ops.subsurfaces.interfaces import Edge, Location
from replan2eplus.ops.subsurfaces.user_interfaces import (
    Detail,
    Dimension,
    EdgeGroup,
    EdgeGroupType,
)
from replan2eplus.ops.zones.user_interface import Room
from utils4plans.geom import CoordsType, coords_type_list_to_coords
from utils4plans.io import read_json

from resp.config import ROOM_HEIGHT
from resp.paths import Constants, DynamicPaths, ResPlanIds
from resp.readin.interfaces import AdjacencyType


# more like a util..
def get_layout_id(ix: int = 0, show=False) -> ResPlanIds:
    path = DynamicPaths.processed_plan_geoms
    ids = [x.name for x in path.iterdir() if x.is_dir()]
    if show:
        print(ids)
    assert ix < len(ids), f"Only have {len(ids)} ids!"
    new_id = ids[ix]
    assert new_id in get_args(ResPlanIds)
    return new_id  # pyright: ignore[reportReturnType]


class GeomRoom(BaseModel):
    name: str
    id: int
    coords: CoordsType

    @property
    def ortho_domain(self):
        coords = map(lambda x: Coord(*x), self.coords)
        return OrthoDomain(list(coords))

    @property
    def as_ezcase_room(self):
        return Room(self.id, self.name, self.ortho_domain, ROOM_HEIGHT)

    @property
    def polymap_ortho_domain(self):
        coords = coords_type_list_to_coords(self.coords)
        return FancyOrthoDomain(coords, self.name)


class GeomPlan(BaseModel):
    rooms: list[GeomRoom]

    @property
    def ezcase_rooms(self):
        res = map(lambda x: x.as_ezcase_room, self.rooms)
        return list(res)

    @property
    def layout(self):
        res = map(lambda x: x.polymap_ortho_domain, self.rooms)
        return Layout(list(res))


def read_geoms_to_ezcase_rooms(layout_id: ResPlanIds):
    file_name = DynamicPaths.processed_plan_geoms / layout_id / Constants.processed_geom
    data = read_json(file_name)
    geom_plan = GeomPlan.model_validate({"rooms": data})

    return geom_plan.ezcase_rooms


# also a util..
def read_geoms_to_layout(layout_id: ResPlanIds):
    file_name = (
        DynamicPaths.processed_plan_geoms / layout_id / Constants.processed_geom
    )  # TODO: put this in a function..
    data = read_json(file_name)
    geom_plan = GeomPlan.model_validate({"rooms": data})

    return geom_plan.layout


class EdeGroupModel(BaseModel):
    edges: list[tuple[str, str]]
    detail: str
    type_: EdgeGroupType

    @property
    def edge_group(self):
        edges = map(lambda x: Edge(*x), self.edges)
        return EdgeGroup(list(edges), self.detail, self.type_)


def read_edges(layout_id: ResPlanIds):
    def read(file_name: str):
        path = (
            DynamicPaths.processed_plan_geoms / layout_id / file_name
        )  # TODO: put this in a function..
        data = read_json(path)
        edge_group = EdeGroupModel.model_validate(data)
        return edge_group

    in_edges = read(Constants.internal_edges).edge_group
    out_edges = read(Constants.external_edges).edge_group

    return [in_edges, out_edges]


def make_details():
    door_detail = Detail(
        Dimension(width=10, height=ROOM_HEIGHT * 0.7),
        location=Location(
            "bm", "SOUTH", "SOUTH"
        ),  # TODO: create list of reasonable defaults, so dont have to think about this..
        type_="Door",
    )
    window_detail = Detail(
        Dimension(width=10, height=ROOM_HEIGHT * 0.5),
        location=Location("mm", "CENTROID", "CENTROID"),
        type_="Window",
    )

    detail_map: dict[AdjacencyType, Detail] = {
        "window": window_detail,
        "door": door_detail,
    }
    return detail_map
