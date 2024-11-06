import logging
import json
import dataclasses
import random
import time
from multiprocessing import Pool

def check_positive(func):
    def wrapper(*args, **kwargs):
        for i in args:
            if isinstance(i, (int, float)) and i < 0:
                raise ValueError(f"Please enter positive values")
        return func(*args, **kwargs)
    return wrapper

@dataclasses.dataclass()
class Client:
    name: str
    balance: dict[str, float]

class FileNotFoundError(Exception):
    "Raised when can't find file"
    pass

class ExchageNoRatioError(Exception):
    "Raised when can't find specific exchange rate"
    pass

class InsufficientFundsOrNoCurrencyError(Exception):
    "Raised when client does not have specific currency in his wallet or has no funds"
    pass

class Bank:
    exchange_rates = {
        ("euro", "zloty"): 4.34,
        ("zloty", "euro"): 1/4.33,
        ("dolar", "zloty"):3.98,
        ("zloty", "dolar"): 1/3.98,
        ("pound", "zloty"): 5.18,
        ("zloty", "pound"): 1/5.18,
                    }
    money_in_bank = {"euro": 0, "pound": 0, "zloty": 0, "lira": 0, "dolar": 0, "forint": 0}
    
    def __init__(self):
        self.database=[]

    def append_client(self, client: Client):
        if any(currency in self.money_in_bank for currency in client.balance.keys()):
            self.database.append(client)
        else:
            logging.info(f"We do not support the currency. Can't append {client.name} with {client.balance}.")
    
    def save_clients(self, filename="clients.json"):
        with open(filename, "w") as file:
            data = [{"name": client.name, "balance": client.balance} for client in self.database]
            json.dump(data, file)
    
    def load_clients(self, filename="clients.json"):
        try:
            with open(filename, "r",  encoding="utf-8") as file:
                clients_data = json.load(file)
                for data in clients_data:
                    client = Client(data["name"], data["balance"])
                    self.append_client(client)
                logging.info("Clients loaded!")
        except FileNotFoundError:
            logging.info("Clients file not found. No clients loaded.")
    
    @classmethod
    def money_count(cls):
        cls.money_in_bank = {currency: 0 for currency in cls.money_in_bank.keys()}
        for client in bank.database:           
            for currency, amount in client.balance.items():
                if currency in cls.money_in_bank:
                    cls.money_in_bank[currency] += amount
        logging.info("Total money in bank:")
        for currency, amount in cls.money_in_bank.items():
            if amount > 0:
                logging.info(f"{currency}: {amount:.2f}")
    
    @staticmethod
    def exchange_calculator(amount: float | int, from_this: str, to_this: str):
        try: 
            if (from_this,  to_this) in Bank.exchange_rates:
                rate = Bank.exchange_rates[(from_this,  to_this)]
                return amount * rate
            else:
                raise ExchageNoRatioError
        except ExchageNoRatioError:
            logging.info(f"Exchange from {from_this} to {to_this} is not available.")
    
    @check_positive
    def exchange(self, client: Client, amount: float | int, from_this: str, to_this: str):
        try:
            start_time = time.time()
            transaction_delay = max(random.gauss(3, 2),0)
            if from_this in client.balance and client.balance[from_this] >= amount:
                converted_amount = self.exchange_calculator(amount, from_this, to_this)
                if converted_amount is not None:
                    client.balance[from_this] -= amount
                    if to_this not in client.balance:
                        client.balance[to_this] = 0
                    client.balance[to_this] += converted_amount
                    time.sleep(transaction_delay)
                    transaction_time = round((time.time() - start_time),2)
                    logging.info(f"{client.name} Exchanged {amount} {from_this} to {converted_amount:.2f} {to_this}. Transaction took {transaction_time} s")
            else:
                raise InsufficientFundsOrNoCurrencyError
        except InsufficientFundsOrNoCurrencyError:
            logging.info(f"Insufficient funds or currency not available in client balance.")

#def multi_exchange(bank, client, amount, from_this, to_this = args):
    #bank.exchange(client, amount, from_this, to_this)

if __name__ == "__main__":
    logging.basicConfig(format="{message}",
                    style="{",
                    level=logging.INFO,
                    force=True)
    logger = logging.getLogger()
    client1 = Client("Jan Nowak", {"euro": 100})
    client2 = Client("Zbigniew Kropka", {"zloty": 150})
    client3 = Client("Daniel Krabus", {"hrywna": 150})
    client4 = Client("Jan Wan", {"euro": 15})
    bank = Bank()
    bank.append_client(client1)
    bank.append_client(client2)
    bank.append_client(client3)
    bank.append_client(client4)
    bank.money_count()
    bank.exchange(client1, 10, "euro", "zloty")
    #bank.exchange(client4, -10, "euro", "zloty")
    bank.exchange(client4, 10, "euro", "forint")
    bank.exchange(client4, 100, "euro", "forint")
    bank.exchange(client2, 50, "zloty", "pound")
    bank.money_count()
    print(client2.balance)
    bank.save_clients("clients.txt")
    bank.load_clients("read.txt")
    #multi_tasks = [
            #(bank, client1, 90, "euro", "dolar"),
            #(bank, client2, 50, "zloty", "pound"),
            #(bank, client4, 1, "euro", "zloty"),
    #]
    #with Pool() as pool:
        #pool.map(multi_exchange, multi_tasks)





