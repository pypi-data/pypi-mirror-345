from a2apay.wallet import Wallet

def test_wallet_send_receive():
    a = Wallet("A", 1000, currency="RLUSD")
    b = Wallet("B", 0, currency="RLUSD")
    a.send(b, 200, memo="test")
    assert a.balance == 800
    assert b.balance == 200
    assert len(a.history) == 1
    assert len(b.history) == 1
