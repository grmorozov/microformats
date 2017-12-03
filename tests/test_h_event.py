from tests.test_runner import run_example


def test_ampm():
    run_example('./examples/microformats-v2/h-event/ampm.json')


def test_attendees():
    run_example('./examples/microformats-v2/h-event/attendees.json')


def test_change_log():
    run_example('./examples/microformats-v2/h-event/change-log.json')


def test_combining():
    run_example('./examples/microformats-v2/h-event/combining.json')


def test_concatenate():
    run_example('./examples/microformats-v2/h-event/concatenate.json')


def test_dates():
    run_example('./examples/microformats-v2/h-event/dates.json')


def test_dt_property():
    run_example('./examples/microformats-v2/h-event/dt-property.json')


def test_just_a_hyperlink():
    run_example('./examples/microformats-v2/h-event/justahyperlink.json')


def test_just_a_name():
    run_example('./examples/microformats-v2/h-event/justaname.json')


def test_time():
    run_example('./examples/microformats-v2/h-event/time.json')
