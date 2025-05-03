from a2apay.wallet import Wallet
from a2apay.transaction import TransactionLog

def test_transaction_log_record():
    log = TransactionLog(log_file="test_transaction_log.json")
    log.transactions = []  # Reset in-memory log for test

    # Create dummy transaction
    tx = log.record(
        sender="AgentA",
        receiver="AgentB",
        amount=150,
        currency="USDC",
        memo="test transaction"
    )

    assert tx["sender"] == "AgentA"
    assert tx["receiver"] == "AgentB"
    assert tx["amount"] == 150
    assert tx["currency"] == "USDC"
    assert "tx_id" in tx
    assert "timestamp" in tx

    # Validate log contains the new transaction
    all_txs = log.all()
    assert len(all_txs) == 1
    assert all_txs[0]["tx_id"] == tx["tx_id"]
