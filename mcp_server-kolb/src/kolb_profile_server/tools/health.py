from datetime import datetime, UTC


def register_tools(server) -> None:
    @server.tool()
    def healthcheck() -> dict[str, str]:
        """Health probe for smoke tests and client bootstrap checks."""
        return {
            "status": "ok",
            "server": "kolb-profile-server",
            "timestamp": datetime.now(UTC).isoformat(),
        }
