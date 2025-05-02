from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ambient_log_level: str = "INFO"
    backend_api_url: str = "https://api.ambientlabs.io"
    edge_server_url: str = "http://localhost:7417"
    log_rotation: str = "10 MB"


settings = Settings()
