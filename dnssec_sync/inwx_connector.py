from __future__ import annotations

import os
from typing import Any

from INWX.Domrobot import ApiClient

from .console import console


class InwxConnector:
    def __init__(self) -> None:
        self.api = self.connect()

    @staticmethod
    def connect() -> ApiClient:
        console.info("Connecting to INWX API")
        target = os.getenv("INWX_SYSTEM", "Live")
        api_url = ApiClient.API_OTE_URL if target == "Ote" else ApiClient.API_LIVE_URL
        debug = os.getenv("INWX_DEBUG", "0") in {"1", "true", "True"}
        api = ApiClient(api_url=api_url, debug_mode=debug)
        result = api.login(
            os.environ["INWX_API_USER"],
            os.environ["INWX_API_PASS"],
            shared_secret=(os.getenv("INWX_API_SECRET") or None),
        )
        if result["code"] != 1000:
            raise RuntimeError(f"INWX login failed [{result['code']}] {result['msg']}")
        console.success("INWX API Connected")
        return api

    def close(self) -> None:
        if self.api is not None:
            self.api.logout()
            console.info("INWX API Disconnected")
