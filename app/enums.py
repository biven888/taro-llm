from enum import StrEnum


class RoleEnum(StrEnum):
    '''
    Перечисление ролей для сообщений в чате
    '''

    SYSTEM = 'system'
    ASSISTANT = 'assistant'
    USER = 'user'
    TOOL = 'tool'
