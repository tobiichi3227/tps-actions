import json
import os

problems = json.loads(os.environ.get('PROBLEMS'))
changes = json.loads(os.environ.get('CHANGES'))
keys = ['input', 'solutions', 'pdf', 'any']
prefixes = {}
for pro in problems:
    prefixes['p{}/'.format(pro)] = pro

result = {}
result['template'] = changes['template']
result['cover'] = changes['cover']
for key in keys:
    result[key] = {}
    for pro in problems:
        result[key][pro] = 'false'
        if key == 'pdf':
            result[key][pro] = changes['template']
    for file in json.loads(changes['{}_files'.format(key)]):
        for prefix, pro in prefixes.items():
            if file.startswith(prefix):
                result[key][pro] = 'true'
                break
result['output'] = {}
solutions_files = json.loads(changes['solutions_files'])
for pro in problems:
    result['output'][pro] = 'false'
    with open('p{}/solutions.json'.format(pro), 'r', encoding='utf8') as f:
        solutions = json.load(f)
    for file, val in solutions.items():
        if val.get('verdict') == 'model_solution':
            if 'p{}/solution/{}'.format(pro, file) in solutions_files:
                result['output'][pro] = 'true'
                result['solutions'][pro] = 'true'
            break

print('::set-output name=changes::{}'.format(json.dumps(result)))
