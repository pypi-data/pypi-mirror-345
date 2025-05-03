from a2apay.agent import Agent
from a2apay.wallet import Wallet

def test_agent_task_and_payment():
    # Set up two agents with wallets
    alice_wallet = Wallet("Alice", balance=1000, currency="RLUSD")
    bob_wallet = Wallet("Bob", balance=0, currency="RLUSD")
    alice = Agent("Alice", wallet=alice_wallet)
    bob = Agent("Bob", wallet=bob_wallet)

    # Create task and assign price
    task = {"action": "translate", "text": "Hola", "lang": "EN"}
    price = 300

    # Alice sends request to Bob and pays after result
    result = alice.request_task(bob, task, price)

    assert result["result"] == "Translated(Hola) to EN"
    assert alice.wallet.balance == 700  # 1000 - 300
    assert bob.wallet.balance == 300
    assert len(alice.wallet.history) == 1
    assert len(bob.wallet.history) == 1
