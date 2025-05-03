import json
from datetime import datetime
from pathlib import Path
import uuid

class TransactionLog:
    def __init__(self, log_file: str = "transaction_log.json"):
        self.log_path = Path(log_file)
        self.transactions = []

        if self.log_path.exists():
            self._load()

    def _load(self):
        with self.log_path.open("r") as f:
            self.transactions = json.load(f)

    def _save(self):
        with self.log_path.open("w") as f:
            json.dump(self.transactions, f, indent=2)

    def record(self, sender: str, receiver: str, amount: int, currency: str, memo: str):
        tx = {
            "tx_id": str(uuid.uuid4()),
            "sender": sender,
            "receiver": receiver,
            "amount": amount,
            "currency": currency,
            "memo": memo,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.transactions.append(tx)
        self._save()
        return tx

    def all(self):
        return self.transactions

    def filter_by_agent(self, agent_name: str):
        return [tx for tx in self.transactions if tx["sender"] == agent_name or tx["receiver"] == agent_name]
