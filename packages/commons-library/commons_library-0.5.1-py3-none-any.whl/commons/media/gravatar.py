from typing import Optional

import httpx

from commons.media.images import Image


def avatar(key: str, size: int) -> Optional[Image]:
    response = httpx.get(f'https://www.gravatar.com/avatar/{key}?s={size}')

    if response and response.content:
        return Image(data=response.content).convert()
    else:
        raise ConnectionError(
            f"An error has occurred while fetching Wise API: {response.status_code} - {response.content}")
