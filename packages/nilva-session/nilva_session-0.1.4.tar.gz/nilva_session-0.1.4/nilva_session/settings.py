from datetime import timedelta

DEFAULT = {
    "TOKEN_SIZE": 20,
    "EXPIRE_AT": timedelta(days=1),
    "SESSION_CACHE_PREFIX": "user_session:",
    "SESSION_ID_CACHE_PREFIX": "user_session_by_id:",
    "SESSION_CACHE_TTL": 15 * 60,  # 15 minutes,
    "SESSION_ID_CLAIM": "session_id",
}
