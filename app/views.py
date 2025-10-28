import json
import aiohttp_jinja2
from aiohttp import client_exceptions
from aiohttp.web_request import Request
from aiohttp import web

from app.llm import LLMClient
from app.validators import ChatPydantic
from app.enums import RoleEnum

from mcp_server.methods import get_card
from mcp_server.schemas import OneCardPydantic


llm_client = LLMClient()


@aiohttp_jinja2.template('index.html')
async def index(request: Request):
    '''
    Обработчик основной страницы сайта

    :param request: запрос
    :type request: Request
    :return:
    '''

    await llm_client.get_available_models()
    return {'models': llm_client.models}


async def send_question(ws: web.WebSocketResponse, chat: ChatPydantic):
    '''
    Отправление запроса пользователя, получение и ответ в JSON

    :param ws: websocket
    :type ws: web.WebSocketResponse
    :param chat: чат
    :type chat: ChatPydantic
    :return:
    :rtype: None
    '''

    async for chunk in llm_client.generate_response(chat):
        try:
            if chunk.messages[-1].role == RoleEnum.TOOL:
                cards = json.loads(chunk.messages[-1].content)
                cards_info = []

                for card in cards:
                    card_info = await get_card(card_id=card['id'])
                    cards_info.append(OneCardPydantic.model_validate(card_info))

                chunk.messages[-1].content = cards_info
            await ws.send_json(chunk.model_dump())
        except client_exceptions.ClientConnectionResetError:
            await ws.close()


async def websocket_handler(request: Request):
    '''
    Обработчик запросов websocket

    :param request: запрос
    :type request: Request
    :return: websocket
    :rtype: web.WebSocketResponse
    '''

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for message in ws:
        if message.type == web.WSMsgType.TEXT:
            try:
                chat = ChatPydantic.model_validate_json(message.data)
                messages = []

                for message_chat in chat.messages:
                    if message_chat.role != RoleEnum.TOOL:
                        messages.append(message_chat)

                chat.messages = messages
            except json.JSONDecodeError:
                continue
            except Exception as err:
                print(err)
                continue
            await send_question(ws, chat)

            try:
                await ws.send_str("assistant_message_done")
            except client_exceptions.ClientConnectionResetError:
                await ws.close()
        elif message.type == web.WSMsgType.PING:
            await ws.pong()
        elif message.type == web.WSMsgType.CLOSE or message.type == web.WSMsgType.ERROR:
            await ws.close()

    return ws
