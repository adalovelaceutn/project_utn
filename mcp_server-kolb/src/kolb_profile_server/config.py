from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Setting:
    host: str = os.getenv("KOLB_SERVER_HOST", "0.0.0.0")
    port: int = int(os.getenv("KOLB_SERVER_PORT", "8080"))
    path: str = os.getenv("KOLB_SERVER_PATH", "/mcp")


setting = Setting()
