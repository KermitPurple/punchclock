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
    elif last_entry_len == 2:
        print('You need to clock in before you clock back out')
    else:
        raise ValueError(f'last_entry_len shouldn\'t be {last_entry_len} :\\')

def main():
    '''Driver Code'''
    os.chdir(PUNCHCLOCK_PATH)

if __name__ == '__main__':
    main() # run driver code
