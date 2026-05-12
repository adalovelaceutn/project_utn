"""Entry point for the Kolb Profiler A2A server."""
from __future__ import annotations

import uvicorn

from kolb_profiler.config import setting


def main() -> None:
    uvicorn.run(
        "kolb_profiler.a2a.server:app",
        host=setting.a2a_host,
        port=setting.a2a_port,
        reload=False,
    )


if __name__ == "__main__":
    main()
