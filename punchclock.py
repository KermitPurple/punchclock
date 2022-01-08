#!/usr/bin/env python3
from command_line_tools import *
import matplotlib.pyplot as plt
from datetime import datetime, date, time, timedelta
import argparse
import pickle
import sys
import os

PUNCHCLOCK_PATH = '/Users/shane/dropbox/punchclocks'
PUNCHCLOCK_PREFIX = 'pc_'
PUNCHCLOCK_PREFIX_LENGTH = len(PUNCHCLOCK_PREFIX)
TIME_FORMAT = '%I:%M %p'
DATE_FORMAT = '%a %Y/%m/%d'

def date_arg(s: str) -> date:
    '''
    User defined date type for arg parse
    :s: input string
    :returns: a parsed date
    '''
    try:
        return parse_date(s)
    except:
        raise argparse.ArgumentTypeError(f'could not parse {s!r}, expected date in isoformat. e.g. 2022/01/07 is January 7th 2021')

def pos_int(s: str) -> int:
    '''
    User defined int type for arg parse
    :s: input string
    :returns: a parsed number greater than one
    '''
    try:
        val = int(s)
    except ValueError:
        raise argparse.ArgumentTypeError(f'Expected int found {s!r}')
    if val <= 0:
        raise argparse.ArgumentTypeError(f'Number must be greater than 0')
    return val


def exists_or_exit(name: str):
    '''
    if clock_exists returns true it does nothing
    otherwise it prints error message and exists
    :name: name of punchclock to check
    '''
    if not clock_exists(name):
        eprint(f'No clock with name "{name}" exists')
        exit(1)

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
    exists_or_exit(name)
    os.remove(f'{PUNCHCLOCK_PREFIX}{name}')

def get_punchclock(name: str) -> list[list[datetime]]:
    '''
    get the punchclock data from a file
    :name: name of clock to get
    :returns: punchclock data
    '''
    exists_or_exit(name)
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
    if not clock_exists(name):
        print(f'{name} does not exist.')
        if get_yes_no('Do you want to create a new clock with that name?(y/n)'):
            set_punchclock(name, [[datetime.now()]])
        return
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
    exists_or_exit(name)
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
    exists_or_exit(name)
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

def plot_dates(
        name: str,
        start: date,
        end: date,
        skip_empty: bool = False
    ):
    '''
    Plot a punchclock between the given dates
    :name: name of punchclock
    :start: start date of punchclock
    :end: end date of punchclock
    :skip_empty: whether or not days where nothing is recorded should be displayed
    '''
    exists_or_exit(name)
    if start > end:
        plot_dates(
            name,
            start,
            end,
        )
    start_date_str = start.strftime(DATE_FORMAT)
    end_date_str = end.strftime(DATE_FORMAT)
    plt.ylim(0, 24) # set limits on y axis
    plt.gca().invert_yaxis() # flippy floppy
    plt.xlabel('Date')
    plt.ylabel('Time')
    plt.title(f'{name.title()} Punchclock {start_date_str} - {end_date_str}')
    x = 0
    width = 20
    dct = get_date_dict(name)
    xticks_pos = []
    xticks_labels = []
    size = (end - start).days + 1
    for current_date in [start + timedelta(i) for i in range(size)]:
        center = x + width / 2
        times = dct.get(current_date)
        if times:
            for start_time, end_time in times:
                s_val = start_time.hour + start_time.minute / 60
                e_val = end_time.hour + end_time.minute / 60
                plt.fill_betweenx(
                    [s_val, e_val],
                    [x, x],
                    [x + width, x + width]
                )
                plt.text(
                    center,
                    (e_val + s_val) / 2,
                    start_time.strftime(TIME_FORMAT) + ' - ' + end_time.strftime(TIME_FORMAT),
                    ha='center',
                    va='center',
                    fontsize=7.5
                )
        elif skip_empty:
            continue
        xticks_pos.append(center)
        xticks_labels.append(current_date.strftime(DATE_FORMAT))
        x += width
    plt.subplots_adjust(
        left = 0.05,
        bottom = 0.15,
        right = 0.95,
        top = 0.95,
    )
    plt.xlim(0, len(xticks_pos) * width)
    plt.xticks(xticks_pos, xticks_labels, rotation = 25)
    plt.show()

def plot_punchclock(
        name: str,
        max_days: int = 7,
        skip_empty: bool = True,
    ):
    '''
    plot a punchclock the most recent {max_days} days
    :name: name of the clock to plot
    :max_days: the maximum number of days to display
    :skip_empty: whether or not days where nothing is recorded should be displayed
    '''
    exists_or_exit(name)
    if skip_empty:
        dates = sorted(map(lambda x: x[0], get_date_dict(name).items()))
        start = dates[-max_days] if len(dates) > max_days else dates[0]
        end = dates[-1]
    else:
        end = date.today()
        start = end - timedelta(max_days)
    plot_dates(
        name,
        start,
        end,
        skip_empty
    )

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
            diff = (end - start).days
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
  pd {name} {start} {end}, plot-dates {name} {start} {end}
                                          - plot dates in {name} between {start} and {end}
  l, list                                 - show all existing clocks
  r, running                              - show all clocks currently clocked into''')

def main():
    '''Driver Code'''
    os.chdir(PUNCHCLOCK_PATH)
    sys.argv.pop(0) # remove first arg
    if len(sys.argv) == 0:
        print_help()
        return
    match sys.argv[0]:
        case 'help' | 'h':
            print_help()
        case 'in' | 'i':
            parser = argparse.ArgumentParser('clock in', description='clock into a punchclcok')
            parser.add_argument('name', type=str, help='name of the clock to punch into')
            args = parser.parse_args()
            clock_in(args.name)
        case 'out' | 'o':
            parser = argparse.ArgumentParser('clock out', description='clock out of a punchclcok')
            parser.add_argument('name', type=str, help='name of the clock to punch out of')
            args = parser.parse_args()
            clock_out(args.name)
        case 'show' | 's':
            parser = argparse.ArgumentParser('clock show', description='show the most recent usage of a punchclock')
            parser.add_argument('name', type=str, help='name of the clock to show')
            args = parser.parse_args()
            show_current(args.name)
        case 'delete' | 'd':
            parser = argparse.ArgumentParser('clock delete', description='delete a punchclock')
            parser.add_argument('name', type=str, help='name of the clock to delete')
            args = parser.parse_args()
            delete_punchclock(args.name)
        case 'plot' | 'p':
            parser = argparse.ArgumentParser('clock plot', description='plot a punchclock')
            parser.add_argument('name', type=str, help='name of clock to plot')
            parser.add_argument('-d', '--days', type=pos_int, default=7, help='number of days to display')
            parser.add_argument('-s', '--skip-empty', action='store_true', help='skip days that do not have any time recorded on them')
            args = parser.parse_args()
            plot_punchclock(args.name, args.days, args.skip_empty)
        case 'plot-dates' | 'pd':
            parser = argparse.ArgumentParser('clock plot-dates', description='plot a punchclock between two dates')
            parser.add_argument('name', type=str, help='name of clock to plot')
            parser.add_argument('start', type=date_arg, help='start of the date range')
            parser.add_argument('end', type=date_arg, help='end of the date range')
            parser.add_argument('-s', '--skip-empty', action='store_true', help='skip days that do not have any time recorded on them')
            args = parser.parse_args()
            plot_dates(args.name, args.start, args.end, args.skip_empty)
        case 'total'  | 't':
            parser = argparse.ArgumentParser('clock total', description='calculate total time worked since a given date')
            parser.add_argument('name', type=str, help='name of clock to calculate from')
            parser.add_argument('date', type=date_arg, help='date to find the total worked since')
            args = parser.parse_args()
            print(f'Total time elapsed in {args.name} since {args.date}: {calculate_total(args.name, args.date)}')
        case 'list' | 'l':
            print(get_all_punchclocks())
        case 'running' | 'r':
            print(get_running())
        case _:
            eprint('ERROR: Invalid args, enter "clock" to show help')
            exit(1)

if __name__ == '__main__':
    main() # run driver code
