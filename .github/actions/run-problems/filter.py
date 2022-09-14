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
print('::set-output name=problemsjson::{}'.format(json.dumps(result)))
print('::set-output name=problems::{}'.format(' '.join(result)))
print('::set-output name=lastproblem::{}'.format(problems[-1]))
