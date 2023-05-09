
from datetime import datetime, date
import pandas as pd
import datetime as dt
from datetime import datetime, timedelta
import traceback
from collections import defaultdict


def read():
    file = r"C:\Users\rcxsm\Documents\xls\masterfinance_2023_dummy.xlsm"
    file = r"C:\Users\rcxsm\Documents\python_scripts\python_scripts_rcsmit\input\masterfinance_2023_dummy.xlsm"
    try:
        df = pd.read_excel (file,
                            sheet_name= "INVOER",
                            header=0,
                            usecols= "a,b,c,d,e,f,g,h",
                            
                            names=["id","source","datum","bedrag","description","income_expenses","main_category","category"],)
        
        df.datum=pd.to_datetime(df.datum,errors='coerce', dayfirst=True)
        
    except Exception as e:
        print("error met laden")
        print(f"{e}")
        print(traceback.format_exc())
        


    df['jaar']=df['datum'].dt.strftime('%Y')
    df['maand']=df['datum'].dt.strftime('%m')
    df['invbedrag']= df['bedrag']* -1
    df['maand_']=df['datum'].dt.strftime('%Y-%m')
    return df

class Account:
    def __init__(self, name):
        self.name = name
        self.balance = 0
        self.transactions = []

    def debit(self, amount):
        self.balance += amount

    def credit(self, amount):
        self.balance -= amount

    def add_transaction(self, transaction):
        self.transactions.append(transaction)

    def __str__(self):
        return f"{self.name} - Balance: {round(self.balance,2)}"


class Transaction:
    def __init__(self, date, debit_account, credit_account, amount, description):
        self.date = date
        self.debit_account = debit_account
        self.credit_account = credit_account
        self.amount = amount
        self.description = description

class Ledger:
    def __init__(self):
        self.accounts = []
        self.transactions = []
    
    def add_account(self, account):
        self.accounts.append(account)
    
    def add_transaction(self, date, debit_account_name, credit_account_name, amount, description):
        debit_account = next((a for a in self.accounts if a.name == debit_account_name), None)
        credit_account = next((a for a in self.accounts if a.name == credit_account_name), None)
        if not debit_account or not credit_account:
            raise ValueError(f"Invalid account name {debit_account_name}, {credit_account_name}")
        transaction = Transaction(date, debit_account, credit_account, amount, description)
        debit_account.debit(amount)
        credit_account.credit(amount)
        debit_account.add_transaction(transaction)
        credit_account.add_transaction(transaction)
        self.transactions.append(transaction)
        
    def print_trial_balance(self):
        total_debits = 0
        total_credits = 0
        for account in self.accounts:
            total_debits += sum(t.amount for t in account.transactions if t.debit_account == account)
            total_credits += sum(t.amount for t in account.transactions if t.credit_account == account)
            print(account)
        print(f"Total Debits: {total_debits}")
        print(f"Total Credits: {total_credits}")

    def ask_trial_balance_date(self, asked_acount, date_given):
        total_debits = 0
        total_credits = 0
        to_return = 0

        # suggestion of Chat-GPT
        # relevant_transactions = [t for t in account.transactions if t.date <= date_given]
        
        for account in self.accounts:
            d = (sum(t.amount for t in account.transactions if t.debit_account == account and t.date <=date_given))
            c = (sum(t.amount for t in account.transactions if t.credit_account == account and t.date <=date_given))
            total_debits += d
            total_credits += c
            if account.name == asked_acount:
                to_return = d+c
            # print (f"{account.name} - {d} {c}")
            #print(account)
        # print(f"Total Debits: {total_debits}")
        # print(f"Total Credits: {total_credits}")
        return to_return


def get_monthly_totals(ledger):
    monthly_totals = defaultdict(lambda: defaultdict(float))
    for transaction in ledger.transactions:
        year, month, day = transaction.date.year, transaction.date.month, transaction.date.day
        account_name = transaction.credit_account.name if transaction.credit_account.name != "None" else transaction.debit_account.name
        monthly_totals[account_name][f"{year}-{month:02d}"] += transaction.amount
    print  ("monthly_totals")
    print  (monthly_totals)
    
    return monthly_totals



def get_monthly_pivot_table(ledger):
    monthly_totals = get_monthly_totals(ledger)
    df = pd.DataFrame(monthly_totals)
    df = df.fillna(0)  # replace NaN values with 0
    df = df.sort_index()  # sort rows alphabetically by account name
    df.columns.name = "Month"
    df = df.apply(lambda x: round(x, 2))  # round values to 2 decimal places
   
    return df.T


def print_pivot_monthlty_trial_balance(ledger, accounts_source):
    # Define the start and end year
    start_year = 2023
    end_year = 2023

    # Initialize an empty DataFrame to store the trial balances
    trial_balance_df = pd.DataFrame(columns=['Date', 'Account', 'Balance'])

    # Loop through each year and month and retrieve the trial balance for each account on the first day of the month
    for year in range(start_year, end_year + 1):
        for month in range(1, 6):
            # Extract the first day of the month
            my_date = date(year, month, 1)
            # Loop through each account and retrieve the trial balance on the first day of the month
            for a in accounts_source:
                balance = ledger.ask_trial_balance_date(a, my_date)
                # Append the trial balance to the DataFrame
                #trial_balance_df = trial_balance_df.append({'Date': my_date, 'Account': a, 'Balance': balance}, ignore_index=True)
                trial_balance_df = pd.concat([trial_balance_df, pd.DataFrame({'Date': [my_date], 'Account': [a], 'Balance': [balance]})], ignore_index=True)

    # Create the pivot table
    pivot_table = pd.pivot_table(trial_balance_df, values='Balance', index=['Account'], columns=['Date'])

    # Print the pivot table
    print(pivot_table)


def main():
    df = (read())
    
    ledger = Ledger()
    modus = "main_category"
    modus = "income_expenses"
    # create some accounts

    accounts = pd.concat([df['source'], df[modus]]).unique().tolist()
    accounts_source = (df['source']).unique().tolist()

    
    for a in accounts:
        a_ = Account(a)
        # add accounts to the ledger
        ledger.add_account(a_)

   
    for index, row in df.iterrows():
        ledger.add_transaction(
            row["datum"].date(),
            row["source"],
            row[modus],
            row["bedrag"],
            row["description"]
        )

   

    monthly_pivot_table = get_monthly_pivot_table(ledger)
    print("monthly_pivot_table")

    print(monthly_pivot_table)

    # print trial balance
    print("ledger.print_trial_balance()")
    ledger.print_trial_balance()

    # print trial balance on a certain date
    print()
    print("print trial balance on a certain date")
    
    print_pivot_monthlty_trial_balance(ledger, accounts_source)

main()
