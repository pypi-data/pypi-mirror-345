from __future__ import annotations

import os
from decimal import Decimal

from sqlalchemy import (
    DECIMAL,
    BigInteger,
    PrimaryKeyConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Balance(Base):
    __tablename__ = "balances"

    chain_id: Mapped[int] = mapped_column()
    token_address: Mapped[bytes] = mapped_column()
    wallet_address: Mapped[bytes] = mapped_column()
    value: Mapped[Decimal] = mapped_column(DECIMAL(62, 0), nullable=True)
    block_number: Mapped[int] = mapped_column(BigInteger, nullable=True)
    log_index: Mapped[int] = mapped_column(BigInteger, nullable=True)

    __table_args__ = (
        PrimaryKeyConstraint(chain_id, token_address, wallet_address),
    )


ALEMBIC_INI_PATH = os.path.join(os.path.dirname(__file__), "alembic.ini")
