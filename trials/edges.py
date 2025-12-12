from shapely.plotting import plot_polygon
from resp.eplus.interfaces import read_geoms_to_layout
from resp.geom.edges import (
    calculate_buf_factor,
    get_adjacency_objects,
    get_external_edges,
)
from resp.geom.interfaces import clean_up_layout, create_layout_from_resplan
from resp.readin.access import get_plan_from_subset
from loguru import logger
from rich.logging import RichHandler
from polymap.visuals.visuals import plot_layout
import shapely as sp
import matplotlib.pyplot as plt


def plot_adjacency_object_on_layout(layout, adj_objects):
    buf = calculate_buf_factor()
    buf_objs = get_external_edges(layout, adj_objects, "window", buf)
    ax = plot_layout(layout, show=False)
    plot_polygon(sp.MultiPolygon(buf_objs), ax=ax)
    plt.show()


def study_edges():
    layout_id = "14877"
    plan = get_plan_from_subset(ix=2)
    print(plan.string_id)
    og_layout = clean_up_layout(create_layout_from_resplan(plan))
    clean_layout = read_geoms_to_layout(layout_id)
    adj_objects = get_adjacency_objects(plan)
    buf = calculate_buf_factor()

    # get_internal_edges(clean_layout, og_layout, adj_objects, "door", buf)
    buf_objs = get_external_edges(og_layout, adj_objects, "window", buf)
    plot_adjacency_object_on_layout(og_layout, adj_objects)

    # graph = plan_to_graph(plan.__dict__)
    #
    # print_graph_edges(graph)

    # for e in graph.edges:
    #     logger.debug(e)
    # print(graph)
    # ax = plot_plan_and_graph(plan.__dict__)
    # plt.show()


if __name__ == "__main__":
    logger.remove()
    logger.configure(
        handlers=[
            {
                "sink": RichHandler(markup=True),
                "format": "<green>{function}:: </green>{message}",
            }
        ]
    )
    study_edges()
