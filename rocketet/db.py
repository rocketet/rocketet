import datetime

import aiopg.sa
from sqlalchemy import (
    MetaData, Table, Column, ForeignKey,
    Integer, String, DateTime, ARRAY
)

meta = MetaData()

user = Table(
    "user", meta,

    Column("id", Integer, primary_key=True),
    Column("username", String(200), nullable=False),
    Column("name", String(200)),
    Column("email", String(200), nullable=False),
    Column("avatar", String(200), nullable=False),
    Column("created_at", DateTime, default=datetime.datetime.utcnow, nullable=False)
)

group = Table(
    "group", meta,

    Column("id", Integer, primary_key=True),
    Column("name", String(200), nullable=False),
    Column("members", ARRAY(Integer)),
    Column("created_at", DateTime, default=datetime.datetime.utcnow, nullable=False),

    Column("owner_id",
           Integer,
           ForeignKey("user.id", ondelete="CASCADE"))
)


async def init_pg(app):
    conf = app["config"]["postgres"]
    engine = await aiopg.sa.create_engine(
        database=conf["database"],
        user=conf["user"],
        password=conf["password"],
        host=conf["host"],
        port=conf["port"],
        minsize=conf["minsize"],
        maxsize=conf["maxsize"],
    )
    app["db"] = engine


async def close_pg(app):
    app["db"].close()
    await app["db"].wait_closed()
