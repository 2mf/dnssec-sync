from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class DnssecRecord(Protocol):
    def __str__(self) -> str: ...

    def get_string_representation(self) -> str: ...

    def get_public_key(self) -> str: ...

    def get_fqdn(self) -> str: ...
