from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    mongo_uri: str = "mongodb://kolb_user:kolb_pass@localhost:27017"
    mongo_db_name: str = "kolb_db"
    mongo_kolb_collection: str = "kolb_profiles"
    mongo_users_collection: str = "users"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    auth_secret_key: str = "change-this-secret"
    auth_algorithm: str = "HS256"
    auth_access_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
