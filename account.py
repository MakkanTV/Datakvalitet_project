

class Account():

    def __init__(self, bank, type, nr):
        self.type = type
        self.bank = bank
        self.nr = bank.banknr + "-" + nr
        self.balance = 0
        self.credit = 0

    def get_balance(self):
        return self.balance

    def deposit(self, amount):
        self.balance += amount
        return amount

    def withdraw(self, amount):
        if(amount > self.balance):
            self.balance -= amount
            return amount
        else: return None

