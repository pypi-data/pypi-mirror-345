from __future__ import annotations

import argparse
import asyncio
import re
from collections.abc import AsyncIterable, Mapping

import structlog
from eth_typing import ChecksumAddress
from evmchains import get_chain_meta
from web3 import AsyncWeb3
from web3.exceptions import Web3RPCError

from .utils import getenv

_logger = structlog.get_logger(__name__)


class ContractNotFound(RuntimeError):
    def __init__(self, *poargs, address: ChecksumAddress):
        super().__init__(*poargs)
        self.address = address

    def __str__(self):
        return f"{self.address}"


async def get_contract_deploy_block(
    w3: AsyncWeb3,
    address: ChecksumAddress,
) -> int:
    latest = await w3.eth.block_number
    low, high = 0, latest
    if not await w3.eth.get_code(address, block_identifier=latest):
        raise ContractNotFound(address=address)
    while low < high:
        mid = (low + high) // 2
        code = await w3.eth.get_code(address, block_identifier=mid)
        if not code:
            low = mid + 1
        else:
            high = mid
    return low


_BLOCK_RANGE_SUGGESTION_RE = re.compile(
    r"this block range should work: \[(0x[0-9a-fA-F]+), (0x[0-9a-fA-F]+)]"
)


async def gen_transfers(
    w3: AsyncWeb3,
    address: ChecksumAddress,
    from_block: int,
    to_block: int,
    *,
    min_stride: int = 1,
) -> AsyncIterable[Mapping]:
    logger = _logger.bind(token_address=address)
    contract = w3.eth.contract(address, abi=ERC20_TRANSFER_ABI)
    start = from_block
    stride = 1000000
    time = asyncio.get_running_loop().time
    while start <= to_block:
        stride = max(stride, min_stride)
        end = min(start + stride - 1, to_block)
        # logger.debug("scanning", start=start, end=end, stride=stride)
        try:
            logs = await contract.events.Transfer.get_logs(
                from_block=start, to_block=end
            )
        except Web3RPCError as e:
            message = e.rpc_response.get("error", {}).get("message")
            if message is None:
                raise
            match = _BLOCK_RANGE_SUGGESTION_RE.search(message)
            if match is None:
                raise
            suggested_start = int(match.group(1), 0)
            suggested_end = int(match.group(2), 0)
            assert suggested_start == start
            assert suggested_end >= suggested_start
            stride = suggested_end - suggested_start + 1
            logger.info(
                "retrying with suggested range",
                start=start,
                end=end,
                stride=stride,
            )
            continue
        else:
            stride = stride * 12 // 10
        logs = sorted(logs, key=lambda l: l["blockNumber"])
        for log in logs:
            yield log
        start = end + 1


ERC20_TRANSFER_ABI = [
    dict(
        name="Transfer",
        type="event",
        inputs=[
            dict(name="from", type="address", indexed=True),
            dict(name="to", type="address", indexed=True),
            dict(name="value", type="uint256", indexed=False),
        ],
        anonymous=False,
    )
]

ALCHEMY_ENDPOINT_SLUGS = {
    1: "eth-mainnet",
    5: "eth-goerli",
    10: "opt-mainnet",
    56: "bsc-mainnet",
    137: "polygon-mainnet",
    420: "opt-goerli",
    592: "astar-mainnet",
    1101: "polygonzkevm-mainnet",
    11155111: "eth-sepolia",
    42161: "arb-mainnet",
    421613: "arb-goerli",
    42170: "arb-nova",
    80001: "polygon-mumbai",
    1422: "polygonzkevm-testnet",
    8453: "base-mainnet",
    84532: "base-sepolia",
    252: "frax-mainnet",
    2522: "frax-sepolia",
    7777777: "zora-mainnet",
    999999999: "zora-sepolia",
}

INFURA_ENDPOINT_SLUGS = {
    1: "mainnet",
    5: "goerli",
    11155111: "sepolia",
    10: "optimism-mainnet",
    420: "optimism-goerli",
    137: "polygon-mainnet",
    80001: "polygon-mumbai",
    42161: "arbitrum-mainnet",
    421613: "arbitrum-goerli",
    42170: "arbitrum-nova",
    8453: "base-mainnet",
    84532: "base-sepolia",
    1101: "polygonzkevm-mainnet",
    1442: "polygonzkevm-testnet",
    534352: "scroll-mainnet",
    534351: "scroll-sepolia",
    59144: "linea-mainnet",
    59140: "linea-sepolia",
    11155420: "mantle-mainnet",
    5000: "mantle-sepolia",
    56: "bsc-mainnet",
    97: "bsc-testnet",
    100: "gnosis-mainnet",
    10200: "gnosis-chiado",
    42220: "celo-mainnet",
    44787: "celo-alfajores",
    110: "palm-mainnet",
    11297108109: "palm-testnet",
    324: "zksync-mainnet",
    280: "zksync-sepolia",
}


def json_rpc_endpoint(args: argparse.Namespace) -> str:
    if args.json_rpc is not None:
        return args.json_rpc
    chain = get_chain_meta(args.chain, args.network)
    if args.alchemy_api_key is not None:
        key = args.alchemy_api_key
        try:
            slug = ALCHEMY_ENDPOINT_SLUGS[chain.chainId]
        except KeyError:
            _logger.warning(f"Alchemy unsupported for {chain.name}")
        else:
            return f"https://{slug}.g.alchemy.com/v2/{key}"
    if args.infura_api_key is not None:
        key = args.infura_api_key
        try:
            slug = INFURA_ENDPOINT_SLUGS[chain.chainId]
        except KeyError:
            _logger.warning(f"Infura unsupported for {chain.name}")
        else:
            return f"https://{slug}.g.alchemy.com/v2/{key}"
    raise RuntimeError("JSON-RPC endpoint not configured")


DEFAULT_CHAIN_ECOSYSTEM = "base"
DEFAULT_CHAIN_NETWORK = "mainnet"


def configure_argparser(parser: argparse.ArgumentParser):
    parser.add_argument(
        "--chain",
        default=getenv("CHAIN", DEFAULT_CHAIN_ECOSYSTEM),
        metavar="NAME",
        help=f"""chain ecosystem name""",
    )
    parser.add_argument(
        "--network",
        default=getenv("NETWORK", DEFAULT_CHAIN_NETWORK),
        metavar="NAME",
        help=f"""chain network name""",
    )
    parser.add_argument(
        "--alchemy-api-key",
        metavar="KEY",
        default=getenv("ALCHEMY_API_KEY", None),
        help=f"""Alchemy API key (optional)""",
    )
    parser.add_argument(
        "--infura-api-key",
        metavar="KEY",
        default=getenv("INFURA_API_KEY", None),
        help=f"""Infura API key (optional)""",
    )
    parser.add_argument(
        "--json-rpc",
        metavar="URL",
        default=getenv("JSON_RPC_ENDPOINT", None),
        help=f"""custom JSON-RPC endpoint (optional)""",
    )
