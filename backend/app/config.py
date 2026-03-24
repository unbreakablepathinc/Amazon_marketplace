from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    oxylabs_user: str = ""
    oxylabs_password: str = ""
    gemini_api_key: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
