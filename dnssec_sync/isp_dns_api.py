from __future__ import annotations

from .isp_connector import ISPConnector


class ISPDnsApi:
    _instance: "ISPDnsApi | None" = None

    def __init__(self) -> None:
        self.connector = ISPConnector()

    @classmethod
    def instance(cls) -> "ISPDnsApi":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_all_server_ids(self) -> list[str]:
        dnsserverids: list[str] = []
        for server in self.connector.client.service.server_get_all(self.connector.session_id):
            sid = server["server_id"]
            functions = self.connector.client.service.server_get_functions(self.connector.session_id, sid)
            if functions.get("dns_server") == "1":
                dnsserverids.append(sid)
        return dnsserverids

    def get_zone(self, zone_id):
        return self.connector.client.service.dns_zone_get(self.connector.session_id, zone_id)
