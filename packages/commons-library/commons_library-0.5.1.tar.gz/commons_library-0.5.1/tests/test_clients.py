import unittest

from commons.media import Image


class TestHTTPClients(unittest.TestCase):
    def test_currency_client(self):
        from commons import currencies

        assert currencies.get_quote(from_currency="BRL", to_currency="EUR")
        assert currencies.get_quote(from_currency="BTC", to_currency="BRL")
        assert currencies.get_quote(from_currency="XMR", to_currency="EUR")

    def test_gravatar_client(self):
        from commons.media import gravatar

        image: Image = gravatar.avatar("e5f43fe12e80783bd2666c529fbf33d0", size=120)
        assert image and image.read()

    def test_giphy_client(self):
        from commons.media import giphy

        image: Image = giphy.gif("l4HogOSqU3uupmvmg")
        assert image and image.read()
