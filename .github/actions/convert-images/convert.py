import glob
import json
import os
import re
import subprocess

from PIL import Image

os.chdir(os.environ.get('GITHUB_WORKSPACE'))

with open('.problems.json', 'r', encoding='utf8') as f:
    problems = json.load(f)

for pro in problems:
    print('Enter p{}/statement'.format(pro))
    os.chdir('p{}/statement'.format(pro))

    idx = 1
    content = open('index.md', 'r', encoding='utf8').read()

    pngs = glob.glob('*.png')
    jpgs = glob.glob('*.jpg')

    for source in pngs:
        while True:
            target = 'img{}.jpg'.format(idx if idx > 1 else '')
            if not os.path.exists(target):
                break
            idx += 1
        new_content = re.sub(r'{\s*' + re.escape(source) + r'\s*}', '{' + target + '}', content)
        if content != new_content:
            content = new_content
            im = Image.open(source)
            print(source, target, im.size)
            cmd = ['convert']
            if im.size[0] > 640:
                cmd.extend(['-resize', '640x'])
            cmd.extend([source, target])

            print(' '.join(cmd))
            subprocess.run(cmd)
            subprocess.run(['rm', source])
            subprocess.run(['git', 'add', source])
            subprocess.run(['git', 'add', target])

    for source in jpgs:
        im = Image.open(source)
        print(source, im.size)
        if im.size[0] > 640:
            cmd = ['convert', '-resize', '640x', source, source]
            print(' '.join(cmd))
            subprocess.run(cmd)
            subprocess.run(['git', 'add', source])

    open('index.md', 'w', encoding='utf8').write(content)
    subprocess.run(['git', 'add', 'index.md'])

    os.chdir(os.environ.get('GITHUB_WORKSPACE'))
