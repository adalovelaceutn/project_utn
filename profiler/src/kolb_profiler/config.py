from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Setting(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Hugging Face (Qwen)
    hf_token: str = ""
    hf_model_id: str = "Qwen/Qwen2.5-7B-Instruct"
    hf_max_new_tokens: int = 512
    hf_temperature: float = 0.7

    # Services
    mcp_server_url: str = "http://localhost:8080/mcp"
    api_base_url: str = "http://localhost:8000"

    # A2A server
    a2a_host: str = "0.0.0.0"
    a2a_port: int = 8001


setting = Setting()
