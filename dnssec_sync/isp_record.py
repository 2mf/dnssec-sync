from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .constants import DNS_KEY_COMPARE_FORMAT


@dataclass
class DnssecRecordISP:
    dnskey: dict[str, Any]
    ds: dict[str, Any]

    @classmethod
    def from_export(cls, keys: dict[str, Any]) -> "DnssecRecordISP":
        return cls(dnskey=keys["DNSKEY"], ds=keys["DS"])

    def __str__(self) -> str:
        return str(self.dnskey["origin"])

    def get_string_representation(self) -> str:
        return DNS_KEY_COMPARE_FORMAT.format(
            self.dnskey["origin"],
            self.dnskey["type"],
            self.dnskey["protocol"],
            self.dnskey["cipher"],
            self.dnskey["key"],
            self.ds["id"],
            self.ds["cipher"],
            self.ds["hashtype"],
            self.ds["hash"],
        )

    def get_public_key(self) -> str:
        return str(self.dnskey["key"])

    def get_fqdn(self) -> str:
        origin = str(self.dnskey["origin"])
        return origin[:-1] if origin.endswith(".") else origin

    def get_dnskey_record(self) -> str:
        return (
            f"{self.dnskey['origin']} IN DNSKEY {self.dnskey['type']} "
            f"{self.dnskey['protocol']} {self.dnskey['cipher']} {self.dnskey['key']}"
        )

    def get_ds_record(self) -> str:
        return (
            f"{self.ds['origin']} IN DS {self.ds['id']} {self.ds['cipher']} "
            f"{self.ds['hashtype']} {self.ds['hash']}"
        )
