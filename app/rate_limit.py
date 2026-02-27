"""Rate limiter singleton — importable from route modules without circular imports."""

from slowapi import Limiter

from app.utils import get_client_ip

limiter = Limiter(key_func=get_client_ip)
