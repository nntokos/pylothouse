def test_import():
    import nicefigs as nf
    assert hasattr(nf, "render")
