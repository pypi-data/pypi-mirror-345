import json
from datetime import datetime
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.exc import DatabaseError
from sqlmodel import SQLModel, Field, Session, select
from commons import runtime

class FileMigration(SQLModel, table=True):
    filename: str = Field(default=None, primary_key=True, nullable=False)
    executed_at: datetime = Field(default=datetime.now(), nullable=False)


class FileDatabaseMigrationExecutor:
    def __init__(self, session: Session, path: Path | str):
        self.session: Session = session
        self.path: Path = Path(path)

    def run(self) -> list[FileMigration]:
        pending_migrations_stack: list[Path] = [Path(file) for file in self.path.glob("*.sql")]
        pending_migrations_stack += [Path(file) for file in self.path.glob("*.json")]
        pending_migrations_stack.sort()  # guarantee the execution order of the sql files based in their filenames

        migrations: list[FileMigration] = [self._execute(migration_file) for migration_file in pending_migrations_stack]
        self.session.close()

        return migrations

    def _execute(self, file: Path) -> FileMigration | None:
        migration: FileMigration | None = None

        if not self._get_last_execution_of(file):
            try:
                if file.name.endswith(".json"):
                    self._migrate_json_data_from(file)
                elif file.name.endswith(".sql"):
                    self._migrate_sql_data_from(file)
                else:
                    pass

                migration = FileMigration(filename=file.name)
                self.session.add(migration)
                self.session.commit()
            except (json.JSONDecodeError, DatabaseError, RuntimeError, Exception) as e:
                self.session.rollback()
                raise RuntimeError(f"Error executing migration {file}: {str(e)}")

    def _get_last_execution_of(self, file: Path) -> FileMigration | None:
        return self.session.exec(select(FileMigration).where(FileMigration.filename == file.name)).first()

    def _migrate_sql_data_from(self, file: Path):
        # Read the file and execute the sql statements
        with file.open(mode="r", encoding="utf-8") as file:
            # Get all statements from the file and execute each one sequentially
            statements: list[str] = [statement.strip() for statement in file.read().split(";")
                                     if isinstance(statement, str) and statement.strip() != '']

            while statements:
                statement: str = statements.pop(0)  # use the list as a queue for performance
                self.session.exec(text(statement))

    def _migrate_json_data_from(self, file: Path) -> FileMigration | None:
        root: dict = json.loads(file.read_text())
        for cls_signature in root.keys():  # Reads all the classes
            # get the class object to create an instance of it and persist
            module_name, class_name = cls_signature.rsplit('.', 1)
            module = runtime.import_module(module_name)
            cls = getattr(module, class_name)

            for obj in root[cls_signature]:  # Reads the list of class elements
                self.session.add(cls(**obj))
