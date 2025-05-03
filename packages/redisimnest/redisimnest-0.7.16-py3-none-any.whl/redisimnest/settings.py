import os

# Default Redis Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_USERNAME = os.getenv("REDIS_USERNAME")
REDIS_PASS = os.getenv("REDIS_PASS")

# Custom settings for the package
REDIS_DELETE_CHUNK_SIZE = 50
ENFORCE_PREFIX_START_WITH_PLACEHOLDER = True  # Default to True
TTL_AUTO_RENEW = False  # Default to False
SHOW_METHOD_DISPATCH_LOGS = True  # Default to False

# Optionally load additional settings from a user-defined file
USER_SETTINGS_FILE = os.getenv("USER_SETTINGS_FILE")

if USER_SETTINGS_FILE and os.path.exists(USER_SETTINGS_FILE):
    # Load user settings file, assuming it’s a Python file
    user_settings = {}
    try:
        with open(USER_SETTINGS_FILE) as file:
            exec(file.read(), user_settings)
        globals().update(user_settings)
    except Exception as e:
        print(f"Error loading user settings from {USER_SETTINGS_FILE}: {e}")
