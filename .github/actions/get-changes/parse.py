import json
import os

os.chdir(os.environ.get('GITHUB_WORKSPACE'))

problems = json.loads(os.environ.get('PROBLEMS'))
changes = json.loads(os.environ.get('CHANGES'))
flagpath = os.environ.get('FLAGPATH')
keys = ['input', 'solutions', 'pdf', 'verify']
prefixes = {}
for pro in problems:
    prefixes['p{}/'.format(pro)] = pro

flags = {
    'tests': {},
    'input': {},
    'output': {},
    'solutions': {},
    'pdf': {},
    'verify': {},
}
for key in flags.keys():
    for pro in problems:
        flags[key][pro] = False

# tests, input, output
input_files = json.loads(changes['input_files'])
solutions_files = json.loads(changes['solutions_files'])
for pro in problems:
    if os.path.exists('p{}/gen/DISABLE_AUTO_BUILD'.format(pro)):
        print('Skip tests for p{} due to disable flag'.format(pro))
        continue

    # paths-filter
    prefix = 'p{}/'.format(pro)

    for file in input_files:
        if file.startswith(prefix):
            flags['tests'][pro] = True
            flags['input'][pro] = True
            print('Set tests,input/{} to true due to {}'.format(pro, file))
            break

    for file in solutions_files:
        if file.startswith(prefix):
            flags['tests'][pro] = True
            flags['solutions'][pro] = True
            print('Set tests,solutions/{} to true due to {}'.format(pro, file))
            break

    with open('p{}/solutions.json'.format(pro), 'r', encoding='utf8') as f:
        solutions = json.load(f)
    for file, val in solutions.items():
        if val.get('verdict') == 'model_solution':
            if 'p{}/solution/{}'.format(pro, file) in solutions_files:
                flags['tests'][pro] = True
                flags['output'][pro] = not flags['input'][pro]
                print('Set tests,output/{0} to true due to p{0}/{1}'.format(pro, file))
            break

    # config
    if os.path.exists(os.path.join(flagpath, 'input-{}'.format(pro))):
        flags['tests'][pro] = True
        flags['input'][pro] = True
        print('Set tests,input/{} to true due to config'.format(pro))
    if os.path.exists(os.path.join(flagpath, 'output-{}'.format(pro))):
        flags['tests'][pro] = True
        flags['output'][pro] = True
        print('Set tests,output/{} to true due to config'.format(pro))
    if os.path.exists(os.path.join(flagpath, 'solutions-{}'.format(pro))):
        flags['tests'][pro] = True
        flags['solutions'][pro] = True
        print('Set tests,solutions/{} to true due to config'.format(pro))

# pdf
for pro in problems:
    if os.path.exists('p{}/statement/DISABLE_AUTO_BUILD'.format(pro)):
        print('Skip pdf for p{} due to disable flag'.format(pro))
        continue

    prefix = 'p{}/'.format(pro)

    for file in json.loads(changes['pdf_files']):
        if file.startswith(prefix):
            flags['pdf'][pro] = True
            print('Set pdf/{} to true due to {}'.format(pro, file))
            break

    if changes['template'] == 'true':
        flags['pdf'][pro] = True
        print('Set pdf/{} to true due to template'.format(pro))

    if pro == 'A' and changes['cover'] == 'true':
        flags['pdf']['A'] = True
        print('Set pdf/A to true due to cover')

    if os.path.exists(os.path.join(flagpath, 'pdf-{}'.format(pro))):
        flags['pdf'][pro] = True
        print('Set pdf/{} to true due to config'.format(pro))

    if pro == problems[-1] and changes['appendix'] == 'true':
        flags['pdf'][problems[-1]] = True
        print('Set pdf/{} to true due to appendix'.format(problems[-1]))

# verify
verify_files = json.loads(changes['verify_files'])
for pro in problems:
    prefix = 'p{}/'.format(pro)
    for file in verify_files:
        if file.startswith(prefix):
            flags['verify'][pro] = True
            print('Set verify/{} to true due to {}'.format(pro, file))
            break

result = {}
for key in flags:
    result[key] = ''
    for pro in problems:
        if flags[key][pro]:
            result[key] += pro

print('flags:', flags)
print('result:', result)
with open(os.environ.get('GITHUB_OUTPUT', ''), 'a') as f:
    f.write('\nchanges={}'.format(json.dumps(result)))
