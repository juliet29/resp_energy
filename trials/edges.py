from resp.eplus.interfaces import read_geoms_to_layout
from resp.geom.edges import get_adjacency_objects, get_internal_edges, print_graph_edges
from resp.geom.interfaces import create_layout_from_resplan
from resp.readin.access import get_plan_from_subset
from loguru import logger
from rich.logging import RichHandler

from resp.resp_utils import plan_to_graph


def study_edges():
    layout_id = "14877"
    plan = get_plan_from_subset(ix=2)
    print(plan.string_id)
    og_layout = create_layout_from_resplan(plan)
    clean_layout = read_geoms_to_layout(layout_id)
    adj_objects = get_adjacency_objects(plan)

    get_internal_edges(clean_layout, og_layout, adj_objects.doors, "door")
    graph = plan_to_graph(plan.__dict__)

    print_graph_edges(graph)

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
