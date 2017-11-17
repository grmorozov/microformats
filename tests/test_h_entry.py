from tests.test_runner import run_example


def test_encoding():
    run_example('./examples/microformats-v2/h-entry/encoding.json')


def test_implied_value_nested():
    run_example('./examples/microformats-v2/h-entry/impliedvalue-nested.json')


def test_just_a_hyperlink():
    run_example('./examples/microformats-v2/h-entry/justahyperlink.json')


def test_just_a_name():
    run_example('./examples/microformats-v2/h-entry/justaname.json')


def test_script_style_tags():
    run_example('./examples/microformats-v2/h-entry/scriptstyletags.json')


def test_summary_content():
    run_example('./examples/microformats-v2/h-entry/summarycontent.json')


def test_u_property():
    run_example('./examples/microformats-v2/h-entry/u-property.json')


def test_url_in_content():
    run_example('./examples/microformats-v2/h-entry/urlincontent.json')
