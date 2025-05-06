# bool_quetion
## Python-module for asking yes/no or accept/cancel questions.

### Installing
#### Install from PyP

`pip install bool_quetion`

#### Install on Debian 12 and later from PyP

`pip install bool_quetion --break-system-packages`

#### Install from APT repositories

**As root or using sudo**

Add APT repositories:

`echo "deb https://pablinet.github.io/apt ./" > /etc/apt/sources.list.d/pablinet.list`

Add APT Key:

`wget -O /etc/apt/trusted.gpg.d/pablinet.gpg https://pablinet.github.io/apt/pablinet.gpg`

Upload APT repositories:

`apt update`

Install bool_quetion:

`apt install python-bool-quetion`

---
### Using the code in Python 3.x
~~~
from bool_quetion import true_false
names = []
reply = True
while reply:
    element = input ('Enter the full name: ')
    names.append(element)
    for name in names:
        print (name)
        reply = true_false('Do you wish to continue?', ['Yes or', 'no'])
else:
    reply = True
~~~

It is also possible to customize the error message and highlight the characters that can be entered:
~~~
reply = true_false('Do you wish to continue?', ['Yes or', 'no'], True)
reply = true_false('Continue?', ['Yes or', 'no'], 'Error Key', True)
~~~
---
**BONUS TRACK**

Use this library in Bash.
~~~
#!/usr/bin/env python3
from sys import argv, exit
from bool_quetion import true_false

if 3 > len(argv) or len(argv) > 5:
    print('Error in the number of arguments.')
    exit(255)
arguments = argv[1:].copy()
arguments[1] = arguments[1].split('%')
err_number = 1
if len(arguments[1]) == 3 and arguments[1][2].isdecimal():
    err_number = int(arguments[1][2])
    arguments[1].pop()
if len(arguments) in (3, 4):
    if arguments[-1].lower() in ('true', 'false'):
        arguments[-1] = arguments[-1].lower() == 'true'
exit(0 if true_false(*arguments) else err_number)
~~~

Add execution permissions:

`chmod +x true-false`

Run the script:
~~~
./true-false 'Do you wish to continue?' 'Yes or%No'
./true-false 'Do you wish to continue?' 'Yes or%No' 'Bad key'
./true-false 'Do you wish to continue?' 'Yes or%No' 'Bad key' true
~~~

Run script with custom error code:

~~~
./true-false 'Do you wish to continue?' 'Yes or%No%5'
./true-false 'Do you wish to continue?' 'Yes or%No%5' 'Bad key'
./true-false 'Do you wish to continue?' 'Yes or%No%5' 'Bad key' true
~~~

