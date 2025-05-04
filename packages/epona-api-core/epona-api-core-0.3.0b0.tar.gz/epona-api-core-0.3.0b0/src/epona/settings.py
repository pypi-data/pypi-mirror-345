
import asyncpg
import os

_db_host = os.getenv("POSTGRES_HOST", "localhost")
_db_port = os.getenv("POSTGRES_PORT", "5432")
_db_user = os.getenv("POSTGRES_USER", "postgres")
_db_pass = os.getenv("POSTGRES_PASSWORD", "postgres")
_db_name = os.getenv("POSTGRES_DB_NAME", "core")
db_settings = {
    "db_host": _db_host,
    "db_port": _db_port,
    "db_user": _db_user,
    "db_pass": _db_pass,
    "db_name": _db_name
}


class Database:
    def __init__(self):
        self.host = db_settings["db_host"]
        self.port = db_settings["db_port"]
        self.user = db_settings["db_user"]
        self.password = db_settings["db_pass"]
        self.database = db_settings["db_name"]
        self._cursor = None

        self._connection_pool = None
        self.conn = None

    async def close(self) -> None:
        await self._connection_pool.close()

    async def connect(self) -> None:
        if not self._connection_pool:
            try:
                self._connection_pool = await asyncpg.create_pool(
                    min_size=1,
                    max_size=10,
                    command_timeout=300,
                    host=db_host,
                    port=db_port,
                    user=db_user,
                    password=db_pass,
                    database=db_name,
                )
            except Exception as ex:
                raise ex

    async def fetch_rows(self, query: str, params=None) -> asyncpg.Record:
        if not self._connection_pool:
            await self.connect()
        try:
            self.conn = await self._connection_pool.acquire()
            if params:
                # query, params = pyformat2psql(query, params)
                result = await self.conn.fetch(query, *params)
            else:
                result = await self.conn.fetch(query)
            return result
        except asyncpg.exceptions.PostgresError as err:
            raise err
        except Exception as ex:
            raise ex
        finally:
            await self._connection_pool.release(self.conn)

    async def execute(self, query: str, params=None) -> None:
        if not self._connection_pool:
            await self.connect()
        try:
            self.conn = await self._connection_pool.acquire()
            if params:
                # query, params = pyformat2psql(query, params)
                result = await self.conn.execute(query, *params)
            else:
                result = await self.conn.execute(query)
            return result
        except asyncpg.exceptions.PostgresError as err:
            raise err
        except Exception as ex:
            raise ex
        finally:
            await self._connection_pool.release(self.conn)


conn = Database()
