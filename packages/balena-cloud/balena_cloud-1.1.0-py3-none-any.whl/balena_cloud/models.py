"""Asynchronous Python client for Balena Cloud."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime  # noqa: TC003

from mashumaro import DataClassDictMixin, field_options


@dataclass
class Organization(DataClassDictMixin):
    """Class to represent an organization in Balena Cloud."""

    id: int
    name: str
    handle: str
    company_name: str
    website: str
    created_at: datetime

    # Boolean fields
    is_frozen: bool


@dataclass
class Fleet(DataClassDictMixin):
    """Class to represent a fleet in Balena Cloud."""

    id: int
    name: str = field(metadata=field_options(alias="app_name"))
    slug: str
    uuid: str
    created_at: datetime

    # Boolean fields
    is_public: bool
    is_host: bool
    is_archived: bool
    is_discoverable: bool


@dataclass
class Release(DataClassDictMixin):
    """Class to represent a release in Balena Cloud."""

    id: int
    status: str
    semver: str
    semver_prerelease: str
    revision: int | str
    created_at: datetime

    # Boolean fields
    is_final: bool
    is_invalidated: bool
    is_passing_tests: bool


@dataclass
class Device(DataClassDictMixin):
    """Class to represent a device in Balena Cloud."""

    id: int
    name: str = field(metadata=field_options(alias="device_name"))
    status: str
    uuid: str

    # Boolean fields
    is_online: bool
    is_web_accessible: bool
    is_undervolted: bool

    latitude: float
    longitude: float


@dataclass
class EnvironmentVariable(DataClassDictMixin):
    """Class to represent an device environment variable in Balena Cloud."""

    id: int
    name: str
    value: str
    created_at: datetime


@dataclass
class Tag(DataClassDictMixin):
    """Class to represent a device tag in Balena Cloud."""

    id: int
    key: str = field(metadata=field_options(alias="tag_key"))
    value: str
