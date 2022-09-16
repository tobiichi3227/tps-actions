import json
import os
import re
import subprocess

os.chdir(os.environ.get('GITHUB_WORKSPACE'))

prob_cnt = int(os.environ.get('PROBLEMCOUNT'))

try:
    prob_cnt = int(prob_cnt)
except:
    print('Please input a number')
    exit(1)

if prob_cnt < 1 or prob_cnt > 26:
    print('Must be 1 ~ 26')
    exit(1)

with open('.problems.json', 'r', encoding='utf8') as f:
    problems = json.load(f)

with open('Makefile', 'r', encoding='utf8') as f:
    makefile = f.read()

with open('README.md', 'r', encoding='utf8') as f:
    readme = f.read()

for i in range(prob_cnt):
    label = chr(ord('A') + i)
    path = 'p{}'.format(label)
    if not os.path.exists(path):
        subprocess.run(['tps', 'init', path, '-T', 'tps-task-templates', '-t', 'default'])

        with open('{}/problem.json'.format(path), 'r', encoding='utf8') as f:
            data = json.load(f)
        data['problem_label'] = label
        with open('{}/problem.json'.format(path), 'w', encoding='utf8') as f:
            f.write(json.dumps(data, indent='\t', ensure_ascii=False))
            f.write('\n')

        subprocess.run(['git', 'add', path])

        problems.append(label)
        makefile = makefile.replace('# NEWPROBELM', 'import-{0}:\n\tcmsImportTask ./{0}/ -u $(if $(s), , --no-statement)\n\n# NEWPROBELM'.format(path))
        readme = re.sub(
            '\n*<!-- new problem -->',
            '\n| {0} | [statement]({1}/statement) [md]({1}/statement/index.md) [pdf]({1}/statement/index.pdf) | [gen]({1}/gen) | [validator]({1}/validator) | [solution]({1}/solution) [check]({1}/solutions-check.txt) | [tests]({1}/tests) | [problem]({1}/problem.json) [solutions]({1}/solutions.json) [subtasks]({1}/subtasks.json) |\n\n<!-- new problem -->'.format(label, path),
            readme
        )
    else:
        print('{} is exists'.format(path))

with open('.problems.json', 'w', encoding='utf8') as f:
    json.dump(problems, f)

with open('Makefile', 'w', encoding='utf8') as f:
    f.write(makefile)

with open('README.md', 'w', encoding='utf8') as f:
    f.write(readme)
