import datetime
import os
import numpy as np
import tkinter as tk
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox
from bokeh.palettes import Category20_20

__author__: 'Brandon Dos Remedios | git: @bdosremedios'


class BankingHistory():
    """ Object containing calculated history of banking account with seperated
    chequing, saving, and total banking, and method for generating a summary
    of it.

    Attributes
    ---
    initial_cheq_balance : float
        Initial balance in chequing account.
    initial_save_balance : float
        Initial balance in saving account.
    initial_bank_balance : float
        Initial balance in banking account.
    cheq_days : list of datetime.datetime
        Days of chequing account transactions.
    cheq_daily_changes : list of tuple(datetime.datetime, float)
        List of tuples of dates and changes to chequing account on date.
    cheq_daily_balances : list of tuple(datetime.datetime, float)
        List of tuples of dates and balance of chequing account on date.
    cheq_months : list of datetime.datetime
        Months of chequing account transactions.
    cheq_monthly_changes : list of tuple(datetime.datetime, float)
        List of tuples of months and changes to chequing account on month.
    cheq_initial_monthly_balances : list of tuple(datetime.datetime, float)
        List of tuples of months and changes to chequing account on month.
    save_days : list of datetime.datetime
        Days of saving account transactions.
    save_daily_changes : list of tuple(datetime.datetime, float)
        List of tuples of dates and changes to saving account on date.
    save_daily_balances : list of tuple(datetime.datetime, float)
        List of tuples of dates and balance of saving account on date.
    save_months : list of datetime.datetime
        Months of saving account transactions.
    save_monthly_changes : list of tuple(datetime.datetime, float)
        List of tuples of months and changes to saving account on month.
    save_initial_monthly_balances : list of tuple(datetime.datetime, float)
        List of tuples of months and changes to saving account on month.
    bank_days : list of datetime.datetime
        Days of banking account transactions.
    bank_daily_changes : list of tuple(datetime.datetime, float)
        List of tuples of dates and changes to banking account on date.
    bank_daily_balances : list of tuple(datetime.datetime, float)
        List of tuples of dates and balance of banking account on date.
    bank_months : list of datetime.datetime
        Months of banking account transactions.
    bank_monthly_changes : list of tuple(datetime.datetime, float
        List of tuples of months and changes to banking account on month.
    bank_initial_monthly_balances : list of tuple(datetime.datetime, float)
        List of tuples of months and changes to banking account on month.

    """
    def __init__(self, initial_chequing, initial_saving, chequing_csv,
                 saving_csv):
        """ Carries out calculation of banking history, for daily and monthly
        increments, for chequing, saving, and banking accounts.

        Parameters
        ---
        initial_chequing : float
            Initial balance in chequing account.
        initial_saving : float
            Initial balance in saving account.
        chequing_csv : str
            Path to csv of transactions to and from chequing account.
        saving_csv : str
            Path to csv of transactions to and from saving account.

        """
        # Initial balance for both accounts on first day of transaction
        # history (balance listed alongside that first day after changes)
        self.initial_cheq_balance = initial_chequing
        self.initial_save_balance = initial_saving
        
        # Load transaction history for each account
        chequing_csvs = np.genfromtxt(
            chequing_csv, delimiter=',', dtype=None, encoding=None)
        saving_csvs = np.genfromtxt(
            saving_csv, delimiter=',', dtype=None, encoding=None)

        # Extract dates, and account changes on those dates
        cheq_days, cheq_changes = self.extract_datetime_accountchange(
                chequing_csvs)
        save_days, save_changes = self.extract_datetime_accountchange(
                saving_csvs)

        # Collapse dates and changes to a total account change on each date
        cheq_unique_days, cheq_daily_changes = self.collapse_date_change(
                cheq_days, cheq_changes)
        save_unique_days, save_daily_changes = self.collapse_date_change(
                save_days, save_changes)
        
        # Flip days and daily_changes so time increase rightwards in list
        cheq_unique_days.reverse()
        cheq_daily_changes.reverse()
        save_unique_days.reverse()
        save_daily_changes.reverse()

        # Fill in days with no account changes with a 0. value account change,
        # So that future plotting and statistics have a more consistent daily
        # time interval to evaluate by
        cheq_fill_days, cheq_fill_daily_changes = self.fill_no_transact_days(
                cheq_unique_days, cheq_daily_changes)
        save_fill_days, save_fill_daily_changes = self.fill_no_transact_days(
                save_unique_days, save_daily_changes)

        # Correct balances, by subtracting first day total change, so that
        # balances are of changes immediately previous to change history
        self.initial_cheq_balance -= cheq_daily_changes[0]
        self.initial_save_balance -= save_daily_changes[0]

        # Convert daily changes into a daily balance
        cheq_daily_balances = self.convert_changes_to_balances(
                self.initial_cheq_balance, cheq_fill_daily_changes)
        save_daily_balances = self.convert_changes_to_balances(
                self.initial_save_balance, save_fill_daily_changes)

        # Define object attributes for chequing account info
        self.cheq_days = cheq_fill_days
        self.cheq_daily_changes = cheq_fill_daily_changes
        self.cheq_daily_balances = cheq_daily_balances

        # Grab chequing account info per month from per day
        cheq_months, cheq_monthly_changes, cheq_monthly_balances = \
            self.get_monthly_change_balance(self.cheq_days,
                                            self.cheq_daily_changes,
                                            self.cheq_daily_balances)

        # Define object attributes for monthly chequing account info
        self.cheq_months = cheq_months
        self.cheq_monthly_changes = cheq_monthly_changes
        self.cheq_initial_monthly_balances = cheq_monthly_balances

        # Define object attributes for saving account info
        self.save_days = save_fill_days
        self.save_daily_changes = save_fill_daily_changes
        self.save_daily_balances = save_daily_balances

        # Grab saving account info per month from per day
        save_months, save_monthly_changes, save_monthly_balances = \
            self.get_monthly_change_balance(self.save_days,
                                            self.save_daily_changes,
                                            self.save_daily_balances)

        # Define object attributes for monthly chequing account info
        self.save_months = save_months
        self.save_monthly_changes = save_monthly_changes
        self.save_initial_monthly_balances = save_monthly_balances

        # Aggregate chequing and saving information into total banking info
        bank_days = self.cheq_days + self.save_days
        bank_changes = self.cheq_daily_changes + self.save_daily_changes

        # Collapse dates and changes to a total account change on each date
        bank_unique_days, bank_daily_changes = self.collapse_date_change(
                bank_days, bank_changes)

        # Flip days and daily_changes so time increase rightwards in list
        bank_unique_days.reverse()
        bank_daily_changes.reverse()

        # Fill in days with no account changes with a 0. value account change,
        # So that future plotting and statistics have a more consistent daily
        # time interval to evaluate by
        bank_fill_days, bank_fill_daily_changes = self.fill_no_transact_days(
                bank_unique_days, bank_daily_changes)

        # Grab initial balance for combined accounts before any transactions.
        # The initial change subtraction has already happened individually
        # for chequing and saving initial balance so does not need to happen
        # again
        self.initial_bank_balance = (self.initial_cheq_balance +
                                     self.initial_save_balance)

        # Convert daily changes into a daily balance
        bank_daily_balances = self.convert_changes_to_balances(
                self.initial_bank_balance, bank_fill_daily_changes)

        # Define object attributes for total banking (combined saving and
        # chequing accounts) info
        self.bank_days = bank_fill_days
        self.bank_daily_changes = bank_fill_daily_changes
        self.bank_daily_balances = bank_daily_balances
        
        # Grab combined accounts info per month from per day
        bank_months, bank_monthly_changes, bank_monthly_balances = \
            self.get_monthly_change_balance(self.bank_days,
                                            self.bank_daily_changes,
                                            self.bank_daily_balances)

        # Define object attributes for monthly chequing account info
        self.bank_months = bank_months
        self.bank_monthly_changes = bank_monthly_changes
        self.bank_initial_monthly_balances = bank_monthly_balances

    def extract_datetime_accountchange(self, csv_rows):
        """ From the loaded csv list of tuples of strings, extract a list of
        dates into datetimes, and extract a list of changes in accounts to
        float numbers.

        Parameters
        ---
        csv_rows : list
            List of tuples of strings loaded from the transaction history csv,
            for the respective account. The first string in each tuple
            represents the date of a transaction, and the second represents
            the amount the account changed by.

        Returns
        ---
        dates_list : list
            List of datetime.datetime objects of all transaction dates, in
            same order as changes_list.
        changes_list : list
            List of floats of all account changes on dates, in same order as
            dates_list.

        """
        dates_list = []
        changes_list = []
        for date_string, account_change, dump1, dump2, dump3 in csv_rows:
            date_temp = datetime.datetime.strptime(date_string, "%m/%d/%Y")
            dates_list.append(date_temp)
            changes_list.append(round(float(account_change), 2))

        return(dates_list, changes_list)

    def collapse_date_change(self, list_of_dates, list_of_changes):
        """ Take a list of dates and account changes on that date, and
        collapse them into a list of unique dates, and the total account
        change on each unique date. In other words grabbing daily changes, and
        dates of those changes.

        Parameters
        ---
        list_of_dates : list
            List of datetime.datetime objects representing the date of each
            account change in list_of_changes.
        list_of_changes : list
            List of floats representing change in account balance on each day.

        Returns
        ---
        collapsed_dates : list
            List of datetime.datetime objects representing unique dates in
            list_of_dates. Sorted in increasing time order.
        collapsed_changes : list
            List of floats of total account changes on dates.

        """
        # Get unique dates and sort them
        unique_dates = list(set(list_of_dates))
        sorted_unique_dates = list(np.flipud(np.sort(unique_dates)))

        # Zip date lists and changes lists to relate changes to dates
        zipped_date_change = list(zip(list_of_dates, list_of_changes))

        # Use sorted list of unique dates to find all account changes on each
        # date, and grab a total change for the date
        collapsed_dates = []
        collapsed_changes = []
        for date_temp in sorted_unique_dates:
            change_on_date = [
                tup[1] for tup in zipped_date_change if tup[0] == date_temp]
            collapsed_dates.append(date_temp)
            collapsed_changes.append(round(sum(change_on_date), 2))

        return(collapsed_dates, collapsed_changes)

    def fill_no_transact_days(self, list_of_dates, list_of_changes):
        """ Fills in non listed days (dates with no transactions) to make
        plotting and monthly time intervals more consistent.

        Parameters
        ---
        list_of_dates : list
            List of datetime.datetime objects representing the date of each
            account change in list_of_changes.
        list_of_changes : list
            List of floats of total account changes on dates, in same order
            as list_of_dates.

        Returns
        ---
        all_days : list
            List of datetime.datetime objects, similar to list_of_dates but
            with no gaps between transaction dates.
        all_changes : list
            List of floats of total account changes on dates, with no
            transaction dates with a 0. value.

        """
        # Set current day to first day given
        current_day = list_of_dates[0]
        last_day = list_of_dates[-1]
        day_delta = datetime.timedelta(days=1)

        # Create dictionary to lookup day and total change on that day
        day_change_lookup = dict(zip(list_of_dates, list_of_changes))

        # For every day until the last day, check if exists in list_of_dates
        # and append the correct change if does. If not in, appends 0
        all_days = []
        all_changes = []
        while(current_day <= last_day):
            all_days.append(current_day)
            if current_day in list_of_dates:
                all_changes.append(day_change_lookup[current_day])
            else:
                all_changes.append(0.)
            current_day += day_delta

        return(all_days, all_changes)

    def convert_changes_to_balances(self, initial_balance, list_of_changes):
        """ Converts list of floats representing account changes, into the
        balance in the account at the time.

        Parameters
        ---
        initial_balance : float
            Amount in account before any changes in list_of_changes.
        list_of_changes : list
            List of floats representing changes to account on each day.

        Returns
        ---
        rounded_balances : list
            List of floats representing balance on each date rounded to the
            cent.

        """
        cumulative_sum_changes = np.cumsum(list_of_changes)
        balances_from_changes = initial_balance + cumulative_sum_changes

        # Round each days balance to 2 decimal places
        rounded_balances = [
            round(balance, 2) for balance in balances_from_changes
            ]

        return(rounded_balances)

    def get_monthly_change_balance(self, list_of_dates, list_of_changes,
                                   list_of_balances):
        """ Collapse daily account changes and balances, into a monthly
        account changes and balances.

        Parameters
        ---
        list_of_dates : list of datetime.datetime
            List of dates corresponding to account changes and balances.
        list_of_changes : list of float
            List of account changes.
        list_of_balances : list of float
            List of account balances.

        Returns
        ---
        sorted_unique_month_years : list of datetime.datetime
            List of dates of months for each months' account changes and
            balances.
        monthly_account_changes
            List of total monthly account changes.
        monthly_account_balances
            List of initial monthly account balances

        """
        # Zip dates to changes and balances, and convert dates into just month
        # and year, with day for all set to the first of the month.
        zipped_day_change_balance = list(zip(list_of_dates,
                                             list_of_changes,
                                             list_of_balances))

        zipped_month_change_balance = [
            (datetime.datetime(day=1, month=date.month, year=date.year),
             change,
             balance)
            for date, change, balance in zipped_day_change_balance
        ]

        # Grab sorted list of unique month, year combos to iterate and
        # collapse on each
        month_years = [tup[0] for tup in zipped_month_change_balance]
        sorted_unique_month_years = list(np.sort(list(set(month_years))))

        # For each month year, grab the balance at the start of the month
        # and total account changes on that month
        monthly_account_changes = []
        monthly_account_balances = []
        for month_year_temp in sorted_unique_month_years:

            change_on_month = [
                change for
                month_year, change, balance in zipped_month_change_balance
                if month_year == month_year_temp
            ]

            # Get initial balance for each month. If data starts after the
            # first day of the first month, will get IndexError and thus just
            # use first balance in history as that will be first date.
            try:
                initial_month_balance = [
                    balance
                    for date, change, balance in zipped_day_change_balance
                    if date == month_year_temp
                ][0]
            except IndexError:
                initial_month_balance = zipped_day_change_balance[0][2]

            monthly_account_changes.append(round(sum(change_on_month), 2))
            monthly_account_balances.append(initial_month_balance)

        return(sorted_unique_month_years, monthly_account_changes,
               monthly_account_balances)

    def plot_pdf(self, pdf_path):
        """
        """
        plt.style.use('ggplot')

        fig = plt.figure(figsize=(12, 18))
        spec = gridspec.GridSpec(ncols=2, nrows=4, figure=fig)

        # Plot title axes stating initial and final balances for accounts
        title_ax = fig.add_subplot(spec[0, 0:2])
        title_ax.grid(False)
        title_ax.text(0., 1., 'Financial Summary', fontsize=50)
        title_ax.text( .02, .9,
                      'Created on {}'.format(
                          datetime.datetime.strftime(
                              datetime.datetime.now(),
                              '%A, %B %d %Y %H:%M:%S')),
                      fontsize=14)
        title_ax.text(.02, .65, 'Initial Balance', fontsize=20)
        title_ax.text(.02, .55, 'Initial Date: {}'.format(
            datetime.datetime.strftime(self.bank_days[0],
                                       '%A, %B %d %Y')),
            fontsize=14, va='top')
        title_ax.text(.02, .45,
                      'Chequing: {}'.format(self.cheq_daily_balances[0]),
                      fontsize=14, va='top')
        title_ax.text(.02, .35,
                      'Saving: {}'.format(self.save_daily_balances[0]),
                      fontsize=14, va='top')
        title_ax.text(.02, .25,
                      'Total: {}'.format(self.bank_daily_balances[0]),
                      fontsize=14, va='top')
        title_ax.text(.51, .65, 'Final Balance', fontsize=20)
        title_ax.text(.51, .55, 'Final Date: {}'.format(
            datetime.datetime.strftime(self.bank_days[-1],
                                       '%A, %B %d %Y')),
            fontsize=14, va='top')
        title_ax.text(.51, .45,
                      'Chequing: {}'.format(self.cheq_daily_balances[-1]),
                      fontsize=14, va='top')
        title_ax.text(.51, .35,
                      'Saving: {}'.format(self.save_daily_balances[-1]),
                      fontsize=14, va='top')
        title_ax.text(.51, .25,
                      'Total: {}'.format(self.bank_daily_balances[-1]),
                      fontsize=14, va='top')
        title_ax.tick_params(axis='both', labelbottom=False, labelleft=False,
                             left=False, bottom=False)

        # Plot changes to chequing account to give an idea on general spending
        cheq_change_ax = fig.add_subplot(spec[1, 0:2])
        cheq_change_ax.bar(
            np.array(self.cheq_months)[np.array(self.cheq_monthly_changes)>0],
            np.array(self.cheq_monthly_changes)[
                np.array(self.cheq_monthly_changes)>0],
                12, color=Category20_20[4])
        cheq_change_ax.bar(
            np.array(self.cheq_months)[np.array(self.cheq_monthly_changes)<0],
            np.array(self.cheq_monthly_changes)[
                np.array(self.cheq_monthly_changes)<0],
                12, color=Category20_20[6])
        cheq_change_ax.bar(
            np.array(self.cheq_months)[
                np.array(self.cheq_monthly_changes)==0],
            np.array(self.cheq_monthly_changes)[
                np.array(self.cheq_monthly_changes)==0],
                12, color=Category20_20[0])
        cheq_change_ax.set_ylabel('Chequing Account Changes')
        cheq_change_ax.margins(x=0.025)

        # Plot changes to entire banking account to see general change trend
        # in easier colored visual (More green is good, more red is bad)
        bank_change_ax = fig.add_subplot(spec[2, 0:2])
        bank_change_ax.bar(
            np.array(self.bank_months)[
                np.array(self.bank_monthly_changes)>0],
            np.array(self.bank_monthly_changes)[
                np.array(self.bank_monthly_changes)>0],
                12, color=Category20_20[4])
        bank_change_ax.bar(
            np.array(self.bank_months)[
                np.array(self.bank_monthly_changes)<0],
            np.array(self.bank_monthly_changes)[
                np.array(self.bank_monthly_changes)<0],
                12, color=Category20_20[6])
        bank_change_ax.bar(
            np.array(self.bank_months)[
                np.array(self.bank_monthly_changes)==0],
            np.array(self.bank_monthly_changes)[
                np.array(self.bank_monthly_changes)==0],
                12, color=Category20_20[0])
        bank_change_ax.set_ylabel('Total Bank Changes')
        bank_change_ax.margins(x=0.025)

        # Plot monthly bank balances to see general trajectory of finances
        bank_bal_ax = fig.add_subplot(spec[3, 0:2])
        bank_bal_ax.bar(
            self.bank_months, self.bank_initial_monthly_balances, 12,
            color=Category20_20[0])
        bank_bal_ax.plot(
            self.bank_months, self.bank_initial_monthly_balances, 'o-',
            color=Category20_20[1])
        bank_bal_ax.set_xlabel('Date')
        bank_bal_ax.set_ylabel('Total Bank Balances')
        bank_bal_ax.margins(x=0.025)

        # Save pdf_path, incrementing bracketed number until pdf does not
        # exist, so that previous ones are not overwritten
        initial_pdf_path = pdf_path + '\\FinancialSummary.pdf'
        if os.path.isfile(initial_pdf_path):
            initial_pdf_path = initial_pdf_path.replace('.pdf', ' (1).pdf')
            increment_count = 2
            while(os.path.isfile(initial_pdf_path)):
                initial_pdf_path = initial_pdf_path.replace(
                    '({}).pdf'.format(increment_count-1),
                    '({}).pdf'.format(increment_count))
                increment_count += 1
        plt.savefig(initial_pdf_path)


class InitialInformationApp():

    def __init__(self, parent):

        self.parent = parent
        self.parent.title('Generate Financial Summary')

        style = ttk.Style(self.parent)
        style.theme_use('xpnative')
        self.padx = 10
        self.pady = 5

        # Create variable to check if entries have been confirmed to be valid
        self.entrycheckvalid = False

        # User input for initial balances for accounts
        tk.Label(self.parent, text='Initial Chequing Balance').grid(
            column=0, row=0, padx=self.padx, pady=self.pady, sticky='W')

        tk.Label(self.parent, text='Initial Saving Balance').grid(
            column=1, row=0, padx=self.padx, pady=self.pady, sticky='W')

        self.cheqbalentry = ttk.Entry(self.parent)
        self.cheqbalentry.grid(
            column=0, row=1, padx=self.padx, pady=self.pady, sticky='EW')

        self.savebalentry = ttk.Entry(self.parent)
        self.savebalentry.grid(
            column=1, row=1, padx=self.padx, pady=self.pady, sticky='EW')

        # User input for chequing and saving transaction balances
        tk.Label(self.parent, text='Chequing Transaction History CSV').grid(
            column=0, row=2, padx=self.padx, pady=self.pady, sticky='W')
        
        self.cheqcsventry = ttk.Entry(self.parent)
        self.cheqcsventry.grid(
            column=0, row=3, padx=self.padx, pady=self.pady, sticky='EW',
            columnspan=2)
        
        ttk.Button(
            self.parent, text='Browse',
            command=lambda: self.browseforcsv(self.cheqcsventry)).grid(
                column=1, row=2, padx=self.padx, pady=self.pady, sticky='NSE')
        
        tk.Label(self.parent, text='Savings Transaction History CSV').grid(
            column=0, row=4, padx=self.padx, pady=self.pady, sticky='W')
        
        self.savecsventry = ttk.Entry(self.parent)
        self.savecsventry.grid(
            column=0, row=5, padx=self.padx, pady=self.pady, sticky='EW',
            columnspan=2)

        ttk.Button(
            self.parent, text='Browse',
            command=lambda: self.browseforcsv(self.savecsventry)).grid(
                column=1, row=4, padx=self.padx, pady=self.pady, sticky='NSE')

        # User input for folder to save pdf to
        tk.Label(self.parent, text='Save PDF to Folder').grid(
            column=0, row=6, padx=self.padx, pady=self.pady, sticky='W')
        
        self.pdfentry = ttk.Entry(self.parent)
        self.pdfentry.grid(
            column=0, row=7, padx=self.padx, pady=self.pady, sticky='EW',
            columnspan=2)

        ttk.Button(
            self.parent, text='Browse',
            command=lambda: self.browsefordir(self.pdfentry)).grid(
                column=1, row=6, padx=self.padx, pady=self.pady, sticky='NSE')

        # Generate financial summary
        ttk.Button(self.parent, text='Generate Financial Summary',
                   command=self.checkentriesbeforegeneration).grid(
            column=0, row=8, padx=self.padx, pady=self.pady, sticky='NSWE',
            columnspan=2)

        for i in range(2):
            self.parent.grid_columnconfigure(i, uniform=True)

        for i in range(9):
            self.parent.grid_rowconfigure(i, uniform=True)

        # Fill previous valid entry if history txt file exists
        if os.path.isfile('FinancialViewerPrevEntry.txt'):
            preventriesintxt = np.genfromtxt(
                'FinancialViewerPrevEntry.txt', dtype=str)
            self.cheqbalentry.insert(tk.END, preventriesintxt[0])
            self.savebalentry.insert(tk.END, preventriesintxt[1])
            self.cheqcsventry.insert(tk.END, preventriesintxt[2])
            self.savecsventry.insert(tk.END, preventriesintxt[3])
            self.pdfentry.insert(tk.END, preventriesintxt[4])

        # Update idletaks so widths exist for geometry calculation
        self.parent.update_idletasks()

        # Place in center of screen and lift to front
        self.parent.geometry('+{}+{}'.format(
            int(self.parent.winfo_screenwidth()/2-
                self.parent.winfo_width()/2),
            int(self.parent.winfo_screenheight()/2-
                self.parent.winfo_height()/2)))
        self.parent.lift()

    def browseforcsv(self, entry):
        """ Browses for csv, and change respective entry text upon selection.

        """
        filename = filedialog.askopenfilename(title='Select CSV')
        if filename != '':  # Doesn't change if no file name entered
            entry.delete(0, tk.END)
            entry.insert(tk.END, filename)

    def browsefordir(self, entry):
        """ Browses for directory, and change respective entry text upon
        selection.

        """
        filename = filedialog.askdirectory(title='Select Directory')
        if filename != '':  # Doesn't change if no file name entered
            entry.delete(0, tk.END)
            entry.insert(tk.END, filename)

    def checkentriesbeforegeneration(self):
        """ Checks that entries are valid, destorying window to begin
        generation if are, and opening error message if not.

        """
        cheqbalvalid = False
        savebalvalid = False
        cheqcsvvalid = False
        savecsvvalid = False
        pdfdirvalid = False

        # Check if balance entries are numbers and either floats with zero,
        # one, or two decimal places, or ints.
        if self.checkifnumber(self.cheqbalentry.get()):
            if (self.cheqbalentry.get().isdigit() or
                self.cheqbalentry.get()[-1] == '.' or
                self.cheqbalentry.get()[-2] == '.' or
                self.cheqbalentry.get()[-3] == '.'):
                    cheqbalvalid = True
        if self.checkifnumber(self.savebalentry.get()):
            if (self.savebalentry.get().isdigit() or
                self.savebalentry.get()[-1] == '.' or
                self.savebalentry.get()[-2] == '.' or
                self.savebalentry.get()[-3] == '.'):
                    savebalvalid = True

        # Check if csv entries are a valid file and are either csvs or txts
        if os.path.isfile(self.cheqcsventry.get()):
            if (self.cheqcsventry.get()[-4:] == '.txt' or
                self.cheqcsventry.get()[-4:] == '.csv'):
                    cheqcsvvalid = True
        if os.path.isfile(self.savecsventry.get()):
            if (self.savecsventry.get()[-4:] == '.txt' or
                self.savecsventry.get()[-4:] == '.csv'):
                    savecsvvalid = True

        # Check if save pdf directory is a valid directory
        if os.path.isdir(self.pdfentry.get()):
            pdfdirvalid = True

        # Check if all are valid, activating error box if not, and actiate
        # case generation if is.
        if (cheqbalvalid and savebalvalid and cheqcsvvalid and
            savecsvvalid and pdfdirvalid):

                self.cheqbal = float(self.cheqbalentry.get())
                self.savebal = float(self.savebalentry.get())
                self.cheqcsv = self.cheqcsventry.get()
                self.savecsv = self.savecsventry.get()
                self.pdfdir = self.pdfentry.get()

                # Write out txt of entries for future uses if app
                f = open('FinancialViewerPrevEntry.txt', 'w')
                f.write('{}\n{}\n{}\n{}\n{}'.format(
                    self.cheqbal, self.savebal, self.cheqcsv, self.savecsv,
                    self.pdfdir))
                f.close()

                # Create banking history object containing data for plotting
                banking_hist = BankingHistory(
                    self.cheqbal, self.savebal, self.cheqcsv, self.savecsv)

                # Save plot to given path
                banking_hist.plot_pdf(self.pdfdir)

                # User feedback of successful plot generation
                messagebox.showinfo('Success',
                                    'Financial summary generated.')

        else:
            self.generateerrormessage(
                cheqbalvalid, savebalvalid, cheqcsvvalid, savecsvvalid,
                pdfdirvalid)

    def checkifnumber(self, test_string):
        """ Check if given string is convertable into a float number, meaning
        string is either an int or a float.

        """
        try:
            float(test_string)
            return(True)
        except ValueError:
            return(False)

    def generateerrormessage(self, cheqbalvalid=False, savebalvalid=False,
                             cheqcsvvalid=False, savecsvvalid=False,
                             pdfdirvalid=False):
        """ Generates error message corresponding to entry boxes with
        invalid entries.

        """
        error_message = ''
        if not cheqbalvalid:
            error_message += ('Initial chequing balance must be a number ' +
                              'with a maximum of two decimal places.\n')
        if not savebalvalid:
            error_message += ('Initial saving balance must be a number ' +
                              'with a maximum of two decimal places.\n')
        if not cheqcsvvalid:
            error_message += ('Chequing csv must be an existing .csv or ' +
                              '.txt file.\n')
        if not savecsvvalid:
            error_message += ('Saving csv must be an existing .csv or ' +
                              '.txt file.\n')
        if not pdfdirvalid:
            error_message += ('Entry of directory to save pdf, must exist.\n')

        messagebox.showerror('Entry Error', error_message)

if __name__ == '__main__':
    # Initiate initial information entry GUI application and activate pdf
    # generation from there
    root = tk.Tk()
    app = InitialInformationApp(root)
    app.parent.mainloop()
