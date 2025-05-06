import json
from pathlib import Path

import pycountry

_CRYPTO_CURRENCIES: list[dict] = [
    {"alpha_3": "BTC", "name": "Bitcoin"},
    {"alpha_3": "XMR", "name": "Monero"},
]
_iso4217_codes = json.loads((Path(pycountry.DATABASE_DIR) / "iso4217.json").read_bytes())["4217"]


for _v in _CRYPTO_CURRENCIES + _iso4217_codes:
    globals()[_v["alpha_3"]] = _v["name"]


def is_crypto(currency_code: str) -> bool:
    return bool(currency_code in [currency["alpha_3"] for currency in _CRYPTO_CURRENCIES])


# noinspection PyUnresolvedReferences
def lookup(currency: str) -> str:
    """
    Lookup for a currency code. It supports Bitcoin.
    :param currency: a currency representation
    :return: an Alpha-3 ISO-4217 upper-case code
    """
    try:
        if currency:
            currency = currency.upper()
        else:
            raise LookupError

        return currency if globals().get(currency) else None
    except LookupError:
        raise ValueError(f"'{currency}' is neither a crypto or ISO-4217 (Alpha-3) currency code.")
