from datetime import datetime, timedelta
from typing import Optional

from pydantic import computed_field
from sqlalchemy import inspect
from sqlmodel import SQLModel, Field, Session, select

from commons.database import DatabaseAdapter


class CacheEntry(SQLModel, table=True):
    __tablename__ = "cache"
    id: str = Field(nullable=False, primary_key=True)
    data: bytes | None = Field(nullable=True)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    max_age: int = Field(default=300, nullable=False)

    @computed_field
    @property
    def expires(self) -> datetime:
        return self.created_at + timedelta(seconds=self.max_age)

    @computed_field
    @property
    def expired(self) -> bool:
        return bool(datetime.now() >= self.expires)


class Cache:
    database: DatabaseAdapter
    session: Optional[Session] = None

    def __init__(self, database: DatabaseAdapter = DatabaseAdapter()):
        self.database = database

        if not inspect(database.engine()).has_table("cache"):
            SQLModel.metadata.tables["cache"].create(database.engine())

    def get(self, key: str) -> CacheEntry | None:
        return self.session.exec(select(CacheEntry).where(CacheEntry.id == key)).first()

    def set(self, key: str, value: bytes, max_age: int = 300) -> CacheEntry:
        entry = CacheEntry(id=key, data=value, max_age=max_age)

        self.invalidate(key)
        self.session.add(entry)
        self.session.commit()

        return entry

    def invalidate(self, key: str):
        entry = self.get(key)
        if entry:
            self.session.delete(entry)

    def __enter__(self):
        self.session = self.database.session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
        self.session = None
