#!/usr/bin/env python3
from command_line_tools import *
import matplotlib.pyplot as plt
from datetime import datetime, date, time, timedelta
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

def plot_punchclock(
        name: str,
        max_days: int = 7,
        time_format: str = '%I:%M %p',
        date_format: str = '%a %Y/%m/%d'

    ):
    '''
    plot a punchclock
    :name: name of the clock to plot
    :max_days: the maximum number of days to display
    :time_format: a time format string for time.strftime
    :date_format: a date format string for datetime.strftime
    '''
    plt.ylim(0, 24) # set limits on y axis
    plt.gca().invert_yaxis() # flippy floppy
    plt.xlabel('Date')
    plt.ylabel('Time')
    plt.title(f'{name.title()} Punchclock')
    index = 0
    x = 0
    width = 20
    dct = get_date_dict(name)
    size = min(len(dct), max_days)
    plt.xlim(0, size * width)
    plt.xticks(
        list(map(
            lambda x: x * width + width / 2,
            range(size)
        ))[::-1],
        reversed(list(map(
            lambda x: x.strftime(date_format),
            sorted(dct.keys())
        ))[:size])
    )
    for current_date, times in sorted(dct.items(), key=lambda x: x[0]):
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
                va='center',
                fontsize=7.5
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
            key = start.date()
            val = [start.time(), end.time()]
            if key not in dct:
                dct[key] = [val]
            else:
                dct[key].append(val)
        else:
            s_date = start.date()
            e_date = end.date()
            val = [start.time(), time(23, 59, 59, 999_999)]
            if s_date not in dct:
                dct[s_date] = [val]
            else:
                dct[s_date].append(val)
            full_day = [time(0, 0, 0), time(23, 59, 59, 999_999)]
            diff = (end - start).days - 1
            for i in range(diff):
                td = timedelta(days=i + 1)
                dct[s_date + td] = [full_day[:]]
            val = [time(0, 0, 0), end.time()]
            if e_date not in dct:
                dct[e_date] = [val]
            else:
                dct[e_date].append(val)
    return dct

def calculate_total(name: str, since: date) -> timedelta:
    '''
    :name: name of the punch clock
    :since: the earliest date to count
    :returns: total ammount of time put into a punchclock
    '''
    total = timedelta()
    dct = get_date_dict(name)
    for key, times in reversed(dct.items()):
        if key < since:
            return total
        for val in times:
            if len(val) == 1:
                start, end = val[0], datetime.now()
            elif len(val) == 2:
                start, end = val
            total += datetime.combine(key, end) - datetime.combine(key, start)
    return total

def print_help():
    print('''clock
  i {name}, in {name}                     - clock into a clock with name {name}
  o {name}, out {name}                    - clock out of a clock with name {name}
  s {name}, show {name}                   - show most recent entry of clock with name {name}
  d {name}, delete {name}                 - delete a clock with the name {name}
  p {name}, plot {name}                   - plot a clock with the name {name}
  t {name} {date}, total {name} {date}    - calculated total time clocked in {name} since {date}
  s, show, l, list                        - show all existing clocks
  r, running                              - show all clocks currently clocked into
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
        case ['total', name, since] | ['t', name, since]:
            try:
                date_obj = parse_date(since)
                print(f'Total time elapsed in {name} since {since}: {calculate_total(name, date_obj)}')
            except ValueError as e:
                print(e)
        case ['show'] | ['s'] | ['list'] | ['l']:
            print(get_all_punchclocks())
        case ['running'] | ['r']:
            print(get_running())
        case _:
            eprint('ERROR: Invalid args, enter "clock" to show help')
            exit(1)

if __name__ == '__main__':
    main() # run driver code
