from __future__ import annotations

import os
from typing import Any

from zeep import Client
from zeep.transports import Transport
from requests import Session
from requests.auth import HTTPBasicAuth

from .console import console


class ISPConnector:
    def __init__(self) -> None:
        console.info("Connecting to ISPConfig Remote API")
        uri = os.environ["ISPCONFIG_REMOTE_URI"]
        wsdl = uri if uri.endswith("?wsdl") else f"{uri}?wsdl"
        session = Session()
        self.client = Client(wsdl=wsdl, transport=Transport(session=session))
        self.session_id = self.client.service.login(
            os.environ["ISPCONFIG_REMOTE_USER"],
            os.environ["ISPCONFIG_REMOTE_PASS"],
        )
        console.success("ISPConfig Remote API connected")

    def logout(self) -> None:
        if getattr(self, "session_id", None):
            try:
                self.client.service.logout(self.session_id)
            finally:
                console.info("ISPConfig Remote API Disconnected")
