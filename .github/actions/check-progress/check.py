import glob
import json
import os
import sys

os.chdir(os.environ.get('GITHUB_WORKSPACE'))

with open('.problems.json', 'r') as f:
    problems = json.load(f)

output = ''


def load_json(path):
    try:
        with open(path, 'r') as f:
            return json.load(f), None
    except json.JSONDecodeError as e:
        error = f'line {e.lineno}, column {e.colno}: {e.msg}'
        print(f'{path}: JSON syntax error: {error}', file=sys.stderr)
        return {}, error


# cover
if os.path.exists('cover.tex'):
    with open('cover.tex', 'r') as f:
        content = f.read()
    if 'TODO' in content:
        icon = ':x:'
    else:
        icon = ':white_check_mark:'
    output += f'- cover.tex [{icon}](cover.tex)\n'

# appendix
if os.path.exists('appendix.tex'):
    with open('appendix.tex', 'r') as f:
        content = f.read()
    if 'TODO' in content:
        icon = ':x:'
    else:
        icon = ':white_check_mark:'
    output += f'- appendix.tex [{icon}](appendix.tex)\n'

output += '\n'

output += '| |'
for pro in problems:
    output += f' {pro} |'
output += '\n'

output += '|'
for _ in range(len(problems) + 1):
    output += ' --- |'
output += '\n'

# problem.json
problemjson = {}
problemjson_errors = {}
for pro in problems:
    path = f'p{pro}/problem.json'
    problemjson[pro], problemjson_errors[pro] = load_json(path)

# subtasks.json
subtasksjson = {}
subtasksjson_errors = {}
for pro in problems:
    path = f'p{pro}/subtasks.json'
    subtasksjson[pro], subtasksjson_errors[pro] = load_json(path)

# JSON syntax
output += '| problem.json syntax |'
for pro in problems:
    if problemjson_errors[pro] is None:
        output += f' [:white_check_mark:](p{pro}/problem.json) |'
    else:
        output += f' [:x:](p{pro}/problem.json)<br>JSON syntax error: {problemjson_errors[pro]} |'
output += '\n'

output += '| subtasks.json syntax |'
for pro in problems:
    if subtasksjson_errors[pro] is None:
        output += f' [:white_check_mark:](p{pro}/subtasks.json) |'
    else:
        output += f' [:x:](p{pro}/subtasks.json)<br>JSON syntax error: {subtasksjson_errors[pro]} |'
output += '\n'

# contest_name consistency
contest_name_groups = {}

for pro in problems:
    if problemjson_errors[pro] is not None:
        continue

    contest_name = problemjson[pro]['contest_name']
    if 'TODO' in contest_name:
        continue
    group_key = json.dumps(
        contest_name,
        ensure_ascii=False,
        sort_keys=True,
    )
    contest_name_groups.setdefault(group_key, []).append(pro)

contest_name_warnings = set()

if len(contest_name_groups) > 1:
    max_group_size = max(
        len(group)
        for group in contest_name_groups.values()
    )

    largest_groups = [
        group
        for group in contest_name_groups.values()
        if len(group) == max_group_size
    ]

    if len(largest_groups) == 1:
        majority_problems = set(largest_groups[0])
        contest_name_warnings = {
            pro
            for pro in problems
            if problemjson_errors[pro] is None
            and pro not in majority_problems
        }
    else:
        contest_name_warnings = {
            pro
            for pro in problems
            if problemjson_errors[pro] is None
        }

# problem info
keys = (
    'contest_name',
    'problem_label',
    'name',
    'title',
)
for key in keys:
    output += f'| {key} | '
    for pro in problems:
        if problemjson_errors[pro] is not None:
            output += f' [:x:](p{pro}/problem.json)<br>Invalid JSON |'
            continue

        value = problemjson[pro][key]
        if isinstance(value, str) and 'TODO' in value:
            icon = ':x:'
        elif key == 'contest_name' and pro in contest_name_warnings:
            icon = ':warning:'
        else:
            icon = ':white_check_mark:'

        text = ''
        if icon != ':x:':
            if key == 'contest_name':
                text = f'<br>{value}'
            elif key not in ('problem_label'):
                text = f'<br>{value}'

        output += f' [{icon}](p{pro}/problem.json){text} |'
    output += '\n'

keys = (
    'memory_limit',
    'time_limit',
    'has_checker',
)
for key in keys:
    output += f'| {key} | '
    for pro in problems:
        if problemjson_errors[pro] is not None:
            output += f' [:x:](p{pro}/problem.json)<br>Invalid JSON |'
            continue

        output += f' {problemjson[pro][key]} |'
    output += '\n'

# gen/solution/validator
folders = (
    'gen',
    'solution',
    'validator',
)
for folder in folders:
    output += f'| {folder} |'
    for pro in problems:
        todos = []
        for file in glob.glob(f'p{pro}/{folder}/**', recursive=True):
            if os.path.isdir(file):
                continue
            with open(file, 'r') as f:
                try:
                    content = f.read()
                except Exception as e:
                    print(f'Ignore {file}')
                    continue
                if 'TODO' in content:
                    todos.append(file)
        if len(todos) == 0:
            output += f' [:white_check_mark:](p{pro}/{folder}) |'
        else:
            output += f' [:x:](p{pro}/{folder})'
            for file in todos:
                output += f'<br>[{os.path.basename(file)}]({file})'
            output += ' |'
    output += '\n'

# global_validators / subtask_sensitive_validators
output += '| subtasks.json<br>global_validators / subtask_sensitive_validators | '
for pro in problems:
    if subtasksjson_errors[pro] is not None:
        output += f' [:x:](p{pro}/subtasks.json)<br>Invalid JSON |'
        continue

    global_validators = subtasksjson[pro].get('global_validators', [])
    subtask_sensitive_validators = subtasksjson[pro].get(
        'subtask_sensitive_validators', []
    )

    warnings = []

    if (len(global_validators) == 0 and
            len(subtask_sensitive_validators) == 0):
        warnings.append('Not set')

    if (len(subtask_sensitive_validators) > 0 and
            not all('{subtask}' in v
                    for v in subtask_sensitive_validators)):
        warnings.append(
            'subtask_sensitive_validators needs `{subtask}` argument'
        )

    if warnings:
        icon = ':warning:'
        text = ' ' + ', '.join(warnings)
    else:
        icon = ':white_check_mark:'
        text = ''

    output += f' [{icon}](p{pro}/subtasks.json){text} |'

output += '\n'

# tests
output += '| tests |'
for pro in problems:
    if os.path.exists(f'p{pro}/tests/0-01.in'):
        icon = ':white_check_mark:'
    else:
        icon = ':x:'
    auto = ''
    if os.path.exists(f'p{pro}/gen/DISABLE_AUTO_BUILD'):
        auto = f'<br>[Auto build disabled](p{pro}/gen/DISABLE_AUTO_BUILD)'
    output += f' [{icon}](p{pro}/tests){auto} |'
output += '\n'

# statement
output += '| statement/index.md |'
for pro in problems:
    with open(f'p{pro}/statement/index.md', 'r') as f:
        content = f.read()

    if 'TODO' in content:
        icon = ':x:'
    else:
        icon = ':white_check_mark:'
    output += f' [{icon}](p{pro}/statement/index.md) |'
output += '\n'

output += '| statement/index.pdf |'
for pro in problems:
    if os.path.exists(f'p{pro}/statement/index.pdf'):
        icon = ':white_check_mark:'
    else:
        icon = ':x:'
    auto = ''
    if os.path.exists(f'p{pro}/statement/DISABLE_AUTO_BUILD'):
        auto = f'<br>[Auto build disabled](p{pro}/statement/DISABLE_AUTO_BUILD)'
    output += f' [{icon}](p{pro}/statement/index.pdf){auto} |'
output += '\n'

output = output.lstrip()

reportpath = os.environ.get('REPORTPATH')

try:
    with open(reportpath, 'r') as f:
        text = f.read()
except FileNotFoundError:
    text = ''

flag1 = '<!-- progress start -->'
flag2 = '<!-- progress end -->'
try:
    idx1 = text.index(flag1)
    idx2 = text.index(flag2)
except ValueError:
    text += f'\n## Progress\n{flag1}\n{flag2}\n'
    idx1 = text.index(flag1)
    idx2 = text.index(flag2)

text = text[:idx1] + flag1 + '\n\n' + output + '\n' + text[idx2:]
with open(reportpath, 'w') as f:
    f.write(text)
