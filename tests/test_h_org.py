from tests.test_runner import run_example


def test_hyperlink():
    run_example('./examples/microformats-v2/h-org/hyperlink.json')


def test_simple_html():
    run_example('./examples/microformats-v2/h-org/simple.json')


def test_simple_properties():
    run_example('./examples/microformats-v2/h-org/simpleproperties.json')