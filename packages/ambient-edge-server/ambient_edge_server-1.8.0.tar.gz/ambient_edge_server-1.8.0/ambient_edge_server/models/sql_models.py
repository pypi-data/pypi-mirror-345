import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column

Base = declarative_base()


class SQLDeviceAuthRequest(Base):
    __tablename__ = "device_auth_t"

    id: Mapped[int] = mapped_column(primary_key=True)
    device_code: Mapped[str] = mapped_column(nullable=False)
    user_code: Mapped[str] = mapped_column(nullable=False)
    verification_uri: Mapped[str] = mapped_column(nullable=False)
    expires_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=False), nullable=False
    )


class SQLToken(Base):
    __tablename__ = "token_t"

    id: Mapped[int] = mapped_column(primary_key=True)
    access_token: Mapped[str] = mapped_column(nullable=False)
    refresh_token: Mapped[str] = mapped_column(nullable=False)
    expires_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=False), nullable=False
    )


class SQLNode(Base):
    __tablename__ = "node_t"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    resource_type: Mapped[str]
    description: Mapped[str] = mapped_column(nullable=True)
    org_id: Mapped[int]
    user_id: Mapped[int]
    role: Mapped[str]
    live: Mapped[bool] = mapped_column(default=False)
    architecture: Mapped[str]
    interfaces: Mapped[Optional[str]] = mapped_column(nullable=True)
    tags: Mapped[Optional[str]] = mapped_column(nullable=True)
    last_seen: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=False), nullable=True
    )
    error: Mapped[Optional[str]] = mapped_column(nullable=True)
    status: Mapped[Optional[str]] = mapped_column(nullable=True)
    cluster_id: Mapped[Optional[int]] = mapped_column(nullable=True)
    docker_swarm_info: Mapped[Optional[str]] = mapped_column(nullable=True)


class SQLAPIUser(Base):
    __tablename__ = "api_user_t"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str]


class SQLPlugin(Base):
    __tablename__ = "plugin_t"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True)
    topics: Mapped[Optional[str]] = mapped_column(nullable=True)
    module: Mapped[str]
    class_name: Mapped[str]
    extra_data: Mapped[Optional[str]] = mapped_column(nullable=True)
    retry_policy: Mapped[Optional[str]] = mapped_column(nullable=True)
    api_user_id: Mapped[int] = mapped_column(ForeignKey("api_user_t.id"), nullable=True)
