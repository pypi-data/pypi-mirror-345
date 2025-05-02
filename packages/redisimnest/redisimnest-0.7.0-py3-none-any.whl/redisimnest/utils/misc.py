import importlib
import os
from typing import Literal

from ..exceptions import MissingDependencyError, MissingEncryptionKeyError








DAY = 86400


# ==============______GET PRETTY RESPRESENTATION______=========================================================================================== GET PRETTY RESPRESENTATION
def get_pretty_representation(desc: dict) -> str:
    """Returns json dumped text of given dict"""
    import json

    return json.dumps(desc, indent=4, ensure_ascii=False)




# ==============______LAZY IMPORT______=========================================================================================== LAZY IMPORT
def lazy_import(name: Literal['bcrypt', 'cryptography']):
    try:
        return importlib.import_module(name)
    except ImportError as e:
        if name == 'bcrypt':
            raise MissingDependencyError(
                "Password hashing requires the 'bcrypt' package. "
                "Install it with: pip install redisimnest[bcrypt]"
            ) from e
        
        elif name == 'cryptography':
            raise MissingDependencyError(
                "Fernet encryption requires the 'cryptography' package. "
                "Install it with: pip install redisimnest[crypto]"
            ) from e
        
        raise MissingDependencyError(f"Optional dependency '{name}' not installed.") from e




# ==============______GET ENCRYPTION KEY______=========================================================================================== GET ENCRYPTION KEY
def get_encryption_key():
    from dotenv import load_dotenv
    load_dotenv()  # this loads variables from .env into os.environ
    ENCRYPTION_KEY = os.getenv("MY_ENCRYPTION_KEY", None)
    if not ENCRYPTION_KEY:
        raise MissingEncryptionKeyError(
            "Missing required environment variable 'MY_ENCRYPTION_KEY'.\n\n"
            "This key is required for encryption features to work.\n"
            "You can generate one using Python:\n\n"
            "    from cryptography.fernet import Fernet\n"
            "    print(Fernet.generate_key().decode())\n\n"
            "Then set it in your shell:\n"
            "    export MY_ENCRYPTION_KEY='your-generated-key'\n"
        )
    return ENCRYPTION_KEY.encode()  # Ensure it's bytes for Fernet
