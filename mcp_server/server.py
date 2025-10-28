import random
from fastmcp import FastMCP

from mcp_server.methods import get_cards
from mcp_server.schemas import CardPydantic


mcp = FastMCP(name='Cards Taro System')


@mcp.tool()
async def get_three_cards():
    '''Получить три карты Таро'''

    all_cards = await get_cards()
    three_cards = random.sample(all_cards, 3)
    return [CardPydantic.model_validate(card).model_dump() for card in three_cards]
