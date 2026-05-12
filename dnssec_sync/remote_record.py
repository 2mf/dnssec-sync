from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .constants import DNS_KEY_COMPARE_FORMAT, DNS_KEY_DATA_OK, DNS_KEY_KNOWN, DNS_KEY_PUBLISHED
from .isp_record import DnssecRecordISP


@dataclass
class DnssecRecordRemote:
    keydata: dict[str, Any]
    keystatus: int = field(default=DNS_KEY_PUBLISHED)

    def match(self, isp_key: DnssecRecordISP) -> "DnssecRecordRemote":
        if isp_key.get_public_key() == self.get_public_key():
            self.keystatus |= DNS_KEY_KNOWN
        if isp_key.get_string_representation() == self.get_string_representation():
            self.keystatus |= DNS_KEY_DATA_OK
        return self

    def get_key_status(self) -> int:
        return self.keystatus

    def get_publish_status(self) -> str:
        return str(self.keydata["status"])

    def get_key_id(self) -> str:
        return str(self.keydata["id"])

    def __str__(self) -> str:
        return f"{self.keydata['ownerName']}."

    def get_string_representation(self) -> str:
        return DNS_KEY_COMPARE_FORMAT.format(
            f"{self.keydata['ownerName']}.",
            self.keydata["flagId"],
            "3",
            self.keydata["algorithmId"],
            self.keydata["publicKey"],
            self.keydata["keyTag"],
            self.keydata["algorithmId"],
            self.keydata["digestTypeId"],
            self.keydata["digest"],
        )

    def get_fqdn(self) -> str:
        return str(self.keydata["ownerName"])

    def get_public_key(self) -> str:
        return str(self.keydata["publicKey"])
