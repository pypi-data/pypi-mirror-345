"""baltrack tracks ERC20 token balances."""

import asyncio
import sys
from argparse import ArgumentParser
from itertools import count

import structlog
from dotenv import load_dotenv
from eth_typing import ChecksumAddress
from eth_utils import to_checksum_address
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from web3 import AsyncWeb3
from web3.constants import CHECKSUM_ADDRESSS_ZERO

__version__ = "0.1.0"

from ._web3 import (
    DEFAULT_CHAIN_ECOSYSTEM,
    DEFAULT_CHAIN_NETWORK,
    configure_argparser,
    gen_transfers,
    get_contract_deploy_block,
    json_rpc_endpoint,
)
from .base import Balance, LogPos
from .sql import SQLBalanceTracker, migrate
from .utils import getenv

_logger = structlog.get_logger(__name__)


async def main():
    load_dotenv()

    parser = ArgumentParser()
    configure_argparser(parser)
    parser.add_argument(
        "--db",
        default=getenv("DB_URI", "postgresql+asyncpg:///"),
        metavar="URI",
        help="DB-API connection URI",
    )
    parser.add_argument(
        "token_addresses",
        type=to_checksum_address,
        nargs="+",
        metavar="ADDRESS",
        help="token contract addresses",
    )
    args = parser.parse_args()

    w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(json_rpc_endpoint(args)))
    engine = create_async_engine(args.db)
    session_maker = async_sessionmaker(engine)

    token_addresses = args.token_addresses

    tasks = [
        asyncio.create_task(
            scrape_token_task(
                token_address=to_checksum_address(token_address),
                w3=w3,
                session_maker=session_maker,
            )
        )
        for token_address in token_addresses
    ]
    await asyncio.gather(*tasks, return_exceptions=True)


async def scrape_token_task(token_address: ChecksumAddress, *poargs, **kwargs):
    try:
        await scrape_token(token_address, *poargs, **kwargs)
    except Exception:
        _logger.error(
            "token scraping task failed",
            token_address=token_address,
            exc_info=sys.exc_info(),
        )
        raise


async def scrape_token(
    token_address: ChecksumAddress,
    w3: AsyncWeb3,
    session_maker: async_sessionmaker,
):
    # await migrate(session_maker)
    tracker = SQLBalanceTracker(
        chain_id=await w3.eth.chain_id,
        token_address=token_address,
    )

    logger = _logger.bind(token_address=token_address)

    async with (
        session_maker() as session,
        tracker.bound_to_session(session),
    ):
        latest = await tracker.latest

    if latest is None:
        logger.info("querying for contract genesis")
        first = await get_contract_deploy_block(w3, token_address)
    else:
        logger.info("last synced through", block_number=latest.block_number)
        first = latest.block_number + 1
    last = await w3.eth.block_number
    logger.debug("looking for transfers", first=first, last=last)
    num_xfers = 0
    last_block = None
    done = False

    async def log_progress():
        time = asyncio.get_running_loop().time
        for due in count(time(), 1):
            now = time()
            await asyncio.sleep(due - now)
            logger.debug("in progress", num_xfers=num_xfers, block=last_block)
            if done:
                return

    progress_logger_task = asyncio.create_task(log_progress())
    try:
        async with (
            session_maker() as session,
            tracker.bound_to_session(session),
        ):
            async for log in gen_transfers(
                w3, token_address, first, last, min_stride=2000
            ):
                args = log["args"]
                sender = to_checksum_address(args["from"])
                recipient = to_checksum_address(args["to"])
                value = args["value"]
                block_number = log["blockNumber"]
                if last_block != block_number:
                    # logger.debug("flushing", block_number=block_number)
                    await tracker.flush()
                    await session.commit()
                    last_block = block_number
                log_pos = LogPos(block_number, log["logIndex"])
                if sender != recipient:
                    if sender != CHECKSUM_ADDRESSS_ZERO:
                        await tracker.adjust(
                            sender, Balance(value=-value, log_pos=log_pos)
                        )
                    if recipient != CHECKSUM_ADDRESSS_ZERO:
                        await tracker.adjust(
                            recipient, Balance(value=value, log_pos=log_pos)
                        )
                    num_xfers += 1
            await tracker.flush()
            await session.commit()
    finally:
        done = True
        await asyncio.gather(progress_logger_task)
    logger.debug("finished", num_xfers=num_xfers, block=last_block)
