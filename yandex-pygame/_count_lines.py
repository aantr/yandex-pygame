import os
from glob import glob

files = [y for x in os.walk(os.getcwd())
         for y in glob(os.path.join(x[0], '*.py'))]
counter = 0
for i in files:
    with open(i, encoding='utf-8') as f:
        counter += len(f.readlines())

print('-' * 100)
print(f'Lines in all "*.py" files in project directory: <<<---   {counter}   --->>>')
print('-' * 100)
input()