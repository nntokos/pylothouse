def test_import():
    import pylothouse_nicefigs as nf
    assert hasattr(nf, "render")
