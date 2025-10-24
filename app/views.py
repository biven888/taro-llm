import json
import aiohttp_jinja2
from aiohttp import client_exceptions
from aiohttp.web_request import Request
from aiohttp import web

from app.llm import LLMClient
from app.validators import ChatPydantic, MessagePydantic
from app.enums import RoleEnum


llm_client = LLMClient()


@aiohttp_jinja2.template('index.html')
async def index(request: Request):
    '''
    Обработчик основной страницы сайта

    :param request: запрос
    :type request: Request
    :return:
    '''
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

    new_chat = chat.model_copy(deep=True)
    message_assistant = MessagePydantic(role=RoleEnum.ASSISTANT, content='')
    new_chat.messages.append(message_assistant)

    if chat.stream:
        async for chunk in llm_client.generate_response(chat):
            if 'choices' in chunk and 'delta' in chunk['choices'][0] and 'content' in chunk['choices'][0]['delta']:
                message_assistant.content += chunk['choices'][0]['delta']['content']
                try:
                    await ws.send_json(new_chat.model_dump())
                except client_exceptions.ClientConnectionResetError:
                    await ws.close()
    else:
        chunk = list(await llm_client.generate_response(chat))[0]
        if 'choices' in chunk and 'delta' in chunk['choices'][0] and 'content' in chunk['choices'][0]['delta']:
            message_assistant.content = chunk['choices'][0]['delta']['content']
            try:
                await ws.send_json(new_chat.model_dump())
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
