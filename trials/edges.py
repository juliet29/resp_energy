from polymap.layout.interfaces import Layout
from shapely.plotting import plot_polygon
from resp.eplus.interfaces import read_geoms_to_layout
from resp.geom.edges import (
    AdjacencyObjects,
    calculate_buf_factor,
    create_subsurface_inputs,
)
from resp.geom.interfaces import (
    LayoutResults,
    clean_up_layout,
    create_layout_from_resplan,
)
from resp.readin.access import get_plan_from_subset
from loguru import logger
from rich.logging import RichHandler
from polymap.visuals.visuals import plot_layout
import shapely as sp
import matplotlib.pyplot as plt


def plot_adjacency_object_on_layout(layout: Layout, adj_objects: AdjacencyObjects):
    buf = calculate_buf_factor()
    ax = plot_layout(layout, show=False)
    plot_polygon(sp.MultiPolygon(adj_objects.get_buffered_objects("door", buf)), ax=ax)
    plt.show()


def study_their_edges():
    plan = get_plan_from_subset(ix=2)
    print(plan.graph.edges)


def study_own_edges():

    plan = get_plan_from_subset(ix=3)
    layout = create_layout_from_resplan(plan)
    cleaned_layout = clean_up_layout(layout)
    processed_layout = read_geoms_to_layout(
        plan.string_id  # pyright: ignore[reportArgumentType]
    )
    lr = LayoutResults(original=cleaned_layout, processed=processed_layout)
    edges = create_subsurface_inputs(lr, plan)

    logger.debug(edges)


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
    study_own_edges()
