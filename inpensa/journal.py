"""journal.py: module containing description of Journal class.

Author: Zachary J. Denman
Date: 2018-03-17
"""

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

    def calculate_statistics(self):
        """Compute statistics for the journal.

        The current computations are 1, 3, and 6-month totals on a per category
        and sub-category grouping.
        """
        # Reset totals for each calculation
        # TODO: Compute the statistics

        return


if __name__ == '__main__':
    test = Journal()
    print(test.expenses)
    print()
    test.add_expense('2018-03-17', 'test', 123.45, 'Entertainment', 'Movies')
    print(test.expenses)
    print()
    test.add_expense('2018-03-19', 'test', 567.89, 'Entertainment', 'Books')
    print(test.expenses)

