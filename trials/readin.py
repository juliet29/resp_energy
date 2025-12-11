from resp.readin.access import get_plan_from_subset
from resp.readin.interfaces import InputResplan


def test_validate_incoming_data():

    for ix in range(10):
        res = get_plan_from_subset(ix=ix)
        # print(f"[bold yellow]\nNew Index: {ix}")
        # print(res)
        r = InputResplan(**res)
        # print(r)
    return True
