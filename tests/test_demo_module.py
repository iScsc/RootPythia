from src.demo_module import demo_func


def test_demo_func(demo_fixture):
    # I get the object returned from the fixture (not mandatory but makes the 
    # code clearer)
    my_obj = demo_fixture

    # I compute the expected value (can be parametrized !!!)
    expected = my_obj.demo_attr + 1

    # I actually test the func to be tested (with a crafted object from the
    # fixture ;) )
    demo_func(my_obj)

    # I finally check that the demo_func worked as expected, 
    # the most interesing point here is that both the attribute and 
    # the expected value can be parametrize
    # see https://docs.pytest.org/en/7.2.x/how-to/parametrize.html
    assert getattr(my_obj, "demo_attr") == expected
