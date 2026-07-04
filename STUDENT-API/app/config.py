from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name : str = "Student Database API"
    debug: bool = True
    secret_key: str = "dev-secret-key-change-in-production"

    class Config:
        env_file = ".env"


settings = Settings()

