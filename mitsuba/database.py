from dataclasses import asdict
from typing import Any, Sequence, TypeVar

from sqlalchemy import Column, inspect, literal, select
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.sql._typing import _ColumnExpressionArgument
from sqlalchemy.sql.selectable import TypedReturnsRows

from .models import Base

T = TypeVar("T", bound=Any)


class Database:
    def __init__(self, db_url: str) -> None:
        self.engine = create_async_engine(db_url)
        self.async_session = async_sessionmaker(
            bind=self.engine, expire_on_commit=False
        )

    # Helper methods for small, simple transactions.
    # For anything more involved, use a session.

    async def exists(self, *whereclause: _ColumnExpressionArgument[bool]) -> bool:
        async with self.async_session() as session:
            exists = await session.scalar(
                select(literal(True)).where(*whereclause).limit(1)
            )
        return bool(exists)

    async def fetch(self, statement: TypedReturnsRows[T]) -> Sequence[T]:
        async with self.async_session() as session:
            result = await session.scalars(statement=statement)
        return result.all()

    async def upsert(self, instances: Sequence[Base]):
        assert len(instances) > 0
        cls = instances[0].__class__
        assert issubclass(cls, Base)

        primary_keys: list[Column] = []
        other_cols: list[Column] = []
        server_defaulted_cols: list[Column] = []
        onupdate_values: dict[str, Any] = {}

        for column in inspect(cls).columns:
            # Manually set onupdate fields, since sqlalchemy doesn't take them into account.
            # See https://docs.sqlalchemy.org/en/19/dialects/postgresql.html#the-set-clause
            if column.onupdate:
                onupdate_values[column.name] = column.onupdate.arg  # type: ignore
            if column.server_default:
                server_defaulted_cols.append(column)
                continue
            (primary_keys if column.primary_key else other_cols).append(column)

        # Prepare insert values
        insert_values = [asdict(instance) for instance in instances]
        for insert_value in insert_values:
            for col in server_defaulted_cols:
                del insert_value[col.name]
        stmt = postgresql.insert(cls).values(insert_values)

        # Prepare update values
        update_values = dict([getattr(stmt.excluded, col.name) for col in other_cols])
        update_values.update(onupdate_values)
        stmt = stmt.on_conflict_do_update(
            index_elements=primary_keys,
            set_=update_values if update_values else None,
        )

        async with self.async_session() as session, session.begin():
            await session.execute(stmt)
