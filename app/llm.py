import json
import asyncio
import aiohttp
import requests

from settings import settings
from app.enums import RoleEnum
from app.validators import ChatPydantic


class LLMClient:
    '''
    Клиент для взаимодействия с LLM
    '''

    def __init__(self):
        '''
        Конструктор класса
        В нем указываются пути к API LLM, таймаут для клиента, сохраняются в память модели
        '''

        self.base_url = f'http://{settings.LLM.HOST}:{settings.LLM.PORT}'
        self.timeout = aiohttp.ClientTimeout(total=None)
        self.api_models = settings.LLM.API.MODELS
        self.api_chat = settings.LLM.API.CHAT
        self.models = self.get_available_models()
        self.temperature = settings.LLM.TEMPERATURE

    def get_available_models(self) -> list[dict]:
        '''
        Получение всех доступных моделей по указанному пути

        :return: Доступные модели
        :rtype: list[dict]
        '''

        try:
            response_models = requests.get(f'{self.base_url}{self.api_models}')
        except Exception as err:
            print(err)
            return []

        if response_models.status_code != 200:
            return []

        models = response_models.json()['models'] if 'models' in response_models.json() \
            else response_models.json()['data']
        return models

    async def generate_response(self, chat: ChatPydantic):
        '''
        Получение ответа от модели

        :param chat:
        :type chat: ChatPydantic
        :yields dict: Следующий ответ
        '''

        data_chat = {'model': chat.model,
                     'messages': [{'role': RoleEnum.SYSTEM,
                                   'content': chat.system_prompt}] +
                                 [{'role': message.role,
                                   'content': message.content} for message in chat.messages],
                     'temperature': self.temperature,
                     'stream': chat.stream}

        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.post(f'{self.base_url}{self.api_chat}', json=data_chat) as response_chat:
                if response_chat.status != 200:
                    raise requests.HTTPError

                if not chat.stream:
                    await asyncio.sleep(0)
                    yield response_chat.json()
                    return

                async for line in response_chat.content:
                    if line:
                        json_line = line.decode('utf-8')[5:]
                        try:
                            json_response_chat = json.loads(json_line)
                            if 'error' in json_response_chat:
                                raise requests.HTTPError
                            await asyncio.sleep(0)
                            yield json_response_chat
                        except json.JSONDecodeError:
                            continue
