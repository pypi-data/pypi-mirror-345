from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, computed_field, Field


class _WiseQuote(BaseModel):
    rate: Decimal
    fee: Decimal
    dateCollected: datetime
    sourceCountry: Optional[str]
    targetCountry: Optional[str]
    markup: Decimal
    receivedAmount: Optional[Decimal]
    sendAmount: Optional[Decimal]
    isConsideredMidMarketRate: bool

    @computed_field
    @property
    def amount(self) -> Decimal:
        if self.sendAmount:
            return self.sendAmount
        elif self.receivedAmount:
            return self.receivedAmount
        else:
            return Decimal(0)


class _WiseQuotationProvider(BaseModel):
    id: int
    alias: str
    name: str
    logos: dict
    type: str
    partner: bool
    quotes: list[_WiseQuote]


class _WiseQuotationResponse(BaseModel):
    sourceCurrency: str
    targetCurrency: str
    sourceCountry: Optional[str] = None
    targetCountry: Optional[str] = None
    providerCountry: Optional[str] = None
    providerTypes: list[str]
    amount: Decimal
    amountType: str
    providers: list[_WiseQuotationProvider]

    @computed_field
    @property
    def quotation(self) -> _WiseQuote:
        provider: Optional[_WiseQuotationProvider] = None
        quote: Optional[_WiseQuote] = None

        if self.providers:
            for provider in self.providers:
                if provider.alias == "wise":
                    break

        if provider and len(provider.quotes) >= 1:
            quote = provider.quotes[0]

        return quote


class CurrencyQuote(BaseModel):
    source_currency: str
    target_currency: str
    date: datetime
    rate: Decimal


class TransferQuote(BaseModel):
    provider: str = "wise"
    quote: CurrencyQuote
    sourceCountry: Optional[str]
    targetCountry: Optional[str]
    date: datetime = Field(validation_alias="dateCollected")
    amount: Decimal
    fee: Decimal

    @computed_field
    @property
    def no_fee_amount(self) -> Decimal:
        return self.amount - self.fee
