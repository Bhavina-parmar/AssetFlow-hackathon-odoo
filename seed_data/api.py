from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests

from config import Settings
from helpers import RetryConfig, retryable


class ApiError(RuntimeError):
    pass


@dataclass(slots=True)
class ApiResponse:
    status_code: int
    data: Any


class ApiClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.token: str | None = None
        self.call_count = 0

    def set_token(self, token: str) -> None:
        self.token = token
        self.session.headers.update({"Authorization": f"Token {token}"})

    def _build_url(self, path: str) -> str:
        if not path.startswith("/"):
            path = f"/{path}"
        return f"{self.settings.base_url}{path}"

    @retryable(RetryConfig(attempts=4, base_delay=0.4, max_delay=4.0, jitter=0.3))
    def request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | list[Any] | None = None,
        params: dict[str, Any] | None = None,
        expected_status: tuple[int, ...] = (200, 201),
        auth_required: bool = True,
    ) -> Any:
        if auth_required and not self.token:
            raise ApiError("Request requires auth token, but no token is set.")

        url = self._build_url(path)
        self.call_count += 1

        try:
            response = self.session.request(
                method=method.upper(),
                url=url,
                json=json,
                params=params,
                timeout=self.settings.timeout_seconds,
                verify=self.settings.verify_ssl,
            )
        except requests.RequestException as exc:
            raise ApiError(f"Network error calling {method} {path}: {exc}") from exc

        if response.status_code not in expected_status:
            body = response.text.strip()
            raise ApiError(
                f"{method.upper()} {path} failed with {response.status_code}. "
                f"Expected {expected_status}. Response: {body}"
            )

        if not response.content:
            return {}

        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type:
            return response.json()

        return response.text

    def get(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        expected_status: tuple[int, ...] = (200,),
        auth_required: bool = True,
    ) -> Any:
        return self.request(
            "GET",
            path,
            params=params,
            expected_status=expected_status,
            auth_required=auth_required,
        )

    def post(
        self,
        path: str,
        *,
        json: dict[str, Any] | list[Any] | None = None,
        expected_status: tuple[int, ...] = (200, 201),
        auth_required: bool = True,
    ) -> Any:
        return self.request(
            "POST",
            path,
            json=json,
            expected_status=expected_status,
            auth_required=auth_required,
        )

    def patch(
        self,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        expected_status: tuple[int, ...] = (200, 202),
        auth_required: bool = True,
    ) -> Any:
        return self.request(
            "PATCH",
            path,
            json=json,
            expected_status=expected_status,
            auth_required=auth_required,
        )
