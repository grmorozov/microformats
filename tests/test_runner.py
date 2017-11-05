from os import walk
from os.path import join
from parser import parse
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
        with open(key, 'r') as html:
            doc = html.read()
            p = parse(doc)
            with open(pairs[key], 'r') as res:
                expected = json.loads(res.read())
                assert expected == p, f'Test {key} failed'


def run_example(path_to_json: str):
    path_to_html = path_to_json.replace('.json', '.html')
    with open(path_to_html, 'r') as html:
        doc = html.read()
        p = parse(doc)
        with open(path_to_json, 'r') as res:
            expected = json.loads(res.read())
            assert expected == p, f'Test {path_to_json} failed'
