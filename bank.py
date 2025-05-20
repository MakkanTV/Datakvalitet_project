# has accounts
# has customers
# can lend(from its own accounts)
# can transfer (to/from other banks)
import customer



class Bank:
    customer = []
    accounts = []

    def __init__(self, name, banknr):
        self.name = name
        self.banknr = banknr

    def add_customer(self, customer):
        customer(self, "personal_account")
        self.customer.append(customer)
        self.accounts.append(customer.accounts[0])




