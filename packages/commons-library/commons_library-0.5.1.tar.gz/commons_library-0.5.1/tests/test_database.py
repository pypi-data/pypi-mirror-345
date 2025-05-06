import tempfile
import unittest
from pathlib import Path
from time import sleep

from sqlmodel import SQLModel, select

from commons.database import FileDatabaseMigrationExecutor, Cache, DatabaseAdapter

RESOURCES_FOLDER: Path = Path(__file__).parent / "resources"


class TestDatabase(unittest.TestCase):
    def test_database_creation(self):
        self.assertIsNotNone(Cache().database)
        self.assertIsNotNone(Cache().database.engine())

        with Cache().database.session() as session:
            self.assertIsNotNone(session)
            session.close()

    def test_migration_files(self):
        from tests import TestUser
        from commons.database import FileMigration

        db: DatabaseAdapter = DatabaseAdapter()
        db.create_tables([TestUser, FileMigration])
        with db.session() as session:
            self.assertIsNotNone(FileDatabaseMigrationExecutor(path=RESOURCES_FOLDER / "migrations", session=session).run())
            self.assertIsNotNone(session.exec(select(TestUser).where(TestUser.username == "john.doe")).first())
            self.assertIsNotNone(session.exec(select(TestUser).where(TestUser.username == "joana.doe")).first())
            session.close()

    def test_cache(self):
        with Cache() as cache:
            key = "key"
            value = b"value"
            entry = cache.set(key, value, max_age=1)

            self.assertIsNotNone(entry)
            self.assertFalse(entry.expired)
            self.assertEqual(b"value", cache.get(key).data)

            sleep(1)

            self.assertTrue(entry.expired)
            cache.invalidate(key)
            self.assertIsNone(cache.get(key))

    def test_async_db(self):
        import asyncio
        async def _inner_func():
            return DatabaseAdapter().engine()

        self.assertEqual(str(DatabaseAdapter().engine()), str(asyncio.run(_inner_func())))

