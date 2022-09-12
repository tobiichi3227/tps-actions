import glob
import json
import os

os.chdir(os.environ.get('GITHUB_WORKSPACE'))

with open('.problems.json', 'r', encoding='utf8') as f:
    problems = json.load(f)

output = ''

# cover
with open('cover.tex', 'r', encoding='utf8') as f:
    content = f.read()
if 'TODO' in content:
    icon = ':x:'
else:
    icon = ':white_check_mark:'
output += '- cover.tex [{}](cover.tex)\n'.format(icon)
output += '\n'

output += '| |'
for pro in problems:
    output += ' {} |'.format(pro)
output += '\n'

output += '|'
for _ in range(len(problems) + 1):
    output += ' --- |'
output += '\n'

# problem.json
problemjson = {}
for pro in problems:
    with open('p{}/problem.json'.format(pro), 'r', encoding='utf8') as f:
        problemjson[pro] = json.load(f)

# subtasks.json
subtasksjson = {}
for pro in problems:
    with open('p{}/subtasks.json'.format(pro), 'r', encoding='utf8') as f:
        subtasksjson[pro] = json.load(f)

# problem info
keys = [
    'contest_name',
    'problem_label',
    'name',
    'title',
]
for key in keys:
    output += '| {} | '.format(key)
    for pro in problems:
        text = ''
        if isinstance(problemjson[pro][key], str) and 'TODO' in problemjson[pro][key]:
            icon = ':x:'
        else:
            icon = ':white_check_mark:'
            if key not in ['contest_name', 'problem_label']:
                text = '<br>{}'.format(problemjson[pro][key])
        output += ' [{}](p{}/problem.json){} |'.format(icon, pro, text)
    output += '\n'

keys = [
    'memory_limit',
    'time_limit',
    'has_checker',
]
for key in keys:
    output += '| {} | '.format(key)
    for pro in problems:
        output += ' {} |'.format(problemjson[pro][key])
    output += '\n'

# gen/solution/validator
folders = [
    'gen',
    'solution',
    'validator',
]
for folder in folders:
    output += '| {} |'.format(folder)
    for pro in problems:
        todos = []
        for file in glob.glob('p{}/{}/**'.format(pro, folder), recursive=True):
            if os.path.isdir(file):
                continue
            with open(file, 'r', encoding='utf8') as f:
                try:
                    content = f.read()
                except Exception as e:
                    print('Ignore {}'.format(file))
                    continue
                if 'TODO' in content:
                    todos.append(file)
        if len(todos) == 0:
            output += ' [:white_check_mark:](p{}/{}) |'.format(pro, folder)
        else:
            output += ' [:x:](p{}/{})'.format(pro, folder)
            for file in todos:
                output += '<br>[{}]({})'.format(os.path.basename(file), file)
            output += ' |'
    output += '\n'

# global_validators
output += '| subtasks.json<br>global_validators | '
for pro in problems:
    if len(subtasksjson[pro]['global_validators']) == 0:
        icon = ':warning:'
        text = ' Not set'
    else:
        icon = ':white_check_mark:'
        text = ''
    output += ' [{}](p{}/subtasks.json){} |'.format(icon, pro, text)
output += '\n'

# tests
output += '| tests |'
for pro in problems:
    if os.path.exists('p{}/tests/0-01.in'.format(pro)):
        icon = ':white_check_mark:'
    else:
        icon = ':x:'
    auto = ''
    if os.path.exists('p{}/gen/DISABLE_AUTO_BUILD'.format(pro)):
        auto = '<br>[Auto build disabled](p{}/gen/DISABLE_AUTO_BUILD)'.format(pro)
    output += ' [{}](p{}/tests){} |'.format(icon, pro, auto)
output += '\n'

# statement
output += '| statement/index.md |'
for pro in problems:
    with open('p{}/statement/index.md'.format(pro), 'r', encoding='utf8') as f:
        content = f.read()

    if 'TODO' in content:
        icon = ':x:'
    else:
        icon = ':white_check_mark:'
    output += ' [{}](p{}/statement/index.md) |'.format(icon, pro)
output += '\n'

output += '| statement/index.pdf |'
for pro in problems:
    if os.path.exists('p{}/statement/index.pdf'.format(pro)):
        icon = ':white_check_mark:'
    else:
        icon = ':x:'
    auto = ''
    if os.path.exists('p{}/statement/DISABLE_AUTO_BUILD'.format(pro)):
        auto = '<br>[Auto build disabled](p{}/statement/DISABLE_AUTO_BUILD)'.format(pro)
    output += ' [{}](p{}/statement/index.pdf){} |'.format(icon, pro, auto)
output += '\n'

reportpath = os.environ.get('REPORTPATH')

try:
    with open(reportpath, 'r', encoding='utf8') as f:
        text = f.read()
except FileNotFoundError:
    text = ''

flag1 = '<!-- progress start -->'
flag2 = '<!-- progress end -->'
try:
    idx1 = text.index(flag1)
    idx2 = text.index(flag2)
except ValueError:
    text += '\n## Progress\n{}\n{}\n'.format(flag1, flag2)
    idx1 = text.index(flag1)
    idx2 = text.index(flag2)

text = text[:idx1] + flag1 + '\n' + output + text[idx2:]
with open(reportpath, 'w', encoding='utf8') as f:
    f.write(text)
