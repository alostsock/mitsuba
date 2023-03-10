from datetime import datetime

from sqlalchemy import BigInteger, func
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column


class Base(MappedAsDataclass, DeclarativeBase):
    pass


class Timestamped:
    created_at: Mapped[datetime] = mapped_column(
        init=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class Guild(Timestamped, Base):
    __tablename__ = "guilds"

    guild_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=False
    )


# class AssignableRole(Timestamped, Base):
#     __tablename__ = "assignable_roles"

#     guild_id: Mapped[int] = mapped_column(primary_key=True)
#     role_id: Mapped[int] = mapped_column(primary_key=True)
