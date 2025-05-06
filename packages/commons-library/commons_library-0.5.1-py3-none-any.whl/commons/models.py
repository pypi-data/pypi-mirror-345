from pathlib import Path
from typing import Optional

import httpx
from pydantic import computed_field, ConfigDict
from sqlmodel import SQLModel, Field


# noinspection PyNestedDecorators
class Resource(SQLModel):
    """
    Represents and loads a resource.
    Be aware that might be unsafe to read remote content that you might not trust.
    """
    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )

    location: str = Field(primary_key=True, nullable=False, default="memory://")
    data: Optional[bytes] = Field(nullable=True, default=None)

    @computed_field
    @property
    def url(self) -> httpx.URL:
        return httpx.URL(self.location)

    @computed_field
    @property
    def path(self) -> Path:
        return Path(self.location)

    def is_remote(self) -> bool:
        """
        Check whether a location is remote or local
        """
        return self.url.is_absolute_url

    def is_local(self) -> bool:
        """
        Check whether a location is local or remote
        """
        return self.url.is_relative_url

    def exists(self) -> bool:
        """Check if the resource exists"""
        if self.is_local():
            return self.path.exists()
        elif self.is_remote():
            return bool(self.read())
        else:
            return bool(self._data)

    def read(self) -> Optional[bytes]:
        """Read a resource, either locally or remotely (via HTTP)."""
        if not self.data:
            try:
                if self.is_remote():
                    response = httpx.get(self.url, headers={"Accept-Encoding": "utf-8"})

                    if response and response.status_code == 200:
                        self.data = response.read()
                elif self.exists():
                    self.data = self.path.read_bytes()
            except FileNotFoundError:
                ...

        return self.data

    def scheme(self) -> str:
        return self.url.scheme

    def filename(self) -> Optional[str]:
        return self.path.name if self.path else None
