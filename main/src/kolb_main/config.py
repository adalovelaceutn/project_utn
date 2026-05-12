from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Setting(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Hugging Face Router (same stack as profiler)
    hf_token: str = ""
    hf_model_id: str = "Qwen/Qwen2.5-7B-Instruct"
    hf_max_new_tokens: int = 256
    hf_temperature: float = 0.1
    tavily_api_key: str = ""
    tavily_base_url: str = "https://api.tavily.com"

    main_host: str = "0.0.0.0"
    main_port: int = 8002
    profiler_a2a_url: str = "http://localhost:8001"
    api_base_url: str = "http://localhost:8000"
    mcp_server_url: str = "http://localhost:8080/mcp"
    a2a_timeout_seconds: int = 45


setting = Setting()