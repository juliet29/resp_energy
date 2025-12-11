from typing import NamedTuple
from utils4plans.lists import chain_flatten
from polymap.geometry.ortho import FancyOrthoDomain
from polymap.layout.interfaces import Layout
from polymap.geometry.shapely_helpers import get_coords_from_shapely_polygon
import shapely as sp

from resp.readin.interfaces import InputResplan, RoomType
from itertools import starmap


class RoomData(NamedTuple):
    # this was under one geom, one room regime, here have groups..
    room_type: RoomType
    ix: int
    poly: sp.Polygon

    def __rich_repr__(self):
        yield "room_type", self.room_type
        yield "ix", self.ix

    @property
    def name(self):
        return f"{self.room_type.lower()}_{self.ix}"  # TODO do the names have to be independent? -> maybe have also a type?

    # @property
    # def room(self):
    #     return Room(self.id, self.name, self.domain, self.height)

    @property
    def coords(self):
        return get_coords_from_shapely_polygon(self.poly)

    # @property
    # def tuple_coords(self):
    #     return [Coord(*i).as_tuple for i in self.poly.exterior.normalize().coords]

    @property
    def ortho_domain(self):
        return FancyOrthoDomain(self.coords, self.name)

    # @property
    # def is_orthogonal(self):
    #     return self.ortho_domain.is_orthogonal
    #


def create_room_data_from_room_type(room_type: RoomType, multipolygon: sp.MultiPolygon):
    res = starmap(
        lambda ix, geom: RoomData(room_type, ix, geom), enumerate(multipolygon.geoms)
    )
    return list(res)


def create_room_data_for_resplan(plan: InputResplan):
    res = map(
        lambda x: create_room_data_from_room_type(x, plan.get_rooms_of_type(x)),
        plan.room_types,
    )
    return chain_flatten(res)


def filter_domains(domains: list[FancyOrthoDomain]):
    res = filter(
        lambda x: x.name not in ["bathroom_0", "balcony_0", "living_0", "kitchen_0"],
        domains,
    )
    return list(res)


def create_layout_from_resplan(plan: InputResplan):
    room_data = create_room_data_for_resplan(plan)
    doms = map(lambda x: x.ortho_domain, room_data)
    filtered_doms = filter_domains(list(doms))
    return Layout(filtered_doms)
