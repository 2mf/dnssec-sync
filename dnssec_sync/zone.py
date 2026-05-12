from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar

from .console import console
from .constants import DNS_KEY_DATA_OK, DNS_KEY_KNOWN, DNS_KEY_KNOWN_AND_PUBLISHED, DNS_KEY_NOT_CHECKED, DNS_KEY_OK, DNS_KEY_PUBLISHED
from .isp_record import DnssecRecordISP
from .remote_record import DnssecRecordRemote
from .utils import print_header, print_subheader


@dataclass
class DnssecZone:
    zones: ClassVar[dict[str, "DnssecZone"]] = {}

    origin: str | None = None
    ispconfig_key: DnssecRecordISP | None = None
    remote_keys: list[DnssecRecordRemote] = field(default_factory=list)
    zonestatus: int = DNS_KEY_NOT_CHECKED

    @classmethod
    def reset(cls) -> None:
        cls.zones = {}

    @classmethod
    def add_ispconfig_key(cls, origin: str, key: dict) -> None:
        if origin not in cls.zones:
            cls.zones[origin] = cls()
        cls.zones[origin]._add_ispconfig_key(key)

    @classmethod
    def add_remote_key(cls, key: dict) -> None:
        if key.get("status") in {"DELETED", "DELETE"}:
            return
        origin = f"{key['ownerName']}."
        if origin not in cls.zones:
            cls.zones[origin] = cls()
        cls.zones[origin]._add_remote_key(key)

    @classmethod
    def get_live_zones(cls) -> list["DnssecZone"]:
        return [z for z in cls.zones.values() if DNS_KEY_OK == (z.zonestatus & DNS_KEY_OK)]

    @classmethod
    def get_remote_zones(cls) -> list["DnssecZone"]:
        return [z for z in cls.zones.values() if z.has_remote_key()]

    @classmethod
    def get_isp_zones(cls) -> list["DnssecZone"]:
        return [z for z in cls.zones.values() if z.has_ispconfig_key()]

    @classmethod
    def get_zones_with_unpublished_keys(cls) -> list["DnssecZone"]:
        return [
            z
            for z in cls.zones.values()
            if DNS_KEY_KNOWN == (z.zonestatus & DNS_KEY_KNOWN)
            and DNS_KEY_DATA_OK != (z.zonestatus & DNS_KEY_DATA_OK)
        ]

    @classmethod
    def get_corrupted_keys(cls, origin: str | None = None) -> list[DnssecRecordRemote]:
        if origin is not None:
            zone = cls.zones.get(origin)
            return zone.get_remote_corrupted_keys() if zone else []
        keys: list[DnssecRecordRemote] = []
        for zone in cls.zones.values():
            keys.extend(zone.get_remote_corrupted_keys())
        return keys

    @classmethod
    def get_orphaned_keys(cls, origin: str | None = None) -> list[DnssecRecordRemote]:
        if origin is not None:
            zone = cls.zones.get(origin)
            return zone.get_remote_orphaned_keys() if zone else []
        keys: list[DnssecRecordRemote] = []
        for zone in cls.zones.values():
            keys.extend(zone.get_remote_orphaned_keys())
        return keys

    @classmethod
    def print_zone_system_list(cls) -> None:
        print_header("ZONE OVERVIEW")
        cls.print_isp_zones()
        cls.print_remote_zones()
        print()

    @classmethod
    def print_status_report(cls) -> None:
        print_header("ZONE STATUS REPORT")
        print(f"{'Result':<8} {'ISP':<8} {'Registry':<8} {'Status':<8} {'Co':<2} {'Or':<2} Domain")
        for zone in cls.zones.values():
            zone.print_status_report_line()
        print()

    @classmethod
    def print_status_summary(cls) -> None:
        live_zones = cls.get_live_zones()
        live_zones_ok = [z for z in live_zones if z.get_remote_live_key() and z.get_remote_live_key().get_publish_status() == "OK"]
        print_header("DNSSEC ZONE SUMMARY")
        print(f"{len(live_zones):<8} Corresponding Keys in ISP and Remote")
        print(f"{len(live_zones_ok):<8} Corresponding Keys live and working")
        print(f"{len(cls.get_isp_zones()):<8} signed zones in ISPConfig")
        print(f"{len(cls.get_zones_with_unpublished_keys()):<8} DNSSEC key from ISPConfig not published")
        print(f"{len(cls.get_remote_zones()):<8} Remote published zones")
        print(f"{len(cls.get_corrupted_keys()):<8} Remote Keys with corrupt data")
        print(f"{len(cls.get_orphaned_keys()):<8} possible Remote orphan keys")
        print()

    @classmethod
    def print_remote_zones(cls) -> None:
        remote_zones = cls.get_remote_zones()
        print_subheader(f"{len(remote_zones)} DNSSEC Zones published Remote")
        for zone in remote_zones:
            zone.print_remote_zone()

    @classmethod
    def print_isp_zones(cls) -> None:
        isp_zones = cls.get_isp_zones()
        print_subheader(f"{len(isp_zones)} DNSSEC Zones exported from ISPConfig")
        for zone in isp_zones:
            zone.print_ispconfig_zone()

    @classmethod
    def print_zone_keys(cls, origin: str) -> None:
        zone = cls.zones.get(origin)
        print_header(f"{origin} ZONE KEYS")
        print_subheader("ISPConfig Key")
        if zone and zone.get_ispconfig_key():
            print(zone.get_ispconfig_key().get_string_representation())
        else:
            console.warning("No DNSKey in ISPConfig")
        print_subheader("Remote Keys")
        if zone and zone.get_remote_keys():
            for remote_key in zone.get_remote_keys():
                print(remote_key.get_string_representation())
        else:
            console.warning("No Remote published DNSKey")

    @classmethod
    def verify_keys(cls) -> None:
        for zone in cls.zones.values():
            zone.verify()

    def _add_ispconfig_key(self, key: dict) -> "DnssecZone":
        self.ispconfig_key = DnssecRecordISP.from_export(key)
        self.origin = key["DNSKEY"]["origin"]
        return self

    def _add_remote_key(self, key: dict) -> "DnssecZone":
        self.remote_keys.append(DnssecRecordRemote(key))
        self.origin = f"{key['ownerName']}."
        return self

    def has_ispconfig_key(self) -> bool:
        return self.ispconfig_key is not None

    def has_remote_key(self) -> bool:
        return len(self.remote_keys) > 0

    def print_ispconfig_zone(self) -> "DnssecZone":
        if self.has_ispconfig_key():
            print(f"     - {self.ispconfig_key}")
        return self

    def print_remote_zone(self) -> "DnssecZone":
        if self.has_remote_key():
            print(f"     - {self.remote_keys[0]}")
        return self

    def get_remote_keys(self) -> list[DnssecRecordRemote]:
        return self.remote_keys

    def get_remote_live_key(self) -> DnssecRecordRemote | None:
        live_keys = [key for key in self.remote_keys if DNS_KEY_OK == (key.get_key_status() & DNS_KEY_OK)]
        return live_keys[0] if live_keys else None

    def get_ispconfig_key(self) -> DnssecRecordISP | None:
        return self.ispconfig_key

    def get_remote_corrupted_keys(self) -> list[DnssecRecordRemote]:
        return [key for key in self.remote_keys if key.get_key_status() == DNS_KEY_KNOWN_AND_PUBLISHED]

    def get_remote_orphaned_keys(self) -> list[DnssecRecordRemote]:
        return [key for key in self.remote_keys if key.get_key_status() == DNS_KEY_PUBLISHED]

    def print_status_report_line(self) -> None:
        status_overall = "x" if DNS_KEY_OK == (self.zonestatus & DNS_KEY_OK) else "-"
        status_isp = "x" if DNS_KEY_KNOWN == (self.zonestatus & DNS_KEY_KNOWN) else "-"
        status_remote = "x" if DNS_KEY_PUBLISHED == (self.zonestatus & DNS_KEY_PUBLISHED) else "-"
        live_key = self.get_remote_live_key()
        status_live_key = live_key.get_publish_status() if live_key else ""
        corrupts = str(len(self.get_remote_corrupted_keys()) or "")
        orphans = str(len(self.get_remote_orphaned_keys()) or "")
        print(f"{status_overall:<8} {status_isp:<8} {status_remote:<8} {status_live_key:<8} {corrupts:<2} {orphans:<2} {self.origin}")

    def verify(self) -> "DnssecZone":
        if self.has_ispconfig_key():
            self.zonestatus |= DNS_KEY_KNOWN
        if self.has_remote_key():
            self.zonestatus |= DNS_KEY_PUBLISHED
        if self.zonestatus != DNS_KEY_KNOWN_AND_PUBLISHED:
            return self
        for remote_key in self.remote_keys:
            remote_key.match(self.ispconfig_key)
            self.zonestatus |= remote_key.get_key_status()
        return self
