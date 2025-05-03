import json
from typing import Any, Awaitable, Optional, Union
import re
from .exceptions import AccessDeniedError, MissingParameterError

from .utils.de_serialization import SERIALIZED_TYPE_MAP, deserialize, serialize
from .utils.logging import with_logging
from .utils.misc import get_encryption_key, get_pretty_representation, lazy_import
from .utils.prefix import validate_prefix
from .settings import TTL_AUTO_RENEW
import copy





# ====================================================================================================
# ==============             KEY ARGUMENT PASSING             ==============#
# ====================================================================================================
class KeyArgumentPassing:
    """Handles single and multi param passing to format prefix."""

    def __call__(self, *args, **kwargs):
        """Support positional and keyword arguments to bind parameters."""
        # Combine positional arguments into kwargs using placeholder keys
        for key, arg in zip(self._placeholder_keys, args):
            if key not in kwargs:
                kwargs[key] = arg

        # Validate all placeholders are present
        missing = [k for k in self._placeholder_keys if k not in kwargs]
        if missing:
            raise MissingParameterError(
                f"Missing required param(s) {missing} for key prefix '{self.prefix_template}'"
            )

        # Create a new bound key instance
        bound_key = self._copy()
        bound_key._resolved_args = kwargs
        bound_key._parent = getattr(self, "_parent", None)  # Preserve parent if present
        return bound_key

    def __getitem__(self, value):
        """Support shorthand syntax for single-parameter keys."""
        if len(self._placeholder_keys) != 1:
            raise ValueError(
                f"Key with multiple placeholders ({', '.join(self._placeholder_keys)}) "
                "cannot be used with [] syntax. Use .__call__(...) instead."
            )
        return self(**{self._placeholder_keys[0]: value})




# ====================================================================================================
# ==============             METHODS             ==============#
# ====================================================================================================
class RedisMethodMixin:
    @with_logging
    async def set(self, value, ex=None, px=None, nx=False, xx=False, keepttl=False, get=False, exat=None, pxat=None) -> Union[Awaitable[Any], Any]:
        """Set the value of a key."""
        val = self._resolve_value(value)
        val = serialize(val)
        
        if self.the_ttl is not None:
            ex = ex or self.the_ttl
        
        return await self._parent.redis.set(self.key, val, ex, px, nx, xx, keepttl, get, exat, pxat)


    @with_logging
    async def get(self, reveal: bool = False) -> Union[Awaitable[Any], Any]:
        """Get the value of a key, with decryption and auto-TTL renewal if applicable."""
        if self.is_password:
            Warning("Passwords cannot be accessed directly. Use `verify_password` instead.")
        get = self._parent.redis.get
        key = self.key
        the_ttl = self.the_ttl

        raw = await get(key)
        plain_raw = await self.raw()

        print(f"{raw=} {plain_raw=}")
        assert raw == plain_raw, "Result mismatch for raw() and get()"

        result = copy.deepcopy(raw)
        del raw, get

        if result is None:
            if self.default_value is not None:
                return self.default_value
            return None

        result = deserialize(result)

        if result is None:
            return None

        if self.is_secret:
            try:
                ENCRYPTION_KEY = get_encryption_key()
                fernet = lazy_import('cryptography').fernet.Fernet(ENCRYPTION_KEY)
                result = fernet.decrypt(result.encode()).decode()
            except Exception as e:
                print(f"[redisimnest] Decryption failed: {e}")
                return "[decryption-error]"

        if self.is_password:
            if reveal:
                return result
            raise AccessDeniedError("To access secrets, set ALLOW_SECRET_ACCESS=1.")

        if self.ttl_auto_renew and the_ttl is not None:
            await self._parent.redis.expire(key, the_ttl)
        print(f'{result=}')
        return result

    
    @with_logging
    async def exists(self) -> Union[Awaitable, Any]:
        """Check if a key exists."""

        return await self._parent.redis.exists(self.key)

    @with_logging
    async def expire(self, time, nx=False, xx=False, gt=False, lt=False) -> Union[Awaitable, Any]:
        """Set a timeout on a key in seconds."""

        return await self._parent.redis.expire(self.key, time, nx, xx, gt, lt)

    @with_logging
    async def pexpire(self, time, nx=False, xx=False, gt=False, lt=False) -> Union[Awaitable[Any], Any]:
        """Set a timeout on a key in milliseconds."""
        return await self._parent.redis.pexpire(self.key, time, nx, xx, gt, lt)

    @with_logging
    async def expireat(self, when, nx=False, xx=False, gt=False, lt=False) -> Union[Awaitable, Any]:
        """Set a key to expire at a specific Unix time (seconds)."""

        return await self._parent.redis.expireat(self.key, when, nx, xx, gt, lt)

    @with_logging
    async def pexpireat(self, when, nx=False, xx=False, gt=False, lt=False) -> Union[Awaitable[Any], Any]:
        """Set a key to expire at a specific Unix time (milliseconds)."""

        return await self._parent.redis.pexpireat(self.key, when, nx, xx, gt, lt)

    @with_logging
    async def persist(self) -> Union[Awaitable[Any], Any]:
        """Remove the existing timeout from a key."""

        return await self._parent.redis.persist(self.key)

    @with_logging
    async def ttl(self) -> Union[Awaitable[Any], Any]:
        """Get the remaining time to live of a key in seconds."""

        return await self._parent.redis.ttl(self.key)

    @with_logging
    async def pttl(self) -> Union[Awaitable[Any], Any]:
        """Get the remaining time to live of a key in milliseconds."""

        return await self._parent.redis.pttl(self.key)

    @with_logging
    async def expiretime(self) -> Union[Awaitable, Any]:
        """Returns the absolute Unix timestamp (since January 1, 1970) in seconds at which the given key will expire"""

        return await self._parent.redis.expiretime(self.key)

    @with_logging
    async def type(self) -> Union[Awaitable[Any], Any]:
        """Return the data type of the value stored at key."""

        return await self._parent.redis.type(self.key)

    @with_logging
    async def memory_usage(self, samples: int=None) -> Union[Awaitable, Any]:
        """Estimate the memory usage of a key in bytes."""

        return await self._parent.redis.memory_usage(self.key, samples)

    @with_logging
    async def touch(self) -> Union[Awaitable, Any]:
        """Alters the last access time of a key."""

        return await self._parent.redis.touch(self.key)

    @with_logging
    async def unlink(self) -> Union[Awaitable, Any]:
        """Asynchronously delete a key (non-blocking DEL)."""

        return await self._parent.redis.unlink(self.key)
    
    @with_logging
    async def delete(self) -> Union[Awaitable, Any]:
        """Deletes the current key itself"""
        return await self._parent.redis.delete(self.key)

# ============================================================================================================================================
# ============================================================================================================================================
# ===========================                         BASE KEY                         ===========================#
# ============================================================================================================================================
# ============================================================================================================================================
class Key(KeyArgumentPassing, RedisMethodMixin):
    def __init__(
        self, 
        prefix_template: str, 
        default_value: Optional[Any] = None,
        ttl: Optional[int] = None,
        ttl_auto_renew: bool = TTL_AUTO_RENEW,
        is_secret: bool = False,
        is_password: bool = False
    ):
        self.prefix_template = prefix_template
        self.default_value = default_value
        self._own_ttl = ttl  # Changed from self.ttl
        self._placeholder_keys = re.findall(r"\{(.*?)\}", prefix_template) if prefix_template else []
        self.ttl_auto_renew = ttl_auto_renew

        if is_secret and is_password:
            raise ValueError(
                "A Key cannot be both 'secret' and 'password'. "
                "'is_secret' is for generic sensitive data, while 'is_password' implies credentials. "
                "Choose only one."
            )
        self.is_secret = is_secret
        self.is_password = is_password

    def _resolve_ttl(self):
        # Key-level TTL
        if getattr(self, '_own_ttl', None) is not None:
            return self._own_ttl

        # Subcluster → parent TTLs
        cluster = self._parent
        while cluster:
            ttl = getattr(cluster.__class__, '__ttl__', None)
            if ttl is not None:
                return ttl
            cluster = cluster._parent

        return None  # No TTL found
    
    async def raw(self):
        """Returns the data as is as stored in redis"""
        return await self._parent.redis.get(self.key)

    
    @property
    def key(self) -> str:
        """Returns the final, resolved key for this key instance."""
        if self._placeholder_keys:
            if not hasattr(self, "_resolved_args"):
                raise MissingParameterError(
                    f"Key '{self._name}' was accessed without required params: {self._placeholder_keys}"
                )
            formatted_key = self.prefix_template.format(**self._resolved_args)
            return f"{self._parent.get_full_prefix()}:{formatted_key}"
        else:
            return f"{self._parent.get_full_prefix()}:{self.prefix_template}"
    
    @property
    async def the_type(self):
        """
        Returns the Python `type` object of the value stored at this key, if available.
        """
        the_key = self.key
        raw_value = await self._parent.redis.get(the_key)

        if raw_value is None:
            return None  # No value present at key

        try:
            if isinstance(raw_value, bytes):
                raw_value = raw_value.decode()
            data = json.loads(raw_value)

            if isinstance(data, dict) and "__type__" in data:
                return SERIALIZED_TYPE_MAP.get(data["__type__"], None)
        except Exception:
            pass  # Not serialized with our method

    @property
    def redis(self):
        """Access to redis client attached to base cluster"""
        return self._parent.redis
    
    async def verify_password(self, plain_password: str) -> bool:
        """Verifies given password with original"""
        if not self.is_password:
            raise TypeError("This key does not store a password hash.")
        
        hashed = await self._parent.redis.get(self.key)
        if not hashed:
            return None
        
        deserialized = deserialize(hashed)

        if not isinstance(deserialized, str):
            return False

        try:
            bcrypt = lazy_import('bcrypt')
            return bcrypt.checkpw(plain_password.encode(), deserialized.encode())
        except Exception:
            return False


    @property
    def the_ttl(self):
        """Returns the current resolved ttl that is about to be applied"""
        return self._resolve_ttl()
    
    def _resolve_value(self, payload):
        if not self.is_secret and not self.is_password:
            return payload
        
        if payload is None:
            return None
        
        if not isinstance(payload, str):
            raise TypeError("Passwords and secrets must be strings.")
        
        if self.is_secret and isinstance(payload, str) and payload.startswith("gAAAA"):
            return payload  # already encrypted

        if self.is_password and isinstance(payload, str) and payload.startswith("$2b$"):
            return payload  # already hashed

        if self.is_password:
            bcrypt = lazy_import('bcrypt')
            payload = bcrypt.hashpw(payload.encode(), bcrypt.gensalt()).decode()
        elif self.is_secret:
            ENCRYPTION_KEY = get_encryption_key()
            fernet = lazy_import('cryptography.fernet').Fernet(ENCRYPTION_KEY)

            payload = fernet.encrypt(payload.encode()).decode()
        return payload


    def __set_name__(self, owner, name: str):
        self._name = name

    
    def __get__(self, instance, owner):
        # if instance is None:
        #     return self

        bound_key = self._copy()
        bound_key._parent = instance
        validate_prefix(bound_key.prefix_template, instance.__class__.__name__)
        return bound_key

    def _copy(self):
        new = self.__class__(
            prefix_template=self.prefix_template,
            default_value=self.default_value,
            ttl=self._own_ttl,
            ttl_auto_renew=self.ttl_auto_renew,
            is_secret=self.is_secret,
            is_password=self.is_password
        )
        new._name = getattr(self, '_name', None)
        return new

    
    def describe(self):
        """Returns key description as dict (name, prefix, params, key, ttl)"""
        return {
            "name": self._name,
            "prefix": self.prefix_template,
            "params": self._placeholder_keys,
            "key": self.key,
            "ttl": self.the_ttl,
            "is_secret": self.is_secret,
            "is_password": self.is_password
        }

    @property
    def __doc__(self):
        return get_pretty_representation(self.describe())
    
    def __repr__(self):
        tag = ' (secret)' if self.is_secret else ' (password)' if self.is_password else ''
        return f"<Key(name='{self._name}' template='{self.prefix_template}'){tag}>"



