from typing import NamedTuple, Sequence
from itertools import combinations
from polymap.geometry.ortho import FancyOrthoDomain
from polymap.layout.interfaces import Layout
from utils4plans.lists import chain_flatten

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


def handle_adjacency_type(geoms: sp.MultiPolygon | sp.Polygon | sp.Geometry):
    if isinstance(geoms, sp.Polygon):  # may be a line also?
        return [geoms]
    elif isinstance(geoms, sp.MultiPolygon):
        return [i for i in geoms.geoms]
    else:
        raise NotImplementedError(f"Haven't handled adjacency with type {type(geoms)}")


def get_adjacency_objects(plan: InputResplan):
    # adjacency_objects = map(
    #     lambda x: plan.get_adjacencies_of_type(x), plan.adjacency_types
    # )
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


def get_internal_edges(
    processed_layout: Layout,
    original_layout: Layout,
    adjacency_objects_holder: AdjacencyObjects,
    adjacency_type: AdjacencyType,  # maybe can do the whole adjacency object and just a string for the type
    buf: float,
):
    # type later becomes enum..
    combos = combinations(processed_layout.domains, 2)
    adjacent_domain_pairs: list[tuple[FancyOrthoDomain, FancyOrthoDomain]] = []
    for i, j in combos:
        if i.polygon.touches(j.polygon):
            adjacent_domain_pairs.append((i, j))

    adj_dom_edges = [(i.name, j.name) for i, j in adjacent_domain_pairs]
    Gadj = nx.Graph(adj_dom_edges)

    adjacency_objects = adjacency_objects_holder.get(adjacency_type)

    edges = []
    for i, j in adjacent_domain_pairs:
        i_original = original_layout.get_domain(i.name)
        j_original = original_layout.get_domain(j.name)
        for obj in adjacency_objects:
            buf_obj = obj.buffer(buf)
            if buf_obj.intersects(i_original.polygon) and buf_obj.intersects(
                j_original.polygon
            ):
                edges.append((i.name, j.name))

    G = nx.Graph(edges)

    print_graph_edges(Gadj)
    print_graph_edges(G)
    return edges


# NOTE: front door is special because only connects to living.. (https://github.com/m-agour/ResPlan/blob/main/resplan_utils.py#L247), not really ready to handle that in replan atm.., would just be used for orienting..
#


def get_external_edges(
    # processed_layout: Layout,
    original_layout: Layout,
    adjacency_objects_holder: AdjacencyObjects,
    adjacency_type: AdjacencyType,  # maybe can do the whole adjacency object and just a string for the type
    buf: float,
):
    objs = adjacency_objects_holder.get(adjacency_type)
    buf_objs = list(
        map(lambda x: x.buffer(buf), objs)
    )  # TODO: this can happen in the adjacency obj holder
    logger.debug(buf_objs)

    def study_domain(domain: FancyOrthoDomain):
        edges = []
        for surf in domain.surfaces:
            line = surf.coords.shapely_line
            for obj in buf_objs:
                if line.intersects(obj):
                    edges.append((domain.name, surf.direction.name))
                    continue
        return edges

    all_edges = map(lambda x: study_domain(x), original_layout.domains)
    res = chain_flatten(list(all_edges))
    G = nx.Graph(res)
    print_graph_edges(G)
    logger.debug(len(res))
    return buf_objs
