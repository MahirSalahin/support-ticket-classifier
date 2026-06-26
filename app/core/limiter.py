from slowapi import Limiter
from slowapi.util import get_remote_address

# Use get_remote_address to rate limit based on the client's IP address.
# This uses in-memory storage by default, which is perfect for single-instance deployments.
limiter = Limiter(key_func=get_remote_address)
