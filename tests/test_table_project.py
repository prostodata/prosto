import pytest

from prosto.Prosto import *

def test_one_key():
    sch = Prosto("My Prosto")

    # Facts
    f_tbl = sch.populate(
        table_name="Facts", attributes=["A"],
        func="lambda **m: pd.DataFrame({'A': ['a', 'a', 'b', 'b']})", tables=[]
    )

    # Groups
    g_tbl = sch.project(
        table_name="Groups", attributes=["X"],
        link="Link",
        tables=["Facts"]
    )

    # Link
    l_clm = sch.link(
        name="Link", table=f_tbl.id, type=g_tbl.id,
        columns=["A"], linked_columns=["X"]
    )

    f_tbl.evaluate()
    g_tbl.evaluate()

    l_clm.evaluate()

    g_tbl_data = g_tbl.get_df()
    assert len(g_tbl_data) == 2
    assert len(g_tbl_data.columns) == 1

    l_data = f_tbl.get_column_series("Link")
    assert l_data[0] == 0
    assert l_data[1] == 0
    assert l_data[2] == 1
    assert l_data[3] == 1

    #
    # Test topology
    #
    topology = Topology(sch)
    topology.translate()
    layers = topology.elem_layers

    assert len(layers) == 3

    assert set([x.id for x in layers[0]]) == set(["Facts"])
    assert set([x.id for x in layers[1]]) == set(["Groups"])
    assert set([x.id for x in layers[2]]) == set(["Link"])

def test_two_keys():
    sch = Prosto("My Prosto")

    # Facts
    f_tbl = sch.populate(
        table_name="Facts", attributes=["A", "B"],
        func="lambda **m: pd.DataFrame({'A': ['a', 'b', 'b', 'a'], 'B': ['b', 'c', 'c', 'a']})", tables=[]
    )

    # Groups
    g_tbl = sch.project(
        table_name="Groups", attributes=["X", "Y"],
        link="Link",
        tables=["Facts"]
    )

    # Link
    l_clm = sch.link(
        name="Link", table=f_tbl.id, type=g_tbl.id,
        columns=["A", "B"], linked_columns=["X", "Y"]
    )

    f_tbl.evaluate()
    g_tbl.evaluate()

    l_clm.evaluate()

    g_tbl_data = g_tbl.get_df()
    assert len(g_tbl_data) == 3
    assert len(g_tbl_data.columns) == 2

    l_data = f_tbl.get_column_series("Link")
    assert l_data[0] == 0
    assert l_data[1] == 1
    assert l_data[2] == 1
    assert l_data[3] == 2

    #
    # Test topology
    #
    topology = Topology(sch)
    topology.translate()
    layers = topology.elem_layers

    assert len(layers) == 3

    assert set([x.id for x in layers[0]]) == set(["Facts"])
    assert set([x.id for x in layers[1]]) == set(["Groups"])
    assert set([x.id for x in layers[2]]) == set(["Link"])

    g_tbl_data = g_tbl.get_df()
    g_tbl_data.drop(g_tbl_data.index, inplace=True)  # Empty

    sch.run()

    g_tbl_data = g_tbl.get_df()
    assert len(g_tbl_data) == 3
    assert len(g_tbl_data.columns) == 2
