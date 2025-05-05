from typing import Any, Awaitable, Optional, Union

from ..redisimnest.settings import TTL_AUTO_RENEW


class Key:
    def __init__(
        self, 
        prefix_template: str, 
        default: Optional[Any] = None,
        ttl: Optional[int] = None,
        ttl_auto_renew: bool = TTL_AUTO_RENEW,
        is_secret: bool = False,
        is_password: bool = False
    ):
        """
        Represents a terminal key in the Redis cluster hierarchy.

        A `Key` defines a fully-resolved Redis entry with a parameterized prefix, optional default value, 
        and fine-grained TTL control. It supports runtime substitution of prefix parameters, hierarchical TTL 
        inheritance, and key-level metadata.

        Parameters:
            prefix_template (str): 
                A string pattern for the Redis key prefix (e.g., "user:{user_id}:session"). 
                Parameters in `{}` must be supplied when resolving the key.

            default (Any, optional): 
                A fallback value returned when the key is not present in Redis.
                This value is not persisted; it's returned only when Redis returns `None`.

            ttl (int, optional): 
                Time-to-live in seconds. Overrides TTL set on any parent cluster.

            ttl_auto_renew (bool): 
                If True, the TTL will be renewed automatically on access. 
                Defaults to the global `TTL_AUTO_RENEW`.

            is_secret (bool): 
                If True, marks the key as sensitive (e.g., API keys). May be excluded from logs or debug output.

            is_password (bool): 
                If True, indicates that the key stores a password. May trigger extra validation or restrictions.

        Features:
            - **Parameterized prefixes**: Dynamic key paths with named placeholders.
            - **TTL management**: Supports TTL inheritance and override ("TTL drilling").
            - **Default fallback**: Soft fallback value for missing keys.
            - **Metadata flags**: Supports marking keys as secrets or passwords.

        Example:
            >>> Key("user:{user_id}:session", ttl=3600)
            # A user session key with a 1-hour TTL

            >>> Key("config:app", default={})
            # A static config key returning `{}` if not present
        """
        ...
    


    @property
    def key(self) -> str:
        """Returns the final, resolved key for this key instance."""
        ...
    @property
    async def the_type(self) -> type:
        """
        Returns the Python `type` object of the value stored at this key, if available.
        """
        ...
    @property
    def redis(self):
        """Access to redis client attached to base cluster"""
        ...

    @property
    def the_ttl(self):
        """Returns the current resolved ttl that is about to be applied"""
        ...
    def describe(self):
        """Returns key description as dict (name, prefix, params, key, ttl)"""
        ...
    async def verify_password(self, plain_password: str) -> bool:
        """Verifies given password with original"""
        ...
    async def raw(self):
        """Returns the data as is as stored in redis"""
        ...
    
    async def set(self, value, ex=None, px=None, nx=False, xx=False, keepttl=False, get=False, exat=None, pxat=None) -> Union[Awaitable[Any], Any]:
        """Set the value of a key."""
        ...
    async def get(self, reveal: bool=False, *args, **kwargs) -> Union[Awaitable[Any], Any]:
        """Get the value of a key."""
        ...
    async def exists(self) -> Union[Awaitable, Any]:
        """Check if a key exists."""
        ...
    async def expire(self, time, nx=False, xx=False, gt=False, lt=False) -> Union[Awaitable, Any]:
        """Set a timeout on a key in seconds."""
        ...
    async def pexpire(self, time, nx=False, xx=False, gt=False, lt=False) -> Union[Awaitable[Any], Any]:
        """Set a timeout on a key in milliseconds."""
        ...
    async def expireat(self, when, nx=False, xx=False, gt=False, lt=False) -> Union[Awaitable, Any]:
        """Set a key to expire at a specific Unix time (seconds)."""
        ...
    async def pexpireat(self, when, nx=False, xx=False, gt=False, lt=False) -> Union[Awaitable[Any], Any]:
        """Set a key to expire at a specific Unix time (milliseconds)."""
        ...
    async def persist(self) -> Union[Awaitable[Any], Any]:
        """Remove the existing timeout from a key."""
        ...
    async def ttl(self) -> Union[Awaitable[Any], Any]:
        """Get the remaining time to live of a key in seconds."""
        ...
    async def pttl(self) -> Union[Awaitable[Any], Any]:
        """Get the remaining time to live of a key in milliseconds."""
        ...
    async def expiretime(self) -> Union[Awaitable, Any]:
        """Returns the absolute Unix timestamp (since January 1, 1970) in seconds at which the given key will expire"""
        ...
    async def type(self) -> Union[Awaitable[Any], Any]:
        """Return the data type of the value stored at key."""
        ...
    async def memory_usage(self, samples: int=None) -> Union[Awaitable, Any]:
        """Estimate the memory usage of a key in bytes."""
        ...
    async def touch(self) -> Union[Awaitable, Any]:
        """Alters the last access time of a key."""
        ...
    async def unlink(self) -> Union[Awaitable, Any]:
        """Asynchronously delete a key (non-blocking DEL)."""
        ...
    async def delete(self) -> Union[Awaitable, Any]:
        """Deletes the current key itself"""
    ...
