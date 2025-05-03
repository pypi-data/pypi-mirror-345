from __future__ import annotations

import importlib.resources
from contextlib import asynccontextmanager
from dataclasses import replace
from decimal import Decimal
from typing import override

import alembic.command
import alembic.config
import eth_utils
import structlog
from eth_typing import ChecksumAddress
from eth_utils import to_checksum_address
from sqlalchemy import bindparam, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .. import Balance, LogPos
from ..base import AbstractBalanceTracker
from ..utils import getenv
from . import model

_logger = structlog.get_logger(__name__)


def configure_alembic(
    cfg: alembic.config.Config,
    *,
    session_maker: async_sessionmaker[AsyncSession] | None = None,
):
    with importlib.resources.path("baltrack", "migrations") as path:
        script_location = str(path)
    if session_maker is not None:
        db_uri = str(session_maker.kw["bind"].url)
        print(type(db_uri))
    else:
        db_uri = getenv("DB_URI", f"postgresql+asyncpg:///")

    # this is the Alembic Config object, which provides
    # access to the values within the .ini file in use.
    cfg.set_main_option("script_location", script_location)
    cfg.set_main_option("sqlalchemy.url", db_uri)


def migrate(session_maker: async_sessionmaker[AsyncSession] | None = None):
    cfg = alembic.config.Config()
    configure_alembic(cfg, session_maker=session_maker)
    alembic.command.upgrade(cfg, "head")


class SQLBalanceTracker(AbstractBalanceTracker):
    def __init__(
        self,
        *poargs,
        chain_id: int,
        token_address: ChecksumAddress,
        only_existing: bool = False,
        **kwargs,
    ):
        super().__init__(*poargs, **kwargs)
        self.__chain_id = chain_id
        self.__token_address = eth_utils.to_bytes(hexstr=token_address)
        self.__only_existing = only_existing
        self.__session: AsyncSession | None = None
        self.__latest: LogPos | None = None
        self.__logger = _logger.bind(
            chain_id=self.__chain_id,
            token_address=to_checksum_address(self.__token_address),
        )

    @asynccontextmanager
    async def bound_to_session(self, session: AsyncSession):
        try:
            assert self.__session is None
            self.__session = session
            yield
        finally:
            self.__session = None

    @property
    def session(self) -> AsyncSession:
        assert self.__session is not None, "not bound to a session"
        return self.__session

    @property
    def chain_id(self):
        return self.__chain_id

    async def __ensure(self, address: ChecksumAddress) -> model.Balance:
        addr_bytes = eth_utils.to_bytes(hexstr=address)
        balance = await self.session.get(
            model.Balance,
            dict(
                chain_id=self.__chain_id,
                token_address=self.__token_address,
                wallet_address=addr_bytes,
            ),
        )
        if balance is None:
            balance = model.Balance(
                chain_id=self.__chain_id,
                token_address=self.__token_address,
                wallet_address=addr_bytes,
            )
            self.session.add(balance)
        return balance

    @override
    async def get(self, address: ChecksumAddress) -> Balance | None:
        obj = await self.__ensure(address)
        if obj.value is None:
            return None
        return Balance(
            value=int(obj.value),
            log_pos=LogPos(
                block_number=obj.block_number, log_index=obj.log_index
            ),
        )

    @override
    async def reset(self) -> None:
        raise NotImplementedError()

    @override
    async def adjust(
        self, address: ChecksumAddress, delta: Balance
    ) -> Balance:
        obj = await self.__ensure(address)
        if obj.value is None:
            balance = replace(delta)
        else:
            balance = Balance(
                value=int(obj.value),
                log_pos=LogPos(
                    block_number=obj.block_number, log_index=obj.log_index
                ),
            )
            balance.adjust(delta)
        obj.value = Decimal(balance.value)
        obj.block_number = balance.log_pos.block_number
        obj.log_index = balance.log_pos.log_index
        if self.__latest is None or self.__latest < delta.log_pos:
            self.__latest = delta.log_pos
        return balance

    @property
    @override
    async def latest(self) -> LogPos | None:
        c = model.Balance.__table__.c
        async with self.session.begin():
            r = await self.session.execute(
                select(func.max(c.block_number)).where(
                    c.chain_id == bindparam("chain_id"),
                    c.token_address == bindparam("token_address"),
                ),
                dict(
                    chain_id=self.__chain_id,
                    token_address=self.__token_address,
                ),
            )
            block_number = r.scalars().one()
            if block_number is None:
                return None
            r = await self.session.execute(
                select(func.max(c.log_index)).where(
                    c.chain_id == bindparam("chain_id"),
                    c.token_address == bindparam("token_address"),
                    c.block_number == block_number,
                ),
                dict(
                    chain_id=self.__chain_id,
                    token_address=self.__token_address,
                ),
            )
            log_index = r.scalars().one()
            assert isinstance(block_number, int)
            assert isinstance(log_index, int)
            return LogPos(block_number=block_number, log_index=log_index)

    async def flush(self) -> None:
        await self.session.flush()
