from __future__ import annotations

from .api_base import DnssecApi
from .utils import print_header
from .zone import DnssecZone
from .inwx_connector import InwxConnector


class DnssecApiInwx(DnssecApi):
    def __init__(self) -> None:
        self.connector = InwxConnector()
        self.api = self.connector.api
        super().__init__()

    def load_remote_keys(self) -> "DnssecApiInwx":
        result = self.api.call_api("nameserver.listDnssec")
        if result["code"] != 1000:
            raise RuntimeError(f"[{result['code']}] {result['msg']}")
        for inwx_key in result.get("resData", {}).get("dnssec", []):
            DnssecZone.add_remote_key(inwx_key)
        return self

    def publish_unpublished_keys(self) -> "DnssecApiInwx":
        print_header("PUBLISHING ALL UNPUBLISHED KEYS")
        for zone in DnssecZone.get_zones_with_unpublished_keys():
            isp_key = zone.get_ispconfig_key()
            params = {
                "domain": isp_key.get_fqdn(),
                "dnskey": isp_key.get_dnskey_record(),
                "ds": isp_key.get_ds_record(),
                "calcDigest": False,
            }
            self._perform_key_operation("nameserver.createDnssec", params, str(isp_key))
        print()
        return self

    def clean_orphaned_keys(self, origin: str | None = None) -> "DnssecApiInwx":
        print_header("REMOVING ALL ORPHANED KEYS")
        for key in DnssecZone.get_orphaned_keys(origin):
            self._perform_key_operation("nameserver.deleteDnssec", {"id": key.get_key_id()}, str(key))
        print()
        return self

    def clean_corrupted_keys(self, origin: str | None = None) -> "DnssecApiInwx":
        print_header("REMOVING ALL ENTRIES WITH CORRUPTED KEY DATA")
        for key in DnssecZone.get_corrupted_keys(origin):
            self._perform_key_operation("nameserver.deleteDnssec", {"id": key.get_key_id()}, str(key))
        print()
        return self

    def _perform_key_operation(self, method: str, params: dict, key: str) -> None:
        result = self.api.call_api(method, params)
        if result["code"] == 1000:
            print(f"{'OK':<8} {key}")
        else:
            print(f"{'ERROR':<8} {key}")
            print(f"{'':<8} [{result['code']}] {result['msg']}")

    def close(self) -> None:
        self.connector.close()
