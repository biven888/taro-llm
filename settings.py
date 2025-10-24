import pathlib
import logging

from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    JsonConfigSettingsSource
)


logging.basicConfig(level=logging.DEBUG)


class GeneralConfig(BaseModel):
    '''
    Общие настройки
    '''

    PORT: int


class LLMAPIConfig(BaseModel):
    '''
    Настройки путей к API

    :param MODELS: API для получения списка моделей
    :type MODELS: str
    :param CHAT: API для генерации
    :type CHAT: str
    '''

    MODELS: str
    CHAT: str


class LLMConfig(BaseModel):
    '''
    Общие настройки для доступа к LLM

    :param HOST: хост сервера
    :type HOST: str
    :param PORT: порт сервера
    :type PORT: int
    :param API: API для получения списка моделей и генерации
    :type API: LLMAPIConfig
    :param TEMPERATURE: случайность ответа
    :type TEMPERATURE: float
    '''

    HOST: str
    PORT: int
    API: LLMAPIConfig
    TEMPERATURE: float


class Settings(BaseSettings):
    '''
    Все настройки из config.json

    :param BASE_DIR: базовая директория, где находится проект
    :type BASE_DIP: str
    :param GENERAL: общие настройки
    :type GENERAL: GeneralConfig
    :param LLM: настройки LLM
    :type LLM: LLMConfig
    '''

    BASE_DIR: str = str(pathlib.Path(__file__).parent)
    GENERAL: GeneralConfig
    LLM: LLMConfig

    model_config = SettingsConfigDict(json_file=f'{BASE_DIR}/config.json')

    @classmethod
    def settings_customise_sources(
            cls,
            settings_cls: type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (init_settings,
                JsonConfigSettingsSource(settings_cls),
                env_settings,
                dotenv_settings,
                file_secret_settings)


settings = Settings()
