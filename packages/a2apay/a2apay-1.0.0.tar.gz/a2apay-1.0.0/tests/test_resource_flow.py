from a2apay.wallet import Wallet
from a2apay.resource import ResourceProvider

def test_resource_access_payment():
    alice_wallet = Wallet("Alice", balance=1000, currency="RLUSD")
    provider_wallet = Wallet("DataBank", balance=0, currency="RLUSD")
    databank = ResourceProvider("DataBank", provider_wallet)
    databank.set_resource("file.txt", 200, "some content")

    price = databank.get_price("file.txt")
    content = databank.provide("file.txt")
    assert content == "some content"

    alice_wallet.send(databank.wallet, price, memo="Payment for file.txt")
    assert alice_wallet.balance == 800
    assert provider_wallet.balance == 200
    assert len(alice_wallet.history) == 1
    assert len(provider_wallet.history) == 1
