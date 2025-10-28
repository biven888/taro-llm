import typing
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mcp_server.models import Base, Card


T = typing.TypeVar('T', bound=Base)


class BaseDAO[T: Base]:
    model: type[T]

    def __init_subclass__(cls, **kwargs):
        cls.model = cls.__orig_bases__[0].__args__[0]

    @classmethod
    async def select_one_or_none(cls, session: AsyncSession, data_id: int):
        record = await session.get(cls.model, data_id)
        return record

    @classmethod
    async def select_all(cls, session: AsyncSession, **filter_by):
        query = select(cls.model).filter_by(**filter_by)
        result = await session.execute(query)
        records = result.unique().scalars().all()
        return records


class CardDAO(BaseDAO[Card]):
    ...
