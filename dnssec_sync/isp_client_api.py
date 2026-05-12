from __future__ import annotations

from .isp_connector import ISPConnector


class ISPClientApi:
    _instance: "ISPClientApi | None" = None

    def __init__(self) -> None:
        self.connector = ISPConnector()

    @classmethod
    def instance(cls) -> "ISPClientApi":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_all(self):
        return self.connector.client.service.client_get_all(self.connector.session_id)
