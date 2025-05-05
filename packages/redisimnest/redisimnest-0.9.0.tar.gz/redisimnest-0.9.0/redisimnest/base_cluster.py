import inspect
import re
from typing import Any, Dict

from .utils.logging import format_clear_log_line

from .exceptions import MissingParameterError, ParameterValidationError

from .settings import REDIS_DELETE_CHUNK_SIZE, SHOW_METHOD_DISPATCH_LOGS
from .utils.misc import get_pretty_representation
from .utils.prefix import validate_prefix
from .utils.redis import scan_keys




# ==============______CLUSTER ACCESSOR______=========================================================================================== CLUSTER ACCESSOR
class ClusterAccessor:
    def __init__(self, cls):
        self.cls = cls

    def __get__(self, instance, owner):
        if instance is None:
            return self.cls
        
        instance.get_full_prefix()
        
        return BoundClusterFactory(instance, self.cls)
    def __repr__(self):
        return f"<ClusterAccessor for {self.cls.__name__}>"







# ==============______BOUDN CLUSTER FACTORY______=========================================================================================== BOUDN CLUSTER FACTORY
class BoundClusterFactory:
    def __init__(self, parent_instance, cluster_cls):
        self.parent = parent_instance
        self.cluster_cls = cluster_cls

    def __call__(self, *args, **kwargs):
        if not issubclass(self.cluster_cls, BaseCluster):
            self.cluster_cls = type(
                self.cluster_cls.__name__,
                (BaseCluster, self.cluster_cls),
                dict(self.cluster_cls.__dict__)
            )

        # Extract placeholder keys from __prefix__
        prefix_template = getattr(self.cluster_cls, "__prefix__", "")
        placeholder_keys = re.findall(r"\{(.*?)\}", prefix_template)

        # Map args to keys in order if kwargs not already provided
        for key, arg in zip(placeholder_keys, args):
            if key not in kwargs:
                kwargs[key] = arg

        return self.cluster_cls(
            inherited_params={**self.parent._inherited_params, **kwargs},
            _parent=self.parent
        )

    def __getattr__(self, name):
        return getattr(self(), name)
    
    def __getitem__(self, value):
        # Infer key name from __prefix__ placeholders
        prefix_template = getattr(self.cluster_cls, "__prefix__", "")
        placeholder_keys = re.findall(r"\{(.*?)\}", prefix_template)

        if not placeholder_keys:
            raise ValueError("No placeholders in prefix to apply item access")
        if len(placeholder_keys) > 1:
            raise ValueError(
                f"Cluster '{self.cluster_cls.__name__}' has multiple placeholders "
                f"({', '.join(placeholder_keys)}); use explicit keyword arguments instead."
            )

        return self.__call__(**{placeholder_keys[0]: value})
    def __repr__(self):
        cls_name = self.cluster_cls.__name__
        parent = repr(self.parent)
        return f"<BoundClusterFactory cluster='{cls_name}' parent={parent}>"

    






# ====================================================================================================
# ==============             BASE CLUSTER             ==============#
# ====================================================================================================
class BaseCluster:
    """
    A base class for managing Redis clusters with flexible prefix-based key 
    management, subcluster support, and runtime parameter inheritance.

    This class facilitates the creation of Redis clusters by:
    - Defining a customizable key prefix using the `__prefix__` attribute.
    - Allowing TTL (Time-to-Live) settings for keys, configurable at both 
        the cluster and key levels.
    - Validating parameter types through custom validators.
    - Supporting hierarchical subclusters for organized data management.
    - Efficiently caching the computed cluster prefix to reduce redundant calculations.
    - Providing utility methods to clear or fetch keys associated with the cluster.

    Attributes:
        __prefix__ (str): The prefix string applied to all keys within the cluster.
        __ttl__ (int or None): Default TTL (in seconds) applied to keys, or `None` for no expiration.
        ENABLE_CACHING (bool): Whether caching of computed prefixes is enabled (default is `True`).
        redis (Any): Redis client used to interact with the Redis server.
        _inherited_params (dict): Parameters inherited from the parent cluster.
        _parent (BaseCluster or None): The parent cluster, if this cluster is a subcluster.

    Methods:
        get_full_prefix(): Computes and returns the full prefix for the cluster, including parent prefixes.
        with_params(**params): Creates a new instance of the cluster with additional parameters.
        describe(): Returns a dictionary description of the cluster, including its prefix, parameters, subclusters, and keys.
        clear(): Deletes all keys under the cluster by scanning with the cluster prefix.
        subkeys(): Returns all keys under the cluster by scanning with the cluster prefix.
    """
    __prefix__ = "base"
    __ttl__ = None  # Optional TTL in seconds
    ENABLE_CACHING = True  # Default is ON; override per class if needed

    
    def __init__(self, redis_client=None, inherited_params: Dict[str, Any] = None, _parent=None):
        """
        Initializes a new instance of the BaseCluster class with the specified Redis client, inherited parameters, 
        and an optional parent cluster.

        This constructor sets up the cluster by applying validators to the provided parameters, 
        binding any subclusters, and collecting runtime information. It also assigns the Redis client 
        and prepares the cluster's representation for documentation.

        Args:
            redis_client (Any, optional): The Redis client to use for interacting with the Redis server. 
                                        If not provided, will use the Redis client from the parent cluster if available.
            inherited_params (dict, optional): A dictionary of parameters inherited from the parent cluster. 
                                            Defaults to an empty dictionary if not provided.
            _parent (BaseCluster, optional): The parent cluster, from which inherited parameters and Redis client 
                                            can be fetched. Defaults to `None`.

        Raises:
            ParameterValidationError: If any of the parameters fail validation based on the cluster's validators.

        Side Effects:
            - Applies parameter validators to ensure that inherited parameters meet required constraints.
            - Binds subclusters defined within the cluster's class.
            - Caches the cluster's documentation string by calling `get_pretty_representation()` on the description.
        """

        self._inherited_params = inherited_params or {}
        self._parent = _parent
        self._apply_validators()
        self._bind_subclusters()
        # self._collect_runtime_structure()

        self.__doc__ = get_pretty_representation(self.describe())
        self.redis = redis_client or getattr(_parent, "redis", None)

    def _apply_validators(self):
        validators = getattr(self.__class__, "__validators__", {})
        for key, validator in validators.items():
            if key in self._inherited_params:
                value = self._inherited_params[key]
                if not validator(value):
                    raise ParameterValidationError(
                        f"Validation failed for '{key}' with value '{value}' in cluster '{self.__class__.__name__}'"
                    ) from None
    def _bind_subclusters(self):
        for name, attr in self.__class__.__dict__.items():
            if inspect.isclass(attr):
                # Enforce that all subclusters declare __prefix__
                if not hasattr(attr, "__prefix__"):
                    raise ValueError(
                        f"Cluster '{attr.__name__}' must define a '__prefix__' attribute "
                        f"to be used as a subcluster of '{self.__class__.__name__}'"
                    )

                # Promote non-BaseCluster classes into BaseCluster subclasses
                if not issubclass(attr, BaseCluster):
                    attr = type(
                        attr.__name__,
                        (BaseCluster, attr),
                        dict(attr.__dict__)
                    )

                validate_prefix(attr.__prefix__, attr.__name__)
                setattr(self.__class__, name, ClusterAccessor(attr))

    def _collect_prefix_parts(self):
        parts = []
        required_keys = set()
        cluster = self

        while cluster:
            prefix_template = getattr(cluster.__class__, "__prefix__", "")
            keys = re.findall(r"\{(.*?)\}", prefix_template)
            required_keys.update(keys)
            try:
                parts.insert(0, prefix_template.format(**cluster._inherited_params))
            except KeyError:
                parts.insert(0, prefix_template)
            cluster = cluster._parent

        return parts, required_keys
    
    def _compute_full_prefix(self):
        parts = []
        required_keys = set()
        cluster = self

        while cluster:
            prefix_template = getattr(cluster.__class__, "__prefix__", "")
            keys = re.findall(r"\{(.*?)\}", prefix_template)
            required_keys.update(keys)

            try:
                # Ensure this line is awaited if it's making Redis calls or coroutines
                parts.insert(0, prefix_template.format(**cluster._inherited_params))
            except KeyError as e:
                missing_key = e.args[0]
                raise MissingParameterError(
                    f"Missing required param '{missing_key}' for prefix '{prefix_template}' "
                    f"in cluster '{cluster.__class__.__name__}'"
                ) from None

            cluster = cluster._parent

        return ":".join(p for p in parts if p)

    def get_full_prefix(self):
        """
        ## Computes and returns the fully-resolved Redis key prefix for this cluster instance.

        The full prefix is constructed by combining this cluster's `__prefix__` with 
        all inherited prefixes from parent clusters, using the provided parameter values.

        If `ENABLE_CACHING` is `True`, the result is cached for faster repeated access.

        ### Returns:
            str: The fully-resolved Redis prefix, ready to be used in key generation.
        
        ### Raises:
            MissingParameterError: If any required parameters are missing during resolution.
        """
        if self.ENABLE_CACHING:
            if not hasattr(self, "_cached_prefix"):
                self._cached_prefix = self._compute_full_prefix()
            return self._cached_prefix
        return self._compute_full_prefix()
    


    def with_params(self, **params):
        new_instance = self.__class__({**self._inherited_params, **params}, _parent=self._parent)
        # Clear cached prefix if it exists
        if hasattr(new_instance, "_cached_prefix"):
            del new_instance._cached_prefix
        return new_instance
    
    def describe(self):
        """
        ## Returns a structured summary of the cluster’s configuration.

        This method analyzes the current cluster class and instance to extract:
            - The raw `__prefix__` template.
            - Required prefix parameters and which are still missing.
            - Names of nested subclusters.
            - Names of defined keys.

        #### Returns:
            dict: A dictionary with the following fields:
                - `prefix` (str): The raw prefix template defined on the cluster.
                - `params` (List[str]): All parameter names required by the prefix.
                - `missing_params` (List[str]): Parameters that have not yet been provided.
                - `subclusters` (List[str]): Names of nested cluster classes.
                - `keys` (List[str]): Names of `Key` objects defined in the cluster.
        """
        prefix = getattr(self.__class__, "__prefix__", "")
        params = re.findall(r"\{(.*?)\}", prefix)
        missing = [p for p in params if p not in self._inherited_params]

        subclusters = []
        keys = []

        for name, value in self.__class__.__dict__.items():
            if name.startswith("__"):
                continue
            from .key import Key
            if isinstance(value, ClusterAccessor):
                subclusters.append(name)
            elif isinstance(value, Key):
                keys.append(name)

        return {
            "prefix": prefix,
            "params": params,
            "missing_params": missing,
            "subclusters": subclusters,
            "keys": keys
        }
    
    async def clear(self) -> None:
        """
        ## Deletes all Redis keys under this cluster's prefix.

        This method performs a scan operation using the fully resolved prefix to find
        all matching keys, then deletes them in chunks for safety and performance.
        It is useful for cleaning up data associated with a specific namespace.

        **Warning**: This operation is irreversible and may result in data loss if used
        improperly. Be especially cautious when calling this on high-level or root clusters.

        #### Returns:
            None
        """
        cluster_prefix = self.get_full_prefix() + '*'
        keys = await scan_keys(self.redis, cluster_prefix)

        total_keys = len(keys)
        chunks_count = (total_keys + REDIS_DELETE_CHUNK_SIZE - 1) // REDIS_DELETE_CHUNK_SIZE
        total_deleted = 0
        chunks = []

        for chunk_num, i in enumerate(range(0, total_keys, REDIS_DELETE_CHUNK_SIZE), start=1):
            chunk = keys[i:i + REDIS_DELETE_CHUNK_SIZE]
            deleted = await self.redis.delete(*chunk)
            total_deleted += deleted
            colored = format_clear_log_line(
                cluster_name=self.__class__.__name__,
                chunk_num=chunk_num,
                chunks_count=chunks_count,
                deleted=deleted,
                deletes_count=total_deleted,
                keys=chunk,
            )
            chunks.append(colored)

        if not chunks:
            colored = format_clear_log_line(
                cluster_name=self.__class__.__name__,
                chunk_num=0,
                chunks_count=0,
                deleted=0,
                deletes_count=0,
                keys=[],
            )
            chunks.append(colored)

        if SHOW_METHOD_DISPATCH_LOGS:
            print('\n'.join(chunks))
        
        return True
    
    async def subkeys(self) -> None:
        """
        ## Retrieves a list of all Redis keys under this cluster's prefix.

        This is a non-destructive introspection method that scans Redis using the
        fully-resolved prefix to return all matching keys without modifying them.

        #### Returns:
            list[str]: A list of Redis keys matching this cluster's prefix pattern.
                    Returns an empty list if no matching keys are found.
        """
        cluster_prefix = self.get_full_prefix() + '*'
        keys = await scan_keys(self.redis, cluster_prefix)
        
        return keys or []


    
    def __repr__(self):
        cls_name = self.__class__.__name__
        params = ", ".join(f"{k}={v}" for k, v in self._inherited_params.items())
        return f"<{cls_name}({params})>"

