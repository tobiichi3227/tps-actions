import json
import os

os.chdir(os.environ.get('GITHUB_WORKSPACE'))

with open('.problems.json', 'r', encoding='utf8') as f:
    problems = json.load(f)

all_subtasks = {}
max_subtask = 0
for pro in problems:
    with open('p{}/subtasks.json'.format(pro), 'r', encoding='utf8') as f:
        subtasks = json.load(f)['subtasks']

    all_subtasks[pro] = []
    for subtask in sorted(subtasks.values(), key=lambda v: v['index']):
        if subtask['index'] == 0:
            continue
        all_subtasks[pro].append((subtask['score'], subtask['text']))

    max_subtask = max(max_subtask, len(all_subtasks[pro]))

output = ''
output += '| |'
for i in range(max_subtask):
    output += ' {} |'.format(i + 1)
output += '\n'

output += '|'
for i in range(max_subtask + 1):
    output += ' --- |'
output += '\n'

for pro in problems:
    output += '| {} |'.format(pro)
    for subtask in all_subtasks[pro]:
        output += ' {}<br>{} |'.format(subtask[0], subtask[1])
    output += '\n'

reportpath = os.environ.get('REPORTPATH')

try:
    with open(reportpath, 'r', encoding='utf8') as f:
        text = f.read()
except FileNotFoundError:
    text = ''

flag1 = '<!-- subtasks start -->'
flag2 = '<!-- subtasks end -->'
try:
    idx1 = text.index(flag1)
    idx2 = text.index(flag2)
except ValueError:
    text += '\n## Subtasks\n{}\n{}\n'.format(flag1, flag2)
    idx1 = text.index(flag1)
    idx2 = text.index(flag2)

text = text[:idx1] + flag1 + '\n\n' + output + '\n' + text[idx2:]
with open(reportpath, 'w', encoding='utf8') as f:
    f.write(text)
