import asyncio
from openai import AsyncOpenAI, DefaultAioHttpClient
from fastmcp.exceptions import ToolError

from settings import settings
from app.enums import RoleEnum
from app.validators import ChatPydantic, MessagePydantic
from mcp_server.client import mcp_client, call_tool


class LLMClient:
    '''
    Клиент для взаимодействия с LLM
    '''

    def __init__(self):
        '''
        Конструктор класса
        В нем указываются пути к API LLM, таймаут для клиента, сохраняются в память модели
        '''

        self.base_url = f'http://{settings.LLM.HOST}:{settings.LLM.PORT}{settings.LLM.API_PREFIX}'
        self.llm_client = AsyncOpenAI(api_key='EMPTY', base_url=self.base_url, http_client=DefaultAioHttpClient())
        self.models = []
        self.temperature = settings.LLM.TEMPERATURE

    async def get_available_models(self):
        data_models = await self.llm_client.models.list()
        self.models = data_models.data

    async def generate_response(self, chat: ChatPydantic):
        '''
        Получение ответа от модели

        :param chat:
        :type chat: ChatPydantic
        :yields dict: Следующий ответ
        '''

        tools = await self.get_tools()
        messages = ([{'role': RoleEnum.SYSTEM,
                     'content': chat.system_prompt}] +
                    [{'role': message.role,
                      'content': message.content} for message in chat.messages])

        response_tools = await self.llm_client.chat.completions.create(model=chat.model,
                                                                      messages=messages,
                                                                      temperature=self.temperature,
                                                                      tools=tools)
        tool_calls = response_tools.choices[0].message.tool_calls

        if tool_calls:
            for tool_call in tool_calls:
                if tool_call.function:
                    tool_result = await call_tool(tool_name=tool_call.function.name,
                                                  arguments={})
                    message_tool = {'role': RoleEnum.TOOL,
                                     'tool_call_id': tool_call.id,
                                     'name': tool_call.function.name,
                                     'content': tool_result}
                    messages.append(message_tool)
                    chat.messages.append(MessagePydantic.model_validate(message_tool))

        yield chat
        message_assistant = MessagePydantic(role=RoleEnum.ASSISTANT, content='')
        chat.messages.append(message_assistant)
        response_chat = await self.llm_client.chat.completions.create(model=chat.model,
                                                                      messages=messages,
                                                                      temperature=self.temperature,
                                                                      stream=True)

        async for line in response_chat:
            if line and line.choices[0].delta.content:
                await asyncio.sleep(0)
                message_assistant.content += line.choices[0].delta.content
                yield chat

    async def get_tools(self):
        async with mcp_client:
            tools = await mcp_client.list_tools()
            json_tools = []

            for tool in tools:
                json_tool = {'type': 'function',
                             'function': {
                                 'name': tool.name,
                                 'description': tool.description,
                                 'parameters': tool.inputSchema
                             }}
                json_tools.append(json_tool)

            return json_tools
