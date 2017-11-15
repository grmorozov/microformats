from tests.test_runner import run_example


def test_just_a_name():
    run_example('./examples/microformats-v2/h-card/justaname.json')


def test_p_property():
    run_example('./examples/microformats-v2/h-card/p-property.json')


def test_implied_name():
    run_example('./examples/microformats-v2/h-card/impliedname.json')


def test_base_url():
    run_example('./examples/microformats-v2/h-card/baseurl.json')
