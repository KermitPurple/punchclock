'''
Tools to make the commandline look nice easier
'''

from sys import stderr
from datetime import date

def get_date(prompt: str = '', print_format: bool = True, print_newline: bool = True) -> date:
    '''
    gets and validates user input for a date in isoformat
    : :
    '''
    if prompt or print_format:
        print(prompt + ('(YYYY-MM-DD)' if print_format else ''), end = '\n' if print_newline else '')
    while 1:
        try:
            return date.fromisoformat(
                input()
                    .strip()
                    .replace(' ', '-')
                    .replace('/', '-')
                    .replace('\\', '-')
            )
        except ValueError as e:
            eprint(e)

def get_yes_no(prompt: str) -> bool:
    '''
    ask a yes or no question and prompt response
    :returns: true if yes false if no
    '''
    if prompt != '':
        print(prompt)
    while 1:
        response = input().lower().strip()
        if response == 'yes' or response == 'y':
            return True
        elif response == 'no' or response == 'n':
            return False

def eprint(*args, **kwargs):
    '''
    Print to stderr
    '''
    print(*args, file=stderr, **kwargs)
