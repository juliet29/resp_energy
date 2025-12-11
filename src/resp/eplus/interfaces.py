from typing import get_args

from pydantic import BaseModel
from replan2eplus.ezcase.ez import EZ
from replan2eplus.geometry.coords import Coord
from replan2eplus.geometry.ortho_domain import OrthoDomain
from replan2eplus.ops.zones.user_interface import Room
from utils4plans.geom import CoordsType
from utils4plans.io import read_json

from resp.config import ROOM_HEIGHT
from resp.paths import Constants, DynamicPaths, ResPlanIds


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


class GeomPlan(BaseModel):
    rooms: list[GeomRoom]

    @property
    def ezcase_rooms(self):
        res = map(lambda x: x.as_ezcase_room, self.rooms)
        return list(res)


def read_geoms_to_ezcase_rooms(layout_id: ResPlanIds):
    file_name = DynamicPaths.processed_plan_geoms / layout_id / Constants.processed_geom
    data = read_json(file_name)
    geom_plan = GeomPlan.model_validate({"rooms": data})

    return geom_plan.ezcase_rooms


def get_layout_id(ix: int = 0, show=False) -> ResPlanIds:
    path = DynamicPaths.processed_plan_geoms
    ids = [x.name for x in path.iterdir() if x.is_dir()]
    if show:
        print(ids)
    assert ix < len(ids), f"Only have {len(ids)} ids!"
    new_id = ids[ix]
    assert new_id in get_args(ResPlanIds)
    return new_id  # pyright: ignore[reportReturnType]


def test_layout_passes(layout_id: ResPlanIds):
    rooms = read_geoms_to_ezcase_rooms(layout_id)
    case = EZ()
    case.add_zones(rooms)
    case.idf.printidf()
    # ideallly plot the empty case
    return True
