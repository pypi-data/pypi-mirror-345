from commons.database import DatabaseAdapter

# commons-lib

This is a common library for dependencies that might be useful on Python Development.

It offers:
- A thread-safe Database Adapter + File-Based Data Migration executor powered by [SQLModel ORM (sqlalchemy)](https://sqlmodel.tiangolo.com/) and [Pydantic](https://pydantic.dev/);
- Local Key-Value Cache database, powered by SQLite;
- Better logging configuration via `commons.logging`;
- Dynamic runtime import (`commons.runtime`);
- Local/HTTP Remote Resource representation powered by [httpx](https://www.python-httpx.org/);
- Currency support (`commons.currencies`):
  - Currencies in ISO-4217 format powered by [pycountry](https://github.com/pycountry/pycountry/);
  - Brazilian Pix support;
  - Bitcoin (BTC) and Monero (XMR) support;
  - Live currencies quotation from [Wise](https://wise.com/) and [cryptocompare.com](https://cryptocompare.com/);
  - Payment QRCode generation for cryptocurrencies and Pix;
- Support for i18n via [Babel](https://babel.pocoo.org/) (`commons.locale`):
  - Wraps common features and format methods from Babel;
  - Automatically compile `.po` files;
  - [ ] Extracts translatable strings from source-code;
- [ ] Notification System (powered by [apprise](https://github.com/caronc/apprise)):
  - [x] SMTP tool for sending messages (to be replaced);
- [ ] Media support:
  - [x] Media/MIME Types (`commons.media.mimetypes`);
  - [ ] Document Processor;
  - [x] Image Processor (`commons.media.images`);
  - [ ] Audio Processor;
  - [ ] Video Processor;
  - [ ] Subtitle Processor;

> ⚠️ This is under active development and might not be ready for production environments.

## Testing

```shell
coverage run -m unittest && coverage html -d tests/coverage/html
```

## Build
```shell
uv build && twine upload dist/*
```

## Usage

This section describe how to use this library.

### Database

#### Database Adapters

To make the life easier when handling with multiple databases, there is a Database Adapter class available at `commons.database.DatabaseAdapter`.

> This class is a Pydantic Model that wraps the logic behind `sqlalchemy` to allow async connection handling to several database drivers. By default, it creates an adapter for a SQLite In-Memory Database.

To allow asynchronous operations, the adapter is thread-safe.

##### Creating an Adapter

```python
from commons.database import DatabaseAdapter

DatabaseAdapter()
# 'sqlite:///:memory:?cache=shared'
DatabaseAdapter(scheme="sqlite", database="sqlite.db")
# 'sqlite:///sqlite.db'
DatabaseAdapter(scheme="postgresql", username="postgres", password="1234", host="db.domain.tld", port=5432, database="mydb")
# 'postgresql://postgres:1234@db.domain.tld:5432/mydb'
DatabaseAdapter(scheme="redis", username="username", password="pwd", host="db.domain.tld", port=6379, database="0")
# 'redis://username:pwd@db.domain.tld:6379/0'
```

##### Connecting to a database

```python
from commons.database import DatabaseAdapter
with DatabaseAdapter().session() as session:
    # your code
    session.close()
```

#### Generic Repository Class

To implement a database repository, you can follow the generic approach described below:

```python
from commons.database import DatabaseAdapter
from typing import Optional
from sqlalchemy import Session

class GenericDatabaseRepository:
    database: DatabaseAdapter
    session: Optional[Session] = None

    def __init__(self, database: DatabaseAdapter = DatabaseAdapter()):
        self.database = database

    def __enter__(self):
        self.session = self.database.session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
        self.session = None
        
    # your repository methods

# Usage
with GenericDatabaseRepository() as db:
    # your code  
    ...

```

This allows easy handling of the database sessions and data persistence. An example of this approach is the `commons.database.Cache` class, described on the next section.


#### Cache Databases

To make a smart use of the SQL power, a Cache class is available at `commons.database.Cache`, allowing quick storage of binary data in key-value scheme.

> By default, the class uses a default database adapter that makes use of an In-Memory SQLite database, but a  `commons.database.DatabaseAdapter` can be specified in the constructor. Be aware that, now, the class is implemented using SQL, so, NoSQL databases are not supported.

Below, an example on how to use it:

```python
from commons.database import Cache, CacheEntry

with Cache() as cache:
    # set an entry
    entry: CacheEntry = cache.set("key", b"value", max_age=3600)

    # Get entry data
    data: bytes = entry.data
    
    # Check if entry is expired
    if entry.expired:
      print("Cache is expired.")
    else:
      print("Cache is not expired.")
    
    # Invalidate an entry
    cache.invalidate("key")

    # Get an entry from a key
    stored_entry: CacheEntry | None = cache.get("key")
```

