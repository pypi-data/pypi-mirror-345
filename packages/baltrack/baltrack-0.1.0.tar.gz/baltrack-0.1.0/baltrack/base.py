from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from typing import NamedTuple, Self

from eth_typing import ChecksumAddress


class AbstractBalanceTracker:
    @abstractmethod
    async def get(self, address: ChecksumAddress) -> Balance | None:
        """Get balance."""

    @abstractmethod
    async def reset(self) -> None:
        """Reset (forget) all balances."""

    @abstractmethod
    async def adjust(self, address: ChecksumAddress, delta: Balance) -> Balance:
        """
        Adjust a wallet balance.

        :param address: The wallet address to adjust.
        :param delta: The amount to adjust by,
            along with where the adjustment was made.
        :return: The new balance.
        """

    @property
    @abstractmethod
    async def latest(self) -> LogPos | None:
        """Return the latest block number/transaction index seen.

        :return: Latest block number/transaction index; None if empty.
        """


class LogPos(NamedTuple):
    block_number: int
    log_index: int


@dataclass(kw_only=True)
class Balance:
    value: int
    log_pos: LogPos

    def adjust(self, delta: Balance) -> Self:
        if self.log_pos >= delta.log_pos:
            raise StaleAdjustment(current=self, delta=delta)
        self.value += delta.value
        self.log_pos = delta.log_pos
        return self


class StaleAdjustment(RuntimeError):
    """Stale balance adjustment."""

    def __init__(self, *poargs, current: Balance, delta: Balance):
        super().__init__(*poargs)
        self.current = current
        self.delta = delta

    def __str__(self):
        return f"tried to apply delta {self.delta!r} against {self.current!r}"
