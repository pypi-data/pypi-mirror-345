"""
Implements a client that fetches currency data from Wise and Coinbase.
Documentation: https://docs.wise.com/api-docs/api-reference/comparison
"""

import json
from datetime import datetime
from decimal import Decimal
from logging import getLogger, Logger
from typing import Optional

import httpx

from commons.currencies._models import _WiseQuotationResponse, CurrencyQuote, TransferQuote
from commons.currencies import codes as currencies
from commons.media import Image
from commons.network.http import query

logger: Logger = getLogger(__file__)


# noinspection PyUnresolvedReferences
def get_transfer_quote(from_currency: str, to_currency: str,
                       send_amount: Optional[Decimal] = None,
                       recipient_gets_amount: Optional[Decimal] = None,
                       source_country: Optional[str] = None, target_country: Optional[str] = None,
                       decimal_precision: int = 2) -> TransferQuote:
    """
    Get a transfer quotation between two currencies. Either `send_amount` or `recipient_gets_amount` should be specified.
    It does not support cryptocurrencies.

    :param from_currency: ISO-4217 currency as string
    :param to_currency: ISO-4217 currency as string
    :param send_amount: [Optional] Amount to send
    :param recipient_gets_amount: [Optional] Amount to receive
    :param source_country: [Optional] ISO-3166-1 Alpha-2 country code as string
    :param target_country: [Optional] ISO-3166-1 Alpha-2 country code as string
    :param decimal_precision: [Optional] Precision used on amount conversion. Default is 2.
    """
    # --- Build parameters
    params: dict = {
        "sourceCurrency": currencies.lookup(from_currency),
        "targetCurrency": currencies.lookup(to_currency)
    }

    if send_amount:
        params["sendAmount"] = f"{send_amount:.{decimal_precision}f}"
    elif recipient_gets_amount:
        params["recipientGetsAmount"] = f"{recipient_gets_amount:.{decimal_precision}f}"
    else:
        raise ValueError("Either `send_amount` or `recipient_gets_amount` must be specified.")

    if source_country:
        params["sourceCountry"] = countries.lookup(source_country).alpha_2
    if target_country:
        params["targetCountry"] = countries.lookup(target_country).alpha_2

    # --- Request data
    response = httpx.get(f"https://api.wise.com/v4/comparisons/?{query.build(params)}")
    if response and response.status_code == 200:
        # build response
        wise_response: _WiseQuotationResponse = _WiseQuotationResponse(**json.loads(response.content.decode()))
        quote: CurrencyQuote = CurrencyQuote(
            **{"source_currency": wise_response.sourceCurrency,
               "target_currency": wise_response.targetCurrency,
               "date": wise_response.quotation.dateCollected,
               "rate": wise_response.quotation.rate}
        )
        transfer_quote: TransferQuote = TransferQuote(**({"quote": quote} | wise_response.quotation.model_dump()))

        return transfer_quote
    else:
        raise ConnectionError(f"An error has occurred while fetching Wise API: {response.status_code} - {response.content}")


def _get_iso4217_quote(from_currency: str, to_currency: str) -> CurrencyQuote:
    return get_transfer_quote(from_currency, to_currency, recipient_gets_amount=Decimal(1)).quote


def _get_crypto_quote(from_currency: str, to_currency: str) -> CurrencyQuote:
    # docs: https://developers.coindesk.com/documentation/legacy/Price/SingleSymbolPriceEndpoint/
    response = httpx.get(f"https://min-api.cryptocompare.com/data/price?fsym={from_currency}&tsyms={to_currency}")
    if response and response.status_code == 200:
        return CurrencyQuote(
            **{"source_currency": from_currency,
               "target_currency": to_currency,
               "date": datetime.now(),
               "rate": json.loads(response.content.decode())[to_currency]
               }
        )
    else:
        raise ConnectionError(
            f"An error has occurred while fetching CryptoCompare API: {response.status_code} - {response.content}")


def get_quote(from_currency: str, to_currency: str) -> CurrencyQuote:
    """
    Get currency rate between two currencies. It supports BTC and XMR among other currencies.

    :param from_currency: ISO-4217 currency as string or cryptocurrency representation
    :param to_currency: ISO-4217 currency as string or cryptocurrency representation
    """
    from_currency = currencies.lookup(from_currency)
    to_currency = currencies.lookup(to_currency)

    if currencies.is_crypto(from_currency) or currencies.is_crypto(to_currency):
        return _get_crypto_quote(from_currency, to_currency)
    else:
        return _get_iso4217_quote(from_currency, to_currency)
