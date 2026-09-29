from datetime import datetime, timedelta, timezone

import jwt

from app.config import settings


class TokenService:

    def _create_token(
        self,
        user,
        token_type: str,
        expire_delta: timedelta,
    ) -> str:

        now = datetime.now(timezone.utc)

        payload = {
            "sub": str(user.id),
            "email": user.email,
            "type": token_type,
            "iat": now,
            "exp": now + expire_delta,
        }

        return jwt.encode(
            payload,
            settings.PRIVATE_KEY_PATH.read_text(),
            algorithm=settings.JWT_ALGORITHM,
        )

    def create_access_token(self, user) -> str:
        return self._create_token(
            user=user,
            token_type="access",
            expire_delta=timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            ),
        )

    def create_refresh_token(self, user) -> str:
        return self._create_token(
            user=user,
            token_type="refresh",
            expire_delta=timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            ),
        )
