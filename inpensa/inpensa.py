"""Inpensa: A simple expense tracking application.

Usage:
  inpensa.py init
  inpensa.py [--journal=<file>] add expense [--date=<date> --name=<name> --amount=<amount>]
  inpensa.py [--journal=<file>] add category <category-name> <sub-category-name>
  inpensa.py [--journal=<file>] remove expense
  inpensa.py [--journal=<file>] remove category
  inpensa.py show expenses --n=<n>
  inpensa.py show categories
  inpensa.py show statistics
  inpensa.py (-h | --help)
  inpensa.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
"""

import datetime
import json
import os

import docopt
import prettytable

import journal


class Inpensa:
    """The Inpensa command-line interface."""
    
    def __init__(self, args):
        """Initialise the command-line interface for Inpensa.

        Process the user's input according to the options provided.

        :param dict args: dictionary of arguments from docopt.
        """
        print('==============================================')
        print('|                                            |')
        print('|                Inpensa v0.1                |')
        print('|                                            |')
        print('==============================================')
        self.args = args
        # Load journal
        if self.args['init']:
            print('== Creating a new journal')
            name = input('  -- Enter a name for the journal (journal.json): ')
            # Check and edit the entered filename appropriately
            if name.strip() == '':
                name = 'journal.json'
            elif not name.endswith('.json'):
                name = name + '.json'
            # Check if journal exists. If so, backup original.
            if os.path.exists(name):
                os.replace(name, name + '.orig')
            # Create a new journal
            self.journal = journal.Journal(name, new=True)
            print('== New journal created')
            print('  -- Location: {0:s}'.format(
                os.path.abspath(self.journal.abs_filename)))
            return  # If user ran 'init', only create the new journal and exit.
        
        # If no 'journal' provided, assume a default name.
        if self.args['--journal'] is None:
            self.filename = 'journal.json'
        else:
            self.filename = self.args['--journal']
        
        try:
            self.journal = journal.Journal(self.filename)
        except FileNotFoundError:
            print('Cannot find the journal file requested.')
            print('File requested: {0:s}'.format(self.filename))
            return
        except json.decoder.JSONDecodeError:
            print('Something wrong with the journal file requested.')
            print('File requested: {0:s}'.format(self.filename))
            return
        print('== Loaded journal: {0:s}'.format(self.filename))

        # Processing commands
        if self.args['add']:
            if self.args['expense']:
                if not self.journal.categories:
                    print('No categories/sub-categories in journal.\n')
                    print('Use \'inpensa add category <name> <sub-name>\' to '
                          'add.')
                    return
                print('== Adding expense')
                self.add_expense()
            elif self.args['category']:
                print('== Adding category')
                c = self.args['<category-name>'].strip()
                sc = self.args['<sub-category-name>'].strip()
                if c in self.journal.categories:
                    if sc in self.journal.categories[c]:
                        print('\'{0:s}\' already in \'{1:s}\''.format(
                            sc, self.journal.filename))
                        return
                    else:
                        self.journal.categories[c].append(sc)
                        self.journal.categories[c].sort(key=str.lower)
                else:
                    # Add new category with current sub-category as first item
                    self.journal.categories[c] = [sc]
                print('  -- \'{0:s}: {1:s}\' was added to \'{2:s}\''.format(
                    c, sc, self.journal.filename))

            # After doing some work write changes to file.
            self.journal.write(self.filename)

        if self.args['show']:
            if self.args['expenses']:
                self.show_expenses()
            elif self.args['categories']:
                self.show_categories()
            elif self.args['statistics']:
                self.show_statistics()
            

        return

    def add_expense(self):
        """Process the user input and add the expense to the journal.
        
        First check if any of the optional command line arguments were used.
        If valid inputs were provided, 
        """
        # Need to set initial values for date and name to allow checks to take
        # place. Initial value not need for amount as it is not compared to
        # any other expense to check for duplicates.
        date = None
        name = None
        # Flags for expense properties
        valid_date = False
        valid_name = False
        valid_amount = False
        category_selected = False
        subcategory_selected = False
        # Check if any optional arguments are provided and if they are valid.
        if self.args['--date']:
            try:
                year, month, day = self.args['--date'].strip().split('-')
                date = datetime.date(
                    int(year), int(month), int(day)).isoformat()
                valid_date = True
            except ValueError:
                print('Date provided to \'--date\' was invalid.')
        # Any string is a valid name so just check if '--name' was provided and
        # store the value.
        if self.args['--name']:  
            name = self.args['--name']
            valid_name = True
        if self.args['--amount']:
            try:
                amount = float(self.args['--amount'])
                valid_amount = True
            except ValueError:
                print('Amount provided to \'--amount\' was invalid.')
        
        # Check that a duplicate does not already exist in journal. If an
        # invalid date was provided at the command line, date will be 'None',
        # resulting in the user being prompted at the next stage. Similarly,
        # if a 
        if date in self.journal.expenses.keys():
            # Check that name does not exist
            if name in self.journal.expenses[date]:
                print('This expense date/name already exists in journal. '
                      'Please enter a new name for the expense.')
                valid_name = False

        # If optional arguments are not used, prompt user.
        while not valid_date:
            try:
                date = input('  -- Enter date (YYYY-MM-DD): ')
                year, month, day = date.strip().split('-')
                date = datetime.date(
                    int(year), int(month), int(day)).isoformat()
                valid_date = True
            except ValueError:
                print('Please enter a date in required format (YYYY-MM-DD).')
        while not valid_name:
            try:
                name = input('  -- Enter expense name: ')
                name = name.strip()
                if name == '':
                    print('Expense name cannot be empty.')
                elif name in self.journal.expenses[date]:
                    print('This expense already exists in journal.')
                else:
                    valid_name = True
            except KeyError:
                # Date does not exist in journal, therefore expense cannot be
                # duplicate so we have a valid name. 
                valid_name = True
        while not valid_amount:
            try:
                amount = float(input('  -- Expense amount ($): '))
                if amount <= 0.0:
                    print('Expense amount must be a positive number.')
                else:
                    valid_amount = True
            except ValueError:
                print('Please enter a number for the expense amount.')
        temp_categories = {}
        print('  -- Category selection')
        for i, category in enumerate(self.journal.categories.keys()):
            print('      {0: 3d}) {1:s}'.format(i+1, category))
            temp_categories[i+1] = category
        while not category_selected:
            try:
                i = int(input('  -- Enter category number: '))                        
                category = temp_categories[i]
                category_selected = True
            except ValueError:
                print('Please enter a valid category number.')
            except KeyError:
                print('Please enter a valid category number.')
        subcategories = self.journal.categories[category]
        print('  -- Subcategory selection')
        for i, subcategory in enumerate(subcategories):
            print('      {0: 3d}) {1:s}'.format(i+1, subcategory))
        while not subcategory_selected:
            try:
                i = int(input('  -- Enter subcategory number: '))                        
                subcategory = subcategories[i-1] 
                subcategory_selected = True
            except ValueError:
                print('Please enter a valid subcategory number.')
            except IndexError:
                print('Please enter a valid subcategory number.')

        self.journal.add_expense(date, name, amount, category, subcategory)

        return


    def show_categories(self):
        """Print the categories in the loaded journal."""
        print('== Categories')
        for category in self.journal.categories.keys():
            print('  -- {0:s}'.format(category))
            for subcategory in self.journal.categories[category]:
                print('      {0:s}'.format(subcategory))

    def show_expenses(self):
        """Print last 'n' expenses - 'n' is retrieved from the --n argument.

        :param int n: the number of expenses whose details will be provided.
        """
        print('  -- Showing last {0:s} expenses\n'.format(self.args['--n']))
        table = prettytable.PrettyTable()
        table.field_names = ['Date', 'Name', 'Amount', 'Category',
                             'Subcategory']
        table.align['Name'] = 'l'
        table.align['Amount'] = 'r'
        table.align['Category'] = 'l'
        table.align['Subcategory'] = 'l'
        table.float_format['Amount'] = '.2'
        n_printed = 0
        exp = self.journal.expenses
        for date in sorted(exp.keys(), reverse=True):
            for name, details in sorted(exp[date].items(), reverse=True):
                if n_printed == int(self.args['--n']):
                    break
                table.add_row([date, name, details['amount'],
                              details['category'], details['subcategory']])
                n_printed += 1
        
        print(table)

        return

    def show_statistics(self):
        """Pretty print expense statistics."""
        print('This is where the expense will be printed')
        print('== Expense statistics')
        print('  -- Calculate statistics...', end='')
        # print(self.args)
        today = datetime.date.today()
        one_month = today.replace(month=today.month-1)
        # three_month = today.month - 3
        # six_month = today.month - 6
        print(one_month.isoformat())

        # one_month, three_month, six_month = datetime.timedelta(months=1)
        self.journal.calculate_statistics()
        print('Done')
        print('  -- Print statistics\n')
        table = prettytable.PrettyTable()


        return

if __name__ == '__main__':
    arguments = docopt.docopt(__doc__, version='0.1')
    app = Inpensa(arguments)
