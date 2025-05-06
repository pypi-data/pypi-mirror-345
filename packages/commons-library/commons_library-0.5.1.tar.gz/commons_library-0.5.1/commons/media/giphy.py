from typing import Optional

import httpx

from commons.media import Image


def gif(key: str) -> Optional[Image]:
    response = httpx.get(f"https://media.giphy.com/media/{key}/giphy.gif")

    if response and response.content:
        return Image(data=response.content, media_type=response.headers['Content-Type'])
    else:
        raise ConnectionError(
            f"An error has occurred while fetching Wise API: {response.status_code} - {response.content}")
