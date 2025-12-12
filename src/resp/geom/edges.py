from typing import Literal, NamedTuple, Sequence
from itertools import combinations
from polymap.geometry.ortho import FancyOrthoDomain
from polymap.layout.interfaces import Layout
from replan2eplus.ops.subsurfaces.interfaces import Edge
from replan2eplus.ops.subsurfaces.user_interfaces import EdgeGroup
from utils4plans.lists import chain_flatten

from resp.paths import Constants, DynamicPaths, ResPlanIds
from resp.readin.interfaces import AdjacencyType, InputResplan
import shapely as sp
from loguru import logger
import networkx as nx

DEFAULT_WALL_WIDTH = 0.1
Geometries = sp.MultiPolygon | sp.Polygon


def print_graph_edges(G: nx.Graph):
    logger.debug("Printing graph edges....")
    for e in sorted(G.edges):
        logger.debug(sorted(e))


class AdjacencyObjects(NamedTuple):
    door: Sequence[Geometries]
    window: Sequence[Geometries]
    front_door: Sequence[Geometries]

    def get(self, t: AdjacencyType):
        return self.__getattribute__(t)

    def get_buffered_objects(self, t: AdjacencyType, buffer_size: float):
        res = list(map(lambda x: x.buffer(buffer_size), self.get(t)))
        return res


def handle_adjacency_type(geoms: sp.MultiPolygon | sp.Polygon | sp.Geometry):
    if isinstance(geoms, sp.Polygon):  # may be a line also?
        return [geoms]
    elif isinstance(geoms, sp.MultiPolygon):
        return [i for i in geoms.geoms]
    else:
        raise NotImplementedError(f"Haven't handled adjacency with type {type(geoms)}")


def get_adjacency_objects(plan: InputResplan):
    doors = handle_adjacency_type(plan.get_adjacencies_of_type("door"))
    windows = handle_adjacency_type(plan.get_adjacencies_of_type("window"))
    front_doors = handle_adjacency_type(plan.get_adjacencies_of_type("front_door"))

    return AdjacencyObjects(doors, windows, front_doors)


def calculate_buf_factor(
    wall_width: float = DEFAULT_WALL_WIDTH,
    buffer_factor=0.75,
):
    return max(
        wall_width * buffer_factor, 0.01
    )  # this is from resplan.., may need to fine tune..


def create_edge_group(
    edges: list[tuple[str, str]],
    detail: str,
    type_: Literal["Zone_Direction", "Zone_Zone"],
):
    g = nx.Graph(edges)
    es = list(map(lambda x: Edge(*x), g.edges))
    return EdgeGroup(es, detail, type_)


def get_internal_edges(
    processed_layout: Layout,
    original_layout: Layout,
    adjacency_objects_holder: AdjacencyObjects,
    adjacency_type: AdjacencyType,  # maybe can do the whole adjacency object and just a string for the type
    buffer_size: float,
):
    def find_adjacent_domains():
        combos = combinations(processed_layout.domains, 2)
        adjacent_domain_pairs: list[tuple[FancyOrthoDomain, FancyOrthoDomain]] = []
        for i, j in combos:
            if i.polygon.touches(j.polygon):
                adjacent_domain_pairs.append((i, j))
        return adjacent_domain_pairs

    adjacency_objects = adjacency_objects_holder.get_buffered_objects(
        adjacency_type, buffer_size
    )
    adjacent_domains = find_adjacent_domains()

    edges = []
    for i, j in adjacent_domains:
        i_original = original_layout.get_domain(i.name)
        j_original = original_layout.get_domain(j.name)
        for buf_obj in adjacency_objects:
            if buf_obj.intersects(i_original.polygon) and buf_obj.intersects(
                j_original.polygon
            ):
                edges.append((i.name, j.name))

    return create_edge_group(edges, adjacency_type, "Zone_Zone")


# NOTE: front door is special because only connects to living.. (https://github.com/m-agour/ResPlan/blob/main/resplan_utils.py#L247), not really ready to handle that in replan atm.., would just be used for orienting..
#


def get_external_edges(
    original_layout: Layout,
    adjacency_objects_holder: AdjacencyObjects,
    adjacency_type: AdjacencyType,
    buffer_size: float,
):

    def study_domain(domain: FancyOrthoDomain):
        edges = []
        for surf in domain.surfaces:
            line = surf.coords.shapely_line
            for obj in buf_objs:
                if line.intersects(obj):
                    edges.append((domain.name, surf.direction.name.upper()))
                    continue
        return edges

    buf_objs = adjacency_objects_holder.get_buffered_objects(
        adjacency_type, buffer_size
    )
    all_edges = map(lambda x: study_domain(x), original_layout.domains)
    res = chain_flatten(list(all_edges))

    return create_edge_group(res, adjacency_type, "Zone_Direction")


def create_subsurface_inputs(
    processed_layout: Layout, orignal_layout: Layout, plan: InputResplan
):
    adj_obj = get_adjacency_objects(plan)
    buf_size = calculate_buf_factor(wall_width=plan.wall_depth)
    logger.debug(f"wall depth = {plan.wall_depth}")

    internal_edges = get_internal_edges(
        processed_layout, orignal_layout, adj_obj, "door", buf_size
    )
    external_edges = get_external_edges(orignal_layout, adj_obj, "window", buf_size)

    return internal_edges, external_edges


def write_subsurface_inputs(
    internal: EdgeGroup, external: EdgeGroup, resplan_id: ResPlanIds
):
    path = DynamicPaths.processed_plan_geoms / resplan_id
    internal.write(path / Constants.internal_edges)
    external.write(path / Constants.external_edges)
