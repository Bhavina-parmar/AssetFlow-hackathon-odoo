from __future__ import annotations

from dataclasses import dataclass

from api import ApiClient
from config import Settings
from helpers import log_info, log_success


@dataclass(slots=True)
class AuthContext:
    token: str
    user_id: int
    username: str
    role: str


class AuthService:
    def __init__(self, client: ApiClient, settings: Settings) -> None:
        self.client = client
        self.settings = settings

    def login_admin(self) -> AuthContext:
        log_info("Logging in with admin credentials via /api/auth/login/")
        payload = {
            "email": self.settings.admin_email,
            "password": self.settings.admin_password,
        }
        data = self.client.post("/api/auth/login/", json=payload, auth_required=False)

        token = str(data["token"])
        user = data["user"]

        context = AuthContext(
            token=token,
            user_id=int(user["id"]),
            username=str(user.get("username", "admin")),
            role=str(user.get("role", "UNKNOWN")),
        )

        self.client.set_token(token)
        log_success(f"Authenticated as {context.username} ({context.role})")
        return context
