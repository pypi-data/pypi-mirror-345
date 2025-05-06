from typing import Optional

from commons import currencies
from commons.media import Image


def generate(currency: str, wallet: str,
             receiver: Optional[str] = None,
             amount: Optional[float] = None,
             description: Optional[str] = None,
             color: str = "black", back_color: str = "white") -> Optional[Image]:
    def qrcode(data: str, box_size: int = 8):
        from qrcode.main import QRCode
        from qrcode.image.pure import PyPNGImage
        from qrcode.image.pil import PilImage
        from commons.media import Image, mimetypes
        from io import BytesIO

        code: QRCode = QRCode(box_size=box_size)
        buffer: BytesIO = BytesIO()
        image: PilImage | PyPNGImage

        code.add_data(data)
        code.make(fit=True)

        image = code.make_image(fill_color=color, back_color=back_color).convert("RGB")
        image.save(buffer, 'png')

        return Image(data=buffer.getvalue(), media_type=mimetypes.IMAGE_PNG)

    # ---
    currency = currencies.lookup(currency)

    if wallet:
        match currency:
            case "BTC":
                from commons.network.http import query

                params = {
                    "amount": f"{amount:.8f}" if amount else None,
                    "label": receiver if receiver else None,
                    "message": description if description else None
                }

                q = query.build(params)
                if q:
                    return qrcode(f"bitcoin:{wallet}?{q}")
                else:
                    return qrcode(f"bitcoin:{wallet}")
            case "XMR":
                from commons.network.http import query

                params = {
                    "tx_amount": f"{amount:.12f}" if amount else None,
                    "recipient_name": receiver if receiver else None,
                    "tx_description": description if description else None
                }

                q = query.build(params)
                if q:
                    return qrcode(f"monero:{wallet}?{q}")
                else:
                    return qrcode(f"monero:{wallet}")
            case "BRL":
                if receiver and wallet:
                    from commons.currencies.payments import Pix

                    params = {
                        "receiver_name": receiver,
                        "key": wallet,
                        "amount": amount if amount else 0,
                        "description": description if description else ""
                    }

                    return qrcode(data=Pix(**params).brcode(), box_size=5)
                else:
                    raise ValueError("BRL QR code via Pix requires a receiver and a wallet.")
            case _:
                return None
    else:
        raise ValueError("No wallet was provided.")
