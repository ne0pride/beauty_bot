from pydantic import BaseSettings, SecretStr


class Settings(BaseSettings):
    bot_token: SecretStr
    admin_bot_token: SecretStr
    admin_bot_password: SecretStr
    bot_url: SecretStr
    db_name: SecretStr
    db_user: SecretStr
    db_host: SecretStr
    db_password: SecretStr

    class Config:
        env_file = '.env'
        # Кодировка читаемого файла
        env_file_encoding = 'utf-8'


# При импорте файла сразу создастся
# и провалидируется объект конфига,
# который можно далее импортировать из разных мест
config = Settings()