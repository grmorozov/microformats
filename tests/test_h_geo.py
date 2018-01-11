from tests.test_runner import run_example
import os
dir_path = os.path.dirname(os.path.realpath(__file__))


def test_abbrpattern():
    run_example(dir_path + '/examples/microformats-v2/h-geo/abbrpattern.json')


def test_altitude():
    run_example(dir_path + '/examples/microformats-v2/h-geo/altitude.json')


def test_hidden():
    run_example(dir_path + '/examples/microformats-v2/h-geo/hidden.json')


def test_just_a_name():
    run_example(dir_path + '/examples/microformats-v2/h-geo/justaname.json')


def test_simple_properties():
    run_example(dir_path + '/examples/microformats-v2/h-geo/simpleproperties.json')


def test_value_title_class():
    run_example(dir_path + '/examples/microformats-v2/h-geo/valuetitleclass.json')
