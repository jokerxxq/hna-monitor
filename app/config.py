from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_FILE = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    app_name: str = "HNA Flight Monitor"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_env: str = "dev"

    database_url: str = "sqlite:///./data/app.db"
    poll_interval_minutes: int = 15

    wechat_provider: str = "serverchan"
    serverchan_sendkey: str = ""

    price_provider: str = "variflight_mcp"  # mock | variflight_mcp

    # Variflight MCP (stdio)
    variflight_api_key: str = ""
    variflight_mcp_command: str = "npx"
    variflight_mcp_args: str = "-y @variflight-ai/variflight-mcp"

    model_config = SettingsConfigDict(env_file=str(_ENV_FILE), env_file_encoding="utf-8", extra="ignore")


settings = Settings()
