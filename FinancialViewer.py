import numpy as np
import matplotlib.pyplot as plt
from bokeh.palettes import Category20_20
import datetime

__author__: 'Brandon Dos Remedios | git: @bdosremedios'

class BankingHistory():

    def __init__(self, initial_chequing, initial_saving, chequing_csv,
                 saving_csv):

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

        # Collapse all dates and changes to a total account change on each date
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
                self.initial_cheq_balance, cheq_daily_changes)
        save_daily_balances = self.convert_changes_to_balances(
                self.initial_save_balance, save_daily_changes)

        # Define object attributes for chequing account info
        self.cheq_days = cheq_fill_days
        self.cheq_daily_changes = cheq_fill_daily_changes
        self.cheq_daily_balances = cheq_daily_balances

        # Define object attributes for saving account info
        self.save_days = save_fill_days
        self.save_daily_changes = save_fill_daily_changes
        self.save_daily_balances = save_daily_balances

        # Aggregate chequing and saving information into total banking info
        bank_days = self.cheq_days + self.save_days
        bank_changes = self.cheq_daily_changes + self.save_daily_changes

        # Collapse all dates and changes to a total account change on each date
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

    def extract_datetime_accountchange(self, csv_rows):
        # Extract dates and account changes into two seperate lists
        dates_list = []
        changes_list = []
        for date_string, account_change, dump1, dump2, dump3 in csv_rows:
            # Split string into datetime
            month, day, year = date_string.split('/')
            extracted_date = datetime.datetime(
                int(year), int(month), int(day))
            dates_list.append(extracted_date)
            changes_list.append(round(float(account_change), 2))
        return(dates_list, changes_list)

    def collapse_date_change(self, list_of_dates, list_of_changes):
        """
        Take a list of dates and account changes on that date, and collapse
        them into a list of unique dates, and the total account change on
        each unique date.

        Parameters
        ---
        list_of_dates : list
            List of datetime.datetime objects representing the date of each
            account change in list_of_changes.
        
        list_of_changes : list
            List of floats representing change in account balance on each day.

        Returns
        ---
        collapsed_dates: list
            List of datetime.datetime objects representing unique dates in
            list_of_dates. Sorted in increasing time order.

        collapsed_changes: list
            List of floats of total account changes on dates.

        """
        # Get individual dates and sort
        unique_dates = list(set(list_of_dates))
        sorted_unique_dates = list(np.flipud(np.sort(unique_dates)))
        zipped_date_change = list(zip(list_of_dates, list_of_changes))
    
        collapsed_dates = []
        collapsed_changes = []
        for date_temp in sorted_unique_dates:
            change_on_date = [
                tup[1] for tup in zipped_date_change if tup[0] == date_temp]
            collapsed_dates.append(date_temp)
            collapsed_changes.append(round(sum(change_on_date), 2))

        return(collapsed_dates, collapsed_changes)

    def fill_no_transact_days(self, list_of_dates, list_of_changes):
        """
        Fills in days with no transactions to make plotting more consistent.

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
        """
        Converts list of floats representing account changes, into the amount
        in the account at the time.
    
        """
        cumulative_sum_changes = np.cumsum(list_of_changes)
        balances_from_changes = initial_balance + cumulative_sum_changes

        # Round each days balance to 2 decimal places
        rounded_balances = [
            round(balance, 2) for balance in balances_from_changes
            ]
    
        return(rounded_balances)

if __name__ == '__main__':
    # Initial balance at first date in transaction history
    initial_chequing = 0
    initial_saving = 0
    
    # Extract dates, changes across dates, and balances across dates
    banking_hist = BankingHistory(initial_chequing, initial_saving,
                                  'cheq csv',
                                  'save csv)
    
    print(banking_hist.cheq_days[-1],
          banking_hist.cheq_daily_changes[-1],
          banking_hist.cheq_daily_balances[-1])
    
    print(banking_hist.save_days[-1],
          banking_hist.save_daily_changes[-1],
          banking_hist.save_daily_balances[-1])
    
    print(banking_hist.bank_days[-1],
          banking_hist.bank_daily_changes[-1],
          banking_hist.bank_daily_balances[-1])

