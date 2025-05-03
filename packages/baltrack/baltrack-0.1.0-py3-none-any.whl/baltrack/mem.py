from __future__ import annotations

from dataclasses import replace
from typing import override

from eth_typing import ChecksumAddress

from baltrack import AbstractBalanceTracker, Balance, LogPos


class InMemoryBalanceTracker(AbstractBalanceTracker):
    def __init__(self, *poargs, **kwargs):
        super().__init__(*poargs, **kwargs)
        self.__balances = dict[ChecksumAddress, Balance]()
        self.__latest: LogPos | None = None

    @override
    async def reset(self) -> None:
        self.__balances.clear()
        self.__latest = None

    @override
    async def get(self, address: ChecksumAddress) -> Balance | None:
        return self.__balances.get(address)

    @override
    async def adjust(self, address: ChecksumAddress, delta: Balance) -> Balance:
        try:
            balance = self.__balances[address]
        except KeyError:
            balance = replace(delta)
            self.__balances[address] = balance
        else:
            balance.adjust(delta)
        if self.__latest is None or self.__latest < delta.log_pos:
            self.__latest = delta.log_pos
        return balance

    @property
    async def latest(self) -> LogPos | None:
        return self.__latest
