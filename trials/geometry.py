import shapely as sp
from shapely.plotting import plot_polygon
from resp.geom.interfaces import (
    create_layout_from_resplan,
    process_layout_and_write,
)
from resp.readin.access import get_plan_from_subset
from polymap.visuals.visuals import plot_layout, plot_polygon
from polymap.process.process import process_layout


## TRUE TESTS
def test_make_layout_from_resplan():
    plan = get_plan_from_subset()
    layout = create_layout_from_resplan(plan)
    assert len(layout.domains) > 3


# TRIALS


def test_create_room_list(plot_first=False):
    plan = get_plan_from_subset(ix=2)
    layout = create_layout_from_resplan(plan)

    test_union = False
    if test_union:

        kl = sp.union(
            layout.get_domain("living_0").polygon,
            layout.get_domain("kitchen_0").polygon,
        )
        plot_polygon(
            kl, title="kl union", show=True
        )  # pyright: ignore[reportArgumentType]

    if plot_first:
        plot_layout(layout, str(plan.id))
    res = process_layout(plan.id, layout)  # pyright: ignore[reportArgumentType]
    # plot_polygon(
    #     layout.get_domain("kitchen_0").polygon, title=f"{plan.id} kitchen", show=True
    # )


def test_write_geom():
    plan = get_plan_from_subset(ix=2)
    process_layout_and_write(plan)


if __name__ == "__main__":
    test_write_geom()
