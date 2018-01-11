from tests.test_runner import run_example
import os
dir_path = os.path.dirname(os.path.realpath(__file__))


def test_just_a_name():
    run_example(dir_path + '/examples/microformats-v2/h-card/justaname.json')


def test_p_property():
    run_example(dir_path + '/examples/microformats-v2/h-card/p-property.json')


def test_implied_name():
    run_example(dir_path + '/examples/microformats-v2/h-card/impliedname.json')


def test_base_url():
    run_example(dir_path + '/examples/microformats-v2/h-card/baseurl.json')
