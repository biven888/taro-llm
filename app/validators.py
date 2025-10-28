from pydantic import BaseModel
from app.enums import RoleEnum
from mcp_server.schemas import OneCardPydantic


class MessagePydantic(BaseModel):
    '''
    Валидация сообщения

    :param role: роль сообщения
    :type role: app.enums.RoleEnum
    :param content: сообщение
    :type content: str
    '''

    role: RoleEnum
    content: str | list[OneCardPydantic]
    tool_call_id: str | None = None
    name: str | None = None


class ChatPydantic(BaseModel):
    '''
    Валидация чата

    :param model: модель
    :type model: str
    :param messages: сообщения чата
    :type messages: list[MessagePydantic]
    '''

    model: str
    system_prompt: str = ('Ты виртуальный таролог. Используй предоставленные инструменты для получения трех карт. '
                          'Ты связываешь карты вместе, чтобы создать интерпретацию, которая фокусируется на том, '
                          'как карты влияют друг на друга, принимая во внимание их позиции, чтобы добавить контекст, '
                          'а не интерпретировать каждую карту по отдельности. Например, карта в центре может быть '
                          'значительно подвержена влиянию (или ослаблена) картами слева и справа. '
                          'Дай подробную интерпретацию и практический совет.')
    messages: list[MessagePydantic]
