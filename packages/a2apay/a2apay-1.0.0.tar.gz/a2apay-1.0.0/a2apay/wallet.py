from dataclasses import dataclass
from datetime import datetime
import uuid

@dataclass
class Transaction:
    tx_id: str
    sender: str
    receiver: str
    amount: int
    currency: str
    timestamp: str
    memo: str = ""

class Wallet:
    def __init__(self, owner: str, balance: int = 0, currency: str = "USDC"):
        self.owner = owner
        self.balance = balance
        self.currency = currency
        self.history = []

    def send(self, to_wallet, amount: int, memo: str = ""):
        if amount <= 0:
            raise ValueError("Amount must be positive.")
        if self.balance < amount:
            raise ValueError("Insufficient funds.")
        if self.currency != to_wallet.currency:
            raise ValueError("Currency mismatch.")

        self.balance -= amount
        to_wallet.receive(self, amount, memo)

        tx = Transaction(
            tx_id=str(uuid.uuid4()),
            sender=self.owner,
            receiver=to_wallet.owner,
            amount=amount,
            currency=self.currency,
            timestamp=datetime.utcnow().isoformat(),
            memo=memo
        )
        self.history.append(tx)
        to_wallet.history.append(tx)

    def receive(self, from_wallet, amount: int, memo: str = ""):
        self.balance += amount
