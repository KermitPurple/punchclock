#!/usr/bin/env python3
from command_line_tools import *
import matplotlib.pyplot as plt
from datetime import datetime, time
import pickle
import sys
import os

PUNCHCLOCK_PATH = '/Users/shane/dropbox/punchclocks'
PUNCHCLOCK_PREFIX = 'pc_'
PUNCHCLOCK_PREFIX_LENGTH = len(PUNCHCLOCK_PREFIX)

def get_all_punchclocks() -> list[str]:
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

def get_punchclock(name: str) -> list[list[datetime]]:
    '''
    get the punchclock data from a file
    :name: name of clock to get
    :returns: punchclock data
    '''
    return pickle.load(open(f'{PUNCHCLOCK_PREFIX}{name}', 'rb'))

def set_punchclock(name: str, clock: list[list[datetime]]):
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

def get_running() -> list[str]:
    '''
    get a list of all running punchclocks
    '''
    return list(filter(lambda name: len(get_punchclock(name)[-1]) == 1, get_all_punchclocks()))

def plot_punchclock(name: str, max_days: int = 7, time_format: str = '%I:%M %p'):
    '''
    plot a punchclock
    :name: name of the clock to plot
    '''
    plt.ylim(0, 24) # set limits on y axis
    plt.gca().invert_yaxis() # flippy floppy
    index = 0
    x = 0
    width = 20
    dct = get_date_dict(name)
    plt.xticks(list(map(lambda x: x * width + width / 2, range(len(dct)))), dct.keys())
    for date, times in dct.items():
        for start, end in times:
            s_val = start.hour + start.minute / 60
            e_val = end.hour + end.minute / 60
            plt.fill_betweenx(
                [s_val, e_val],
                [x, x],
                [x + width, x + width]
            )
            plt.text(
                x + width / 2,
                (e_val + s_val) / 2,
                start.strftime(time_format) + ' - ' + end.strftime(time_format),
                ha='center',
                va='center'
            )
        if index > max_days:
            break
        x += width
        index += 1
    plt.show()

def get_date_dict(name: str):
    '''
    :name: name of the clock to get
    '''
    dct = {}
    clock = get_punchclock(name)
    for entry in reversed(clock):
        if len(entry) == 1:
            start, end = entry[0], datetime.now()
        elif len(entry) == 2:
            start, end = entry
        if start.date() == end.date():
            date = start.date()
            val = [start.time(), end.time()]
            if date not in dct:
                dct[date] = [val]
            else:
                dct[date].append(val)
        else:
            date = start.date()
            val = [start.time(), time(23, 59, 59)]
            if date not in dct:
                dct[date] = [val]
            else:
                dct[date].append(val)
            date = end.date()
            val = [time(0, 0, 0), end.time()]
            if date not in dct:
                dct[date] = [val]
            else:
                dct[date].append(val)
    return dct

def print_help():
    print('''clock
  i {name}, in {name}     - clock into a clock with name {name}
  o {name}, out {name}    - clock out of a clock with name {name}
  s {name}, show {name}   - show most recent entry of clock with name {name}
  d {name}, delete {name} - delete a clock with the name {name}
  p {name}, plot {name}   - plot a clock with the name {name}
  s, show, l, list        - show all existing clocks
  r, running              - show all clocks currently clocked into
    ''')

def main():
    '''Driver Code'''
    os.chdir(PUNCHCLOCK_PATH)
    sys.argv.pop(0)
    arg_len = len(sys.argv)
    match sys.argv:
        case [] | ['help'] | ['h']:
            print_help()
        case ['in', name] | ['i', name]:
            clock_in(name)
        case ['out', name] | ['o', name]:
            clock_out(name)
        case ['show', name] | ['s', name]:
            show_current(name)
        case ['delete', name] | ['d', name]:
            delete_punchclock(name)
        case ['plot', name] | ['p', name]:
            plot_punchclock(name)
        case ['show'] | ['s'] | ['list'] | ['l']:
            print(get_all_punchclocks())
        case ['running'] | ['r']:
            print(get_running())
        case _:
            eprint('ERROR: Invalid args, enter "clock" to show help')
            exit(1)

if __name__ == '__main__':
    main() # run driver code
