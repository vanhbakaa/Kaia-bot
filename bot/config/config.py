from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    API_ID: int
    API_HASH: str

    AUTO_UPGRADE: bool = True
    REF_LINK: str = "https://t.me/kaiaplaybot/app?startapp=ref-sfpx96ju54fv41n"
    AUTO_SPIN: bool = False

    USE_PROXY_FROM_FILE: bool = False


settings = Settings()


