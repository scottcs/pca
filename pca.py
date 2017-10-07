#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Paired Comparison Analysis tool"""

import argparse
import cmd
from operator import itemgetter


class Comparison(object):
    """Comparison of two items"""

    def __init__(self, one, two):
        self._items = (one, two)
        self.weight = 0

    @property
    def best(self):
        """best property"""
        return self._items[0]

    @property
    def worst(self):
        """worst property"""
        return self._items[1]

    def request_best(self):
        best = ''
        while best.lower() not in ('a', 'b'):
            print('Which is best?')
            print('  [A] {}\n  [B] {}'.format(*self._items))
            best = input('A or B? ').strip()
        self.set_best(self._items[ord(best.lower())-97])

    def request_weight(self):
        weight = 0
        while weight < 1 or weight > 3:
            print('{} > {}'.format(*self._items))
            answer = input('  by how much [1 is a little, 3 is a lot] (1-3)? ')
            try:
                weight = int(answer)
            except ValueError:
                weight = 0
        self.weight = weight

    def set_best(self, item):
        if item not in self._items:
            raise RuntimeError('Unknown item in comparison: {}'.format(item))
        if item == self.worst:
            self._items = (self._items[1], self._items[0])

    def __eq__(self, other):
        return other.best in self._items and other.worst in self._items

    def __str__(self):
        return '{} > {} ({})'.format(*self._items, self.weight)


class PCA(cmd.Cmd):
    """Command loop"""

    def __init__(self, *args, **kwargs):
        items = kwargs.pop('items', None)
        self._outfile = kwargs.pop('outfile', None)
        super(PCA, self).__init__(*args, **kwargs)
        if items:
            self._items = set(items)
        else:
            self._items = set()
        self._comparisons = []
        self.prompt = 'pca> '

    def preloop(self):
        print('================================')
        print('|| Paired Comparison Analysys ||')
        print('================================')
        print('Step 1: "add <item>" for each item to compare')
        print('Step 2: "compare" to compare all items')
        print('Step 3: "weigh" to set weights')
        if self._items:
            self._list_in_order()

    def postcmd(self, stop, _):
        self._list_in_order()
        return stop

    def _list_in_order(self, quiet=False):
        """list all items in order"""
        final = {}
        total = 0
        lines = []
        for comparison in self._comparisons:
            final.setdefault(comparison.best, 0)
            final.setdefault(comparison.worst, 0)
            final[comparison.best] += comparison.weight
            total += comparison.weight
        if not quiet:
            print('------------------------------------------------------')
        if final:
            weighted = False
            for i, item in enumerate(sorted(final.items(), key=itemgetter(1), reverse=True)):
                weighted = weighted or item[1] != 0
                if weighted:
                    pos = str(i + 1)
                    percentage = '{:>2}%'.format(int(((float(item[1]) / float(total)) * 100.0) + 0.5))
                else:
                    pos = '?'
                    percentage = '?'
                lines.append('{}: [{}] {}'.format(pos, percentage, item[0]))
        else:
            for item in self._items:
                lines.append('?: {}'.format(item))
        if not quiet:
            for line in lines:
                print(line)
            print('------------------------------------------------------')
        return lines

    def _write_to_file(self):
        if self._outfile:
            with open(self._outfile, 'w') as f:
                f.writelines('\n'.join(self._list_in_order(quiet=True)))

    def do_add(self, line):
        """add an item to the list"""
        self._items.add(line)

    def do_compare(self, _):
        """compare all items in the list"""
        self._comparisons = []
        for item1 in self._items:
            for item2 in self._items:
                if item1 != item2:
                    comparison = Comparison(item1, item2)
                    if comparison not in self._comparisons:
                        self._comparisons.append(comparison)
                        comparison.request_best()

    def do_weigh(self, _):
        """set weights for each comparison"""
        for comparison in self._comparisons:
            comparison.request_weight()

    def do_quit(self, _):
        """quit the program"""
        self._write_to_file()
        return True

    def do_EOF(self, _):
        """End of file = quit"""
        print()
        self._write_to_file()
        return True


def parse_args():
    """Parse command-line arguments and return parse obj"""
    parser = argparse.ArgumentParser(prog=__file__, description='performs Paired Comparison Analysis')
    parser.add_argument('-f', '--file',
                        action='store',
                        help='Get list of options from a text file (one per line)')
    parser.add_argument('-o', '--output',
                        action='store',
                        help='Output results to file')
    return parser.parse_args()


def main():
    """ Main function """
    args = parse_args()
    items = None
    if args.file:
        with open(args.file) as f:
            items = [line.rstrip() for line in f]
    return PCA(items=items, outfile=args.output).cmdloop()


if __name__ == '__main__':
    main()
