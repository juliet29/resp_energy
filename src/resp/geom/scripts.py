from resp.geom.edges import write_subsurface_inputs
from resp.geom.interfaces import process_layout_and_write
from resp.paths import DynamicPaths
from resp.readin.access import get_plan_from_subset


# TODO: this should be more structured.. subset should have it's length recorded..
def write_resplans_from_subset():
    for i in range(10):
        plan = get_plan_from_subset(DynamicPaths.rp10, i)
        try:
            layout_result = process_layout_and_write(plan)
        except Exception as e:
            print(f"Failure for ix={i}, plan={plan.string_id}: {e}")
            continue

        write_subsurface_inputs(layout_result, plan)


if __name__ == "__main__":
    write_resplans_from_subset()
    # TODO: make a cli that will rin this.. , then can generate and run simulatneously..
