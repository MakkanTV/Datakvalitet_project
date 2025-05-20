# has accounts
# can borrow
# can apply for an account
# can ask for credit
# can try update personal info
import account
from account import Account

class Customer:
    accounts = []

    def __init__(self, name, balance, ssn): # konstruktor
        self.name = name
        self.ssn = ssn
        self.balance = balance

    def add_account(self, bank, type):
        self.accounts.append(Account(bank, "Personal Account", self.ssn)) # New Account



