from os import walk
from os.path import join
from parser import parse_from_file
import json


def test_run_all_tests():
    pairs = {}
    base_dir = './examples/'
    for root, dirs, files in walk(base_dir):
        for file in files:
            if file.endswith('.json'):
                jf = join(root, file)
                hf = jf.replace('.json', '.html')
                pairs[hf] = jf

    for key in pairs.keys():
        parse_result = parse_from_file(key)
        with open(pairs[key], 'r') as res:
            expected = json.loads(res.read())
            assert expected == parse_result, f'Test {key} failed'


def run_example(path_to_json: str):
    path_to_html = path_to_json.replace('.json', '.html')
    parse_result = parse_from_file(path_to_html)
    with open(path_to_json, 'r') as res:
        expected = json.loads(res.read())
        print(expected)
        print(parse_result)
        assert expected == parse_result, f'Test {path_to_json} failed'
