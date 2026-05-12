from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path

from .console import console
from .zone import DnssecZone


class DnssecApi(ABC):
    def __init__(self) -> None:
        DnssecZone.reset()
        self.load_isp_keys()
        self.load_remote_keys()
        self.verify_zones()

    @abstractmethod
    def load_remote_keys(self) -> "DnssecApi":
        raise NotImplementedError

    def load_isp_keys(self) -> "DnssecApi":
        console.info("Loading Signing Information from ISPConfig export file dnsseckeydata.json")
        path = Path("dnsseckeydata.json")
        data = json.loads(path.read_text())
        if not data:
            raise RuntimeError("Could not parse JSON data from dnsseckeydata.json")
        for origin, keys in data.items():
            DnssecZone.add_ispconfig_key(origin, keys)
        console.success("ISPConfig DNSSEC keys loaded")
        return self

    def verify_zones(self) -> "DnssecApi":
        DnssecZone.verify_keys()
        return self

    def print_report(self) -> "DnssecApi":
        DnssecZone.print_status_report()
        return self

    def print_summary(self) -> "DnssecApi":
        DnssecZone.print_status_summary()
        return self

    def print_domain_list(self) -> "DnssecApi":
        DnssecZone.print_zone_system_list()
        return self

    def print_zone_keys(self, origin: str) -> "DnssecApi":
        DnssecZone.print_zone_keys(origin)
        return self

    @abstractmethod
    def publish_unpublished_keys(self) -> "DnssecApi":
        raise NotImplementedError

    @abstractmethod
    def clean_orphaned_keys(self, origin: str | None = None) -> "DnssecApi":
        raise NotImplementedError

    @abstractmethod
    def clean_corrupted_keys(self, origin: str | None = None) -> "DnssecApi":
        raise NotImplementedError
