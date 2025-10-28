from sqlalchemy.ext.asyncio import AsyncSession

from mcp_server.dao import CardDAO
from mcp_server.database import connection

@connection
async def get_cards(session: AsyncSession):
    cards = await CardDAO.select_all(session=session)
    return cards


@connection
async def get_card(session: AsyncSession, card_id: int):
    card = await CardDAO.select_one_or_none(session=session, data_id=card_id)
    return card
