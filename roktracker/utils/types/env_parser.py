from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(BaseSettings):
    dev_server_port: int = 3000
    development: bool = False

    model_config = SettingsConfigDict(cli_parse_args=True)
