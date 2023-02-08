import json
import os

requests = os.environ.get('REQUESTS')
problems = json.loads(os.environ.get('PROBLEMS'))

print('requests:', requests)

result = []
for pro in problems:
    if pro in requests:
        result.append(pro)

print('result:', result)
with open(os.environ.get('GITHUB_OUTPUT', ''), 'a') as f:
    f.write('\nproblemsjson={}'.format(json.dumps(result)))
    f.write('\nproblems={}'.format(' '.join(result)))
    f.write('\nlastproblem={}'.format(problems[-1]))
