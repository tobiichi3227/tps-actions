import json
import os

os.chdir(os.environ.get('GITHUB_WORKSPACE'))
GROUP_SIZE = int(os.environ.get('GROUPSIZE', 3))

with open('.problems.json', 'r', encoding='utf8') as f:
    problems = json.load(f)

scores = {}
allSubtasks = []
for pro in problems:
    scores[pro] = {}
    with open(os.path.join('p' + pro, 'subtasks.json'), 'r', encoding='utf8') as f:
        subtasks = json.load(f)
        for subid, subtask in subtasks['subtasks'].items():
            scores[pro][subtask['index'] + 1] = subtask['score']
            if subtask['score'] == 0:
                continue
            allSubtasks.append({'id': '{}{}'.format(pro, subtask['index']), 'score': subtask['score']})
maxIndex = max([len(pro) for pro in scores.values()])

allSubtasks.sort(key=lambda v: v['score'])

total = len(problems) * 100
dp = [[] for i in range(total + 1)]
dp[0] = [set()]

for subtask in allSubtasks:
    for i in range(total, -1, -1):
        for group in dp[i]:
            temp = group.copy()
            temp.add(subtask['id'])
            if len(temp) <= GROUP_SIZE:
                dp[i + subtask['score']].append(temp)

output = '| score | count | groups |\n'
output += '| --- | --- | --- |\n'
for i in range(1, total + 1):
    if len(dp[i]) > 1:
        output += '| {} | {} | {} |\n'.format(
            i,
            len(dp[i]),
            ' '.join(['(' + ', '.join(sorted(group)) + ')' for group in dp[i]])
        )

reportpath = os.environ.get('REPORTPATH')

try:
    with open(reportpath, 'r', encoding='utf8') as f:
        text = f.read()
except FileNotFoundError:
    text = ''

flag1 = '<!-- scores start -->'
flag2 = '<!-- scores end -->'
try:
    idx1 = text.index(flag1)
    idx2 = text.index(flag2)
except ValueError:
    text += '\n## Scores\n{}\n{}\n'.format(flag1, flag2)
    idx1 = text.index(flag1)
    idx2 = text.index(flag2)

text = text[:idx1] + flag1 + '\n\n' + output + '\n' + text[idx2:]
with open(reportpath, 'w', encoding='utf8') as f:
    f.write(text)
