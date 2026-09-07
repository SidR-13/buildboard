from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    redis_url: str
    anthropic_api_key: str = ""
    github_webhook_secret: str = ""
    github_token: str = ""
    jwt_secret: str = ""
    ai_mock: bool = True
    claude_model: str = "claude-haiku-4-5-20251001"

    class Config:
        env_file = ".env"


settings = Settings()
