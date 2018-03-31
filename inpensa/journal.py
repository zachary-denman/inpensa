"""journal.py: module containing description of Journal class.

Author: Zachary J. Denman
Date: 2018-03-17
"""

import datetime
import math
import os

import json


class Journal:
    """A Journal object holds all tracked expenses."""

    def __init__(self, filename='journal.json', new=False):
        """Initialise a Journal object from filename.

        A journal is a simple nested dictionary/list structure for holding
        categories/sub-categories and expenses (and their associated data).

        :param str filename: filename of the journal file to be read.
        :param bool new: flag for creating a new journal.
        """
        self.filename = filename
        self.abs_filename =  os.path.abspath(self.filename)

        if new:
            self.create_new_journal()
            return

        with open(self.filename, 'r') as fp:
            self.data = json.load(fp)

        # Convenient names
        self.categories = self.data['categories']
        self.expenses = self.data['expenses']
       
        return

    def write(self, output_filename):
        """Write current journal to file.
        
        :param str output_filename: filename to save the journal to.
        """
        with open(self.filename, 'w') as fp:
            json.dump(self.data, fp, sort_keys=True, indent=4)

        return

    def add_expense(self, date, name, amount, category, subcategory):
        """Add an expense to the Journal."""
        # Retrieve current expenses for that date if any exist, if not add new
        # dict for that date.
        if date in self.expenses:
            self.expenses[date][name] = {'amount': amount,
                                         'category': category,
                                         'subcategory': subcategory}
        else:
            self.expenses[date] = {}
            self.add_expense(date, name, amount, category, subcategory)

        return

    def create_new_journal(self):
        """Create a new journal file.
        
        Three dictionaries for holding the required information.
        """
        empty_file = {'categories': {},
                      'expenses': {}}
        self.data = empty_file
        self.write(self.filename)

        return

    def calculate_statistics(self, start, end):
        """Compute statistics for the journal.

        """
        # Reset totals for each calculation
        dt = datetime.timedelta(days=1)
        year, month, day = [int(item) for item in start.split('-')]
        start_date = datetime.date(year, month, day)
        year, month, day = [int(item) for item in end.split('-')]
        end_date = datetime.date(year, month, day)

        if start_date > end_date:
            print('Start date after end date.')
            return

        self.statistics = {}
        for category in self.categories.keys():
            self.statistics[category] = {'total': 0.0,
                                         'subcategories': {}}
            for subcategory in self.categories[category]:
                self.statistics[category]['subcategories'][subcategory] = 0
        # Iterate through expenses from start adding each one to its
        # corresponding category/subcategory total
        date = start_date
        while date <= end_date:
            if date.isoformat() in self.expenses:
                for name, details in self.expenses[date.isoformat()].items():
                    amount = details['amount']
                    category = details['category']
                    subcategory = details['subcategory']
                    self.statistics[category]['total'] += amount
                    self.statistics[category]['subcategories'][subcategory] += amount
            date += dt

        return


if __name__ == '__main__':
    test.calculate_statistics('2018-01-01', '2018-02-28')

