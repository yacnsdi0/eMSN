from pydantic import BaseSettings, Field, AnyHttpUrl


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    domain_id: str = Field("domain-1", env="DOMAIN_ID")
    jwks_url: AnyHttpUrl = Field(
        "https://nrf.local/.well-known/jwks.json", env="JWKS_URL"
    )
    ryu_rest: AnyHttpUrl = Field("http://ryu:8080", env="RYU_REST")
    etcd_host: str = Field("etcd", env="ETCD_HOST")
    etcd_port: int = Field(2379, env="ETCD_PORT")
    ca: str = Field("/certs/ca.pem", env="FM_CA")
    cert: str = Field("/certs/fm.pem", env="FM_CERT")
    key: str = Field("/certs/fm.key", env="FM_KEY")
    max_concurrent: int = Field(10, env="FM_MAX_CONCURRENT")


settings: Settings = Settings()  # type: ignore[call-arg]


def get_settings() -> Settings:
    """Return application settings singleton."""

    return settings
