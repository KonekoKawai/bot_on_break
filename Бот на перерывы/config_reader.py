from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

#Для токена
class Settings(BaseSettings):
    bot_token: SecretStr
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


config = Settings()

#Количество очередей и человек в ней 
queue_drivers = 2;
queue_client = 2;