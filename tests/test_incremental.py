import pytest

from prosto.Prosto import *

def test_calculate_value():
    sch = Prosto("My Prosto")
    sch.incremental = True

    tbl = sch.create_table(
        table_name="My table", attributes=["A"],
    )

    clm = sch.calculate(
        name="My column", table=tbl.id,
        func="lambda x: float(x)", columns=["A"], model=None
    )

    sch.run()  # Inference on empty data

    tbl.data.add({"A": 1})  # New record is added and marked as added

    # Assert new change status
    assert tbl.data.added_length() == 1

    sch.run()

    # Assert clean change status and results of inference
    assert tbl.data.added_length() == 0

    tbl.data.add({"A": 2})
    tbl.data.add({"A": 3})

    # Assert new change status
    assert tbl.data.added_length() == 2

    # For debug purpose, modify an old row (which has not been recently added but was evaluated before)
    tbl_df = tbl.data.get_df()
    tbl_df['A'][0] = 10  # Old value is 1. Prosto does not see this change

    sch.run()

    # The manual modification is invisible for Prosto and hence it should not be re-computed and the derived column will have to have the old value
    assert tbl_df['My column'][0] == 1

    # Assert clean change status and results of inference
    assert tbl.data.added_length() == 0

    tbl.data.remove(1)  # Remove one oldest record by marking it as removed

    # Assert new change status
    assert tbl.data.removed_length() == 1

    sch.run()

    # Assert clean change status and results of inference
    assert tbl.data.removed_length() == 0

    tbl.data.remove_all()  # Remove all records by marking them as removed

    # Assert new change status

    sch.run()

    # Assert clean change status and results of inference
    assert tbl.data.added_range.start == 3
    assert tbl.data.added_range.end == 3
    assert tbl.data.removed_range.start == 3
    assert tbl.data.removed_range.end == 3
