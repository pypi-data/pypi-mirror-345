from typing import AsyncGenerator, Generator, Optional

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from qdrant_client import AsyncQdrantClient, QdrantClient
from redis import Redis
from redis.asyncio import Redis as AsyncRedis
from sqlmodel import Session
from sqlmodel.ext.asyncio.session import AsyncSession as SQLModelAsyncSession

from keble_db.wrapper import ExtendedAsyncRedis
from keble_db.wrapper.redis import ExtendedRedis

from ..session import Db


class ApiDbDeps:
    def __init__(self, db: Db):
        self.__db = db

    def get_redis(self) -> Generator[Redis | None, None, None]:
        r = None
        try:
            r = self.__db.get_redis(force_new_instance=True)
            yield r
        finally:
            self.__db.try_close(r)

    def get_aredis(self) -> Generator[AsyncRedis, None, None]:
        """Get an async Redis client."""
        r = None
        r = self.__db.get_aredis(new_instance=True)
        yield r  # no need to close redis, it will manage itself

    def get_extended_redis(
        self, *, namespace: Optional[str] = None
    ) -> Generator[ExtendedRedis | None, None, None]:
        r = None
        try:
            r = ExtendedRedis.extend(redis=self.__db.get_redis(), namespace=namespace)
            yield r
        finally:
            pass

    def get_mongo(self) -> Generator[MongoClient | None, None, None]:
        m = None
        try:
            m = self.__db.get_mongo(new_instance=True)
            yield m
        finally:
            self.__db.try_close(m)

    def get_amongo(self) -> Generator[AsyncIOMotorClient, None, None]:
        """Get an async MongoDB client."""
        m = None
        try:
            m = self.__db.get_amongo()
            yield m
        finally:
            self.__db.try_close(m)

    def get_write_sql(self) -> Generator[Session | None, None, None]:
        s = None
        try:
            s = self.__db.get_sql_write_client(new_instance=True)
            yield s
        finally:
            self.__db.try_close(s)

    def get_read_sql(self) -> Generator[Session | None, None, None]:
        """Get a SQL session for reading operations."""
        s = None
        try:
            s = self.__db.get_sql_read_client(new_instance=True)
            yield s
        finally:
            self.__db.try_close(s)

    async def get_async_write_sql(
        self,
    ) -> AsyncGenerator[SQLModelAsyncSession | None, None]:
        """Get an async SQL session for writing operations."""
        s = None
        try:
            s = self.__db.get_async_sql_write_client(new_instance=True)
            yield s
        finally:
            await self.__db.try_close_async(s)

    async def get_async_read_sql(
        self,
    ) -> AsyncGenerator[SQLModelAsyncSession | None, None]:
        """Get an async SQL session for reading operations."""
        s = None
        try:
            s = self.__db.get_async_sql_read_client(new_instance=True)
            yield s
        finally:
            await self.__db.try_close_async(s)

    def get_qdrant(self) -> Generator[QdrantClient | None, None, None]:
        q = None
        try:
            q = self.__db.get_qdrant_client(new_instance=True)
            yield q
        finally:
            self.__db.try_close(q)

    def get_aqdrant(self) -> Generator[AsyncQdrantClient | None, None, None]:
        """Get an async Qdrant client."""
        q = None
        try:
            q = self.__db.get_aqdrant_client(new_instance=True)
            yield q
        finally:
            self.__db.try_close(q)

    def get_extended_aredis(
        self, *, namespace: Optional[str] = None
    ) -> Generator[ExtendedAsyncRedis | None, None, None]:
        """Get an extended async Redis client with namespace support."""
        r = None
        r = ExtendedAsyncRedis.extend(
            aredis=self.__db.get_aredis(new_instance=True), namespace=namespace
        )
        yield r
