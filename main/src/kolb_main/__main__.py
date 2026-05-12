from __future__ import annotations

import uvicorn

from kolb_main.config import setting


def main() -> None:
    uvicorn.run(
        "kolb_main.server:app",
        host=setting.main_host,
        port=setting.main_port,
        reload=False,
    )


if __name__ == "__main__":
    main()