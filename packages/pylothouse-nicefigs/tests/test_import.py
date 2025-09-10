def test_import():
    from pylothouse import nicefigs as nf
    assert hasattr(nf, "render")
