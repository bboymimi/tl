#!/usr/bin/python3
# Add a new task to the gtimelog log file.
# Propose a list of task if only the category is supplied
#
# Copyright (c) 2015 Canonical Ltd.
# Author: Louis Bouchard <louis.bouchard@ubuntu.com>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.

import argparse
import re
import sys
import datetime
from os.path import expanduser
from gtimelog.timelog import TimeWindow
virtual_midnight = datetime.time(2, 0)

LogFile = '%s/.local/share/gtimelog/timelog.txt' % expanduser("~")

Categories = {
    'ua': 'L3 / L3 support',
    'lp': 'Launchpad & Public',
    'train': 'Mentoring / Edu / Training',
    'meet': 'Meetings',
    'seg': 'SEG related activities',
    'charm': 'Charm Devel',
    'doc': 'Documentation',
    'kb': 'Knowledge base Work',
    'z': 'Mainframe related',
    'ib': 'Mellanox related',
    'svvp': 'SVVP/Virtio dev',
    'qe': 'QE',
    'fan': 'Fan development',
    'is': 'IS bug work',
    'pers': 'Personal management',
    'skill': 'Skills building',
    'team': 'Team support',
    'comm': 'Community Involvment',
    'pto': 'Paid Timeout',
    }

ListLimit = 10


def print_categories():
    for k in sorted(Categories):
        print(k)


def print_tasks(category, **kwargs):
    tasks = get_tasks(category)
    if "escape" in kwargs and kwargs["escape"]:
        new_tasks = [t.replace(" ", "\\ ") for t in tasks]
        tasks = new_tasks
    print("\n".join(tasks))


def show_help():
    try:
        # python3-prettytable will be used if installed
        import prettytable
        categories = prettytable.PrettyTable(["Key", "Description"],
                                             sortby="Key", padding_width=1)
        categories.align["Key"] = "l"
        categories.align["Description"] = "l"
        categories.padding_width = 1
        for keys, description in Categories.items():
            categories.add_row([keys, description])
        print(categories)
    except:
        for keys, description in Categories.items():
            print("%s : %s" % (keys, description))


def get_tasks(category):
    cases = []
    regex = re.compile(r'{}'.format(Categories[category]))
    with open(LogFile, 'r') as timelog:
        all_cases = timelog.readlines()
    all_cases.reverse()
    for line in all_cases:
        if regex.findall(line):
            case = regex.split(line)[-1].strip()
            if case.lstrip(": ") not in cases:
                cases.append(case.lstrip(": "))
    return cases


def select_tasks(category):
    cases = get_tasks(category)
    mytask = 0
    for I in cases:
        if (cases.index(I) + 1) % ListLimit:
            print("{}) {}".format(cases.index(I) + 1, I))
        else:
            # account for modulo = 0 item
            print("{}) {}".format(cases.index(I) + 1, I))
            if cases.index(I) + 1 < len(cases):
                try:
                    mytask = input("Select task (0 to exit,<CR> to continue): "
                                   )
                    if mytask == '0':
                        return(None, None)
                    if mytask == '' or not mytask.isdecimal():
                        continue
                    else:
                        mytask = int(mytask)
                        break

                except KeyboardInterrupt:
                    print("Terminated\n")
                    sys.exit(1)

    if not mytask:
        try:
            mytask = input("Select task (0 or <CR> to exit): ")
            if mytask == '0' or mytask == '' or not mytask.isdecimal():
                return(None, None)
            else:
                mytask = int(mytask)

        except KeyboardInterrupt:
            print("Terminated\n")
            sys.exit(1)

    if mytask > 0 and mytask <= len(cases):
        return(category, cases[mytask - 1])
    else:
        print("Invalid task number")
        return(None, None)


def task_summary(category, task=None):

    total_delta = datetime.timedelta()
    today = datetime.datetime.today()
    epoch = datetime.datetime(1970, 10, 1)
    log_entries = TimeWindow(LogFile, epoch, today, virtual_midnight)
    entries, _ = log_entries.categorized_work_entries()

    for (_, entry, entry_time) in entries[Categories[category] + ' ']:
        if entry.lstrip() == task:
            total_delta += entry_time
    print("total time spent on %s : %d.%d" % (
        task, int(total_delta.seconds / 3600) + int(total_delta.days * 24),
        int(total_delta.seconds / 60 % 60)))
    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('task', nargs='*',
                        help='category | category : task title')
    parser.add_argument('-c', '--list-categories',
                        help='list available task categories',
                        action='store_true')
    parser.add_argument('-t', '--list-tasks', nargs=1, metavar='CATEGORY',
                        help='list available tasks for a given category')
    parser.add_argument('-r', '--raw',
                        help='produce raw output (without pretty formatting)',
                        action='store_true')
    args = parser.parse_args()

    if args.list_categories:
        if args.raw:
            print_categories()
        else:
            show_help()
        sys.exit(0)

    if args.list_tasks:
        print_tasks(args.list_tasks[0], escape=args.raw)
        sys.exit(0)

    if args.task:
        if len(args.task) == 1:
            if args.task[0] == '?':
                show_help()
                sys.exit(0)
            elif args.task[0] in Categories:
                (category, task) = select_tasks(args.task[0])
                if category:
                    task_summary(category, task)
            else:
                print("Unknown category : %s" % args.task[0])
        else:
            show_help()
    else:
        parser.print_help()
    sys.exit(0)
