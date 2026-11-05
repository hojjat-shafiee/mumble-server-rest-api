import os

# Ice connectivity
ICE_HOST_ADDRESS = os.environ.get("MURMUR_ICE_HOST", "localhost").strip()
ICE_HOST_PORT = os.environ.get("MURMUR_ICE_PORT", "6502").strip()
ICE_TIMEOUT = int(os.environ.get("MURMUR_ICE_TIMEOUT", "1000"))
ICE_HOST = f"Meta:tcp -h {ICE_HOST_ADDRESS} -p {ICE_HOST_PORT} -t {ICE_TIMEOUT}"
ICE_SECRET = os.environ.get("ICE_SECRET", "")
ICE_MESSAGE_SIZE = int(os.environ.get("ICE_MESSAGE_SIZE", "1024"))

# Security & Behavior
API_KEY = os.environ.get("API_KEY", "").strip()
MASK_PASSWORDS = os.environ.get("MASK_PASSWORDS", "true").lower() in ("true", "1", "yes")
ENVIRONMENT = os.environ.get("ENVIRONMENT", "production").strip()
