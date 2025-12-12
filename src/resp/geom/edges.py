from typing import NamedTuple, Sequence
from itertools import combinations
from polymap.geometry.ortho import FancyOrthoDomain
from polymap.layout.interfaces import Layout

from resp.readin.interfaces import InputResplan
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
    doors: Sequence[Geometries]
    windows: Sequence[Geometries]
    front_door: Sequence[Geometries]


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


def get_internal_edges(
    processed_layout: Layout,
    original_layout: Layout,
    adjacency_objects: Sequence[Geometries],
    adjacency_type: str,
    wall_width: float = DEFAULT_WALL_WIDTH,
    buffer_factor=0.75,
):
    # type later becomes enum..
    buf = max(
        wall_width * buffer_factor, 0.01
    )  # this is from resplan.., may need to fine tune..

    combos = combinations(processed_layout.domains, 2)
    adjacent_domain_pairs: list[tuple[FancyOrthoDomain, FancyOrthoDomain]] = []
    for i, j in combos:
        if i.polygon.touches(j.polygon):
            adjacent_domain_pairs.append((i, j))

    adj_dom_edges = [(i.name, j.name) for i, j in adjacent_domain_pairs]
    Gadj = nx.Graph(adj_dom_edges)

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
