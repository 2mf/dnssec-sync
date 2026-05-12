from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .console import console
from .isp_client_api import ISPClientApi
from .isp_dns_api import ISPDnsApi
from .utils import print_header


class ISPDnssec:
    _instance: "ISPDnssec | None" = None

    def __init__(self) -> None:
        print_header("ISPCONFIG DNSSEC EXPORTER")
        self.cached_zone_data: dict[str, Any] | None = None

    @classmethod
    def instance(cls) -> "ISPDnssec":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load_keys(self) -> "ISPDnssec":
        dnsservers = ISPDnsApi.instance().get_all_server_ids()
        dnssecdata: dict[str, Any] = {}
        if not self.cached_zone_data:
            console.info("Loading DNS-Zones of all clients")
            for client in ISPClientApi.instance().get_all():
                cid = client["client_id"]
                for sid in dnsservers:
                    zones = ISPDnsApi.instance().connector.client.service.dns_zone_get_by_user(
                        ISPDnsApi.instance().connector.session_id,
                        cid,
                        sid,
                    )
                    for zone_ref in zones:
                        zone = ISPDnsApi.instance().get_zone(zone_ref["id"])
                        dnssecdata[zone_ref["origin"]] = {
                            "customer": client,
                            "zone": zone,
                            "dnssec": self.parse_dnssec_info(zone),
                        }
                print(".", end="")
            print()
            self.cached_zone_data = dnssecdata
        else:
            console.info("Using cached DNS-Zones")
        console.success(f"{len(self.cached_zone_data)} Zones loaded")
        return self

    def parse_dnssec_info(self, zone: dict[str, Any]):
        if zone.get("dnssec_initialized") == "N":
            return False
        dnssecdata = zone.get("dnssec_info", "")
        ds_match = re.findall(r"(\S*)\s+IN DS (\d+) (\d) ([2-]) ([\S ]+)", dnssecdata)
        zsk_match = re.findall(r"(\S*)\s+IN DNSKEY 256 (\d) (\d) ([\S ]+)", dnssecdata)
        ksk_match = re.findall(r"(\S*)\s+IN DNSKEY 257 (\d) (\d) ([\S ]+)", dnssecdata)
        if not ds_match or not zsk_match or not ksk_match:
            return False
        ds_row = ds_match[0]
        zsk_row = zsk_match[0]
        ksk_row = ksk_match[0]
        ds = {
            "record": ds_row[0],
            "origin": ds_row[0],
            "id": ds_row[1],
            "cipher": ds_row[2],
            "hashtype": ds_row[3],
            "hash": "".join(ds_row[4].split()),
        }
        zsk = {
            "record": zsk_row[0],
            "origin": zsk_row[0],
            "type": "256",
            "protocol": zsk_row[1],
            "cipher": zsk_row[2],
            "key": "".join(zsk_row[3].split()),
        }
        ksk = {
            "record": ksk_row[0],
            "origin": ksk_row[0],
            "type": "257",
            "protocol": ksk_row[1],
            "cipher": ksk_row[2],
            "key": "".join(ksk_row[3].split()),
        }
        return {"DS": ds, "ZSK": zsk, "KSK": ksk}

    def export_keys(self) -> "ISPDnssec":
        console.info("Exporting DNSSec data of loaded zones for submission to registrar")
        console.info("Target file: dnsseckeydata.json")
        dnssec_zones = {}
        for origin, zone in (self.cached_zone_data or {}).items():
            if zone["dnssec"] is False:
                print(f"    UNSIGNED:      {zone['zone']['origin']}")
                continue
            dnssec_zones[origin] = zone
        export_data = {
            origin: {"DS": zone["dnssec"]["DS"], "DNSKEY": zone["dnssec"]["KSK"]}
            for origin, zone in dnssec_zones.items()
        }
        Path("dnsseckeydata.json").write_text(json.dumps(export_data))
        console.success(f"Export finished. {len(dnssec_zones)} DNSSEC Keys exported.")
        return self
