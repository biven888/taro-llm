from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from settings import settings


DATABASE_URL = f'sqlite+aiosqlite:///{settings.BASE_DIR}/{settings.GENERAL.DATABASE.PATH}/db.sqlite3'
engine = create_async_engine(url=DATABASE_URL)
session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def connection(method):
    async def wrapper(*args, **kwargs):
        async with session_maker() as session:
            try:
                return await method(*args, session=session, **kwargs)
            except Exception as err:
                await session.rollback()
                raise err
            finally:
                await session.close()

    return wrapper
