#!/usr/bin/env python3
from command_line_tools import get_yes_no
from datetime import datetime
from typing import List
import pickle
import sys
import os

PUNCHCLOCK_PATH = '/Users/shane/dropbox/punchclocks'
PUNCHCLOCK_PREFIX = 'pc_'
PUNCHCLOCK_PREFIX_LENGTH = len(PUNCHCLOCK_PREFIX)

def get_all_punchclocks() -> List[str]:
    '''
    get a list of existing punch clock names
    :returns: list of punchclock names
    '''
    return list(sorted(map(lambda x: x[PUNCHCLOCK_PREFIX_LENGTH:], filter(lambda x: x.startswith(PUNCHCLOCK_PREFIX), os.listdir()))))

def clock_exists(name: str) -> bool:
    '''
    checks if a clock exists
    :name: name of clock to get
    :returns: True if clock exists
    '''
    return f'{PUNCHCLOCK_PREFIX}{name}' in os.listdir()

def delete_punchclock(name: str):
    '''
    delete a punch clock
    :name: name of clock to delete
    '''
    os.remove(f'{PUNCHCLOCK_PREFIX}{name}')

def get_punchclock(name: str) -> List[List[datetime]]:
    '''
    get the punchclock data from a file
    :name: name of clock to get
    :returns: punchclock data
    '''
    return pickle.load(open(f'{PUNCHCLOCK_PREFIX}{name}', 'rb'))

def set_punchclock(name: str, clock: List[List[datetime]]):
    '''
    :name: name of punchclock to set
    :clock: the data to set the clock to
    '''
    pickle.dump(clock, open(f'{PUNCHCLOCK_PREFIX}{name}', 'wb'))

def clock_in(name: str):
    '''
    clock into a punch in clock setting the intial time
    :name: name of clock to clock in to
    '''
    clocks = get_all_punchclocks()
    while not clock_exists(name):
        print(f'{name} does not exist.')
        if get_yes_no('Do you want to create a new clock with that name?(y/n)'):
            set_punchclock(name, [[datetime.now()]])
            return
        else:
            print(f'The existing clocks are: {clocks}')
            name = input('Enter name of another clock> ')
    clock = get_punchclock(name)
    last_entry_len = len(clock[-1])
    if last_entry_len == 1:
        print('You need to clock out before you clock back in')
    elif last_entry_len == 2:
        clock.append([datetime.now()])
        set_punchclock(name, clock)
        print('Clocked in!')
    else:
        raise ValueError(f'last_entry_len shouldn\'t be {last_entry_len} :\\')

def clock_out(name: str):
    '''
    clock out of a punch out clock setting the ending time
    :name: name of clock to clock out of
    '''
    clocks = get_all_punchclocks()
    while not clock_exists(name):
        print(f'{name} does not exist.')
        print(f'The existing clocks are: {clocks}')
        name = input('Enter name of another clock> ')
    clock = get_punchclock(name)
    last_entry_len = len(clock[-1])
    if last_entry_len == 1:
        clock[-1].append(datetime.now())
        set_punchclock(name, clock)
        print('Clocked out!')
        print(f'elapsed time: {clock[-1][1] - clock[-1][0]}')
    elif last_entry_len == 2:
        print('You need to clock in before you clock back out')
    else:
        raise ValueError(f'last_entry_len shouldn\'t be {last_entry_len} :\\')

def show_current(name: str):
    '''
    show the most recent entry for the given clock
    :name: name of clock to check
    '''
    clocks = get_all_punchclocks()
    while not clock_exists(name):
        print(f'{name} does not exist.')
        print(f'The existing clocks are: {clocks}')
        name = input('Enter name of another clock> ')
    clock = get_punchclock(name)
    last_entry_len = len(clock[-1])
    if last_entry_len == 1:
        start, = clock[-1]
        end = datetime.now()
        elapsed = (end - start)
        print(f'started: {start.isoformat()}')
        print(f'now: {end.isoformat()}')
        print(f'elapsed time: {elapsed}')
    elif last_entry_len == 2:
        start, end = clock[-1]
        elapsed = (end - start)
        print(f'started: {start.isoformat()}')
        print(f'ended: {end.isoformat()}')
        print(f'elapsed time: {elapsed}')
    else:
        raise ValueError(f'last_entry_len shouldn\'t be {last_entry_len} :\\')

def get_running() -> List[str]:
    '''
    get a list of all running punchclocks
    '''
    return list(filter(lambda name: len(get_punchclock(name)[-1]) != 1, get_all_punchclocks()))


def print_help():
    print('''clock
    i {name}
    in {name} - clock into a clock with name {name}
    o {name}
    out {name} - clock out of a clock with name {name}
    s {name}
    show {name} - show most recent entry of clock with name {name}
    s
    show
    l
    list - show all existing clocks
    r
    running - show all clocks currently clocked into
    ''')

def main():
    '''Driver Code'''
    os.chdir(PUNCHCLOCK_PATH)
    sys.argv.pop(0)
    arg_len = len(sys.argv)
    if arg_len == 2:
        action, name = sys.argv
        if action == 'in' or action == 'i':
            clock_in(name)
        elif action == 'out' or action == 'o':
            clock_out(name)
        elif action == 'show' or action == 's':
            show_current(name)
        elif action == 'delete' or action == 'd':
            delete_punchclock(name)
    elif arg_len == 1:
        action = sys.argv[0]
        if action == 'show' or action == 's' or action == 'list' or action == 'l':
            print(get_all_punchclocks())
        elif action == 'running' or action == 'r':
            print(get_running())
        elif action == 'help' or action == 'h':
            print_help()
    elif arg_len == 0:
        print_help()
    else:
        raise ValueError(f'Incorrect number of args: {arg_len}')

if __name__ == '__main__':
    main() # run driver code
