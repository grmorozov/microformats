from tests.test_runner import run_example
import os
dir_path = os.path.dirname(os.path.realpath(__file__))


def test_hyperlink():
    run_example(dir_path + '/examples/microformats-v2/h-org/hyperlink.json')


def test_simple_html():
    run_example(dir_path + '/examples/microformats-v2/h-org/simple.json')


def test_simple_properties():
    run_example(dir_path + '/examples/microformats-v2/h-org/simpleproperties.json')