from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class TaskRequest:
    sender: str
    receiver: str
    task_type: str
    payload: dict
    price: int
    timestamp: str = datetime.utcnow().isoformat()

@dataclass
class TaskResult:
    sender: str
    receiver: str
    result_data: dict
    success: bool
    timestamp: str = datetime.utcnow().isoformat()
    error_message: Optional[str] = None

@dataclass
class PaymentNotice:
    sender: str
    receiver: str
    amount: int
    currency: str
    tx_id: str
    memo: Optional[str] = ""
    timestamp: str = datetime.utcnow().isoformat()
