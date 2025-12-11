from resp.geom.interfaces import (
    create_layout_from_resplan,
)
from resp.readin.access import get_plan_from_subset
from polymap.visuals.visuals import plot_layout
from polymap.process.process import process_layout


## TRUE TESTS
def test_make_layout_from_resplan():
    plan = get_plan_from_subset()
    layout = create_layout_from_resplan(plan)
    assert len(layout.domains) > 3


# TRIALS


def test_create_room_list(plot_first=False):
    plan = get_plan_from_subset(ix=9)
    layout = create_layout_from_resplan(plan)

    if plot_first:
        plot_layout(layout, str(plan.id))
    res = process_layout(plan.id, layout)  # pyright: ignore[reportArgumentType]
    # plot_polygon(
    #     layout.get_domain("kitchen_0").polygon, title=f"{plan.id} kitchen", show=True
    # )


if __name__ == "__main__":
    test_create_room_list(plot_first=True)
