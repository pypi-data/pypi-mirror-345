from typing import Optional

from pydantic import BaseModel, field_validator

from commons.media import Image, mimetypes

"""
Module adapted from PyPix package by Artemis Resende.

Source: https://github.com/cleitonleonel/pypix/
License: MIT License

Copyright (c) 2022 Cleiton Leonel Creton

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# noinspection PyNestedDecorators
class Pix(BaseModel):
    """
    Model for Brazilian Payment System PIX.
    """
    single_transaction: bool = False
    key: str
    receiver_name: str
    receiver_city: str = ""
    amount: float = 0.0
    receiver_zipcode: Optional[str] = None
    identification: Optional[str] = None
    description: Optional[str] = None
    default_url_pix: Optional[str] = None

    @classmethod
    def _cpf_key(cls, source: str) -> Optional[str]:
        is_valid: bool = True
        numbers = [int(char) for char in source if char.isdigit()]

        if (len(numbers) != 11) or (numbers == numbers[::-1]):
            is_valid = False

        try:
            for i in range(9, 11):
                value = sum((numbers[num] * ((i + 1) - num) for num in range(0, i)))
                digit = ((value * 10) % 11) % 10
                if digit != numbers[i]:
                    is_valid = False
        except (IndexError, Exception):
            is_valid = False

        return source if is_valid else None

    @classmethod
    def _phone_key(cls, source: Optional[str]) -> Optional[str]:
        import re

        rule = re.compile(r'^\+?[1-9]\d{1,14}$')

        if rule.match(source):
            if source.startswith("+55"):
                return source
            else:
                return f"+55{source}"
        else:
            return None

    @field_validator("key", mode="before")
    @classmethod
    def key_validator(cls, value: str) -> str:
        key = cls._cpf_key(value)  # check if it is a CPF

        if not key:
            key = cls._phone_key(value)  # check if it is a brazilian phone number

        if not key:
            # todo: add validation for random and e-mail keys
            key = value

        return key

    @field_validator("default_url_pix", mode="before")
    @classmethod
    def validate_default_url_pix(cls, value: Optional[str]) -> Optional[str]:
        return value.replace('https://', '') if value else None

    @field_validator("receiver_name", mode="before")
    @classmethod
    def validate_receiver_name(cls, value: Optional[str]) -> Optional[str]:
        if len(value) > 25:
            raise ValueError('The maximum number of characters for the receiver name is 25.')
        return value

    @field_validator("receiver_city", mode="before")
    @classmethod
    def validate_receiver_city(cls, value: Optional[str]) -> Optional[str]:
        if len(value) > 15:
            raise ValueError('The maximum number of characters for the receiver city is 15.')
        return value

    @field_validator("amount", mode="before")
    @classmethod
    def validate_amount(cls, value: float) -> float:
        if len(str("{0:.2f}".format(value))) > 13:
            raise ValueError('The maximum number of characters for the amount value is 13.')
        return float("{0:.2f}".format(value))

    def brcode(self):
        """
        Generate a BR code [1].

        [1]: The BR Code is the name of the QR Code standard, for the purpose of initiating payments, adopted in Brazil,
         in accordance with Circular No. 3,682, dated November 4, 2013.

        Source: https://www.bcb.gov.br/content/estabilidadefinanceira/spb_docs/ManualBRCode.pdf

        :return: BR Code data as string.
        """
        def encode_value(identifier: str, value: str) -> str:
            return f"{identifier}{str(len(value)).zfill(2)}{value}"

        def format_text(value: str) -> str:
            from unicodedata import normalize
            import re
            if value:
                return re.sub(
                    r'[^A-Za-z0-9$@%*+\-./:_ ]', '',
                    normalize('NFD', value).encode('ascii', 'ignore').decode('ascii')
                )
            else:
                return ""

        def encode_info():
            base_pix = encode_value('00', 'br.gov.bcb.pix')
            info_string = ''

            if self.key:
                info_string += encode_value('01', self.key)
            elif self.default_url_pix:
                info_string += encode_value('25', self.default_url_pix)
            else:
                raise ValueError('You must enter a URL or a Pix key to generate a valid BR Code.')

            if self.description:
                info_string += encode_value('02', format_text(self.description))

            return encode_value('26', f'{base_pix}{info_string}')

        def encode_additional_data():
            if self.identification:
                return encode_value('62', encode_value('05', format_text(self.identification)))
            return encode_value('62', encode_value('05', '***'))

        def compute_crc(hex_code: str) -> str:
            from binascii import crc_hqx
            msg = bytes(hex_code, "utf-8")
            crc = crc_hqx(msg, 0xffff)
            return "{:04X}".format(crc & 0xffff)

        result_string = (
            f"{encode_value("00", "01")}"
            f"{encode_value("01", "12" if self.single_transaction else "11")}"
            f"{encode_info()}"
            f"{encode_value("52", "0000")}"
            f"{encode_value("53", "986")}"
            f"{encode_value("54", str(self.amount))}"
            f"{encode_value("58", "BR")}"
            f"{encode_value("59", format_text(self.receiver_name))}"
            f"{encode_value("60", format_text(self.receiver_city))}"
            f"{encode_value("61", format_text(self.receiver_zipcode))}"
            f"{encode_additional_data()}"
            f"6304"
        )
        return result_string + compute_crc(result_string)

    def qrcode(self, color: str = "black", back_color: str = "white",
               amount: Optional[float] = None,
               description: Optional[str] = None) -> Image:
        from commons.currencies.payments import qrcode
        return qrcode.generate(currency="BRL", wallet=self.key, receiver=self.receiver_name, amount=amount,
                        description=description, color=color, back_color=back_color)
