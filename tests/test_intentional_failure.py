def test_will_fail_to_demonstrate_ci():
    """This test fails on purpose to show CI catches broken code."""
    assert 1 == 2, "This should fail to prove CI is working"
