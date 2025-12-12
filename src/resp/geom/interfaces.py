from typing import NamedTuple
from pathlib import Path
from polymap.process.process import process_layout
from utils4plans.geom import tuple_list_from_list_of_coords
from utils4plans.io import write_json
from utils4plans.lists import chain_flatten
from polymap.geometry.ortho import FancyOrthoDomain
from polymap.layout.interfaces import Layout
from polymap.geometry.shapely_helpers import get_coords_from_shapely_polygon
import shapely as sp

from resp.paths import Constants, DynamicPaths
from resp.readin.interfaces import InputResplan, RoomType
from itertools import starmap


class RoomData(NamedTuple):
    room_type: RoomType
    ix: int
    poly: sp.Polygon

    def __rich_repr__(self):
        yield "room_type", self.room_type
        yield "ix", self.ix

    @property
    def name(self):
        return f"{self.room_type.lower()}_{self.ix}"

    @property
    def coords(self):
        return get_coords_from_shapely_polygon(self.poly)

    @property
    def ortho_domain(self):
        return FancyOrthoDomain(self.coords, self.name)


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


def clean_up_layout(layout: Layout):
    res = filter(
        lambda x: x.name
        not in ["bathroom_0", "balcony_0", "living_0", "kitchen_0", "living_1"],
        layout.domains,
    )
    kl = sp.union(
        layout.get_domain("living_0").polygon, layout.get_domain("kitchen_0").polygon
    )
    new_living = FancyOrthoDomain(
        get_coords_from_shapely_polygon(kl),  # pyright: ignore[reportArgumentType]
        name="living_0",
    )
    all_doms = list(res) + [new_living]
    return Layout(all_doms)


def create_layout_from_resplan(plan: InputResplan):
    room_data = create_room_data_for_resplan(plan)
    doms = map(lambda x: x.ortho_domain, room_data)
    l1 = Layout(list(doms))
    return l1


def write_layout(layout: Layout, file_path: Path):
    res = starmap(
        lambda ix, domain: {
            "name": domain.name,
            "id": ix,
            "coords": tuple_list_from_list_of_coords(domain.normalized_coords),
        },
        enumerate(layout.domains),
    )
    write_json(list(res), file_path / Constants.processed_geom, OVERWRITE=True)


def process_layout_and_write(plan: InputResplan):
    layout = create_layout_from_resplan(plan)
    cleaned_layout = clean_up_layout(layout)
    processed_layout = process_layout(
        other_layout_id=plan.string_id, layout=cleaned_layout
    )
    write_layout(processed_layout, DynamicPaths.processed_plan_geoms / plan.string_id)
    return cleaned_layout, processed_layout
