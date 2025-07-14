"""Configuration helpers for Flow Manager."""

from __future__ import annotations

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    domain_id: str = "default"
    etcd_endpoint: str = "localhost:2379"
    ryu_rest: str = "http://ryu:8080"

    class Config:
        env_prefix = "FM_"
