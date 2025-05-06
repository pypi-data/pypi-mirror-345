import unittest

import commons.currencies.payments.qrcode
from commons import currencies


class TestCurrencies(unittest.TestCase):
    def test_currency_client(self):
        assert currencies.lookup("brl") == "BRL"
        assert currencies.lookup("eur") == "EUR"
        assert currencies.lookup("btc") == "BTC"
        assert currencies.lookup("xmr") == "XMR"
        self.assertRaises(ValueError, currencies.lookup, currency="")

    def test_qrcode_gen(self):
        assert commons.currencies.payments.qrcode.generate(currency="brl", wallet="pix@email.com", receiver="Maria Joana")
        assert commons.currencies.payments.qrcode.generate(currency="brl", wallet="pix@email.com", receiver="Maria Joana", amount=100, description="pagamento")
        assert commons.currencies.payments.qrcode.generate(currency="btc", wallet="samplekey")
        assert commons.currencies.payments.qrcode.generate(currency="btc", wallet="samplekey", receiver="Maria Joana", amount=100, description="pagamento")
        assert commons.currencies.payments.qrcode.generate(currency="xmr", wallet="samplekey")
        assert commons.currencies.payments.qrcode.generate(currency="xmr", wallet="samplekey", receiver="Maria Joana", amount=100, description="pagamento")
        self.assertRaises(ValueError, commons.currencies.payments.qrcode.generate, currency="BRL", wallet="pix@email.com")
        self.assertRaises(ValueError, commons.currencies.payments.qrcode.generate, currency="BRL", wallet="")
