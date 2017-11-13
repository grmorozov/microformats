from tests.test_runner import run_example


def test_abbrpattern():
    run_example('./examples/microformats-v2/h-geo/abbrpattern.json')


def test_altitude():
    run_example('./examples/microformats-v2/h-geo/altitude.json')


def test_hidden():
    run_example('./examples/microformats-v2/h-geo/hidden.json')


def test_just_a_name():
    run_example('./examples/microformats-v2/h-geo/justaname.json')


def test_simple_properties():
    run_example('./examples/microformats-v2/h-geo/simpleproperties.json')


def test_value_title_class():
    run_example('./examples/microformats-v2/h-geo/valuetitleclass.json')
