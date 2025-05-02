from typing import Any, Dict


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
    
    __prefix__: str = ...
    __ttl__: int = ...
    ENABLE_CACHING: bool = True  # Default is ON; override per class if needed
    
    def __init__(self, inherited_params: Dict[str, Any] = None, _parent=None, redis_client=None):
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

        ...
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
        ...
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
        ...
    
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

        ...
    async def subkeys(self) -> None:
        """
        ## Retrieves a list of all Redis keys under this cluster's prefix.

        This is a non-destructive introspection method that scans Redis using the
        fully-resolved prefix to return all matching keys without modifying them.

        #### Returns:
            list[str]: A list of Redis keys matching this cluster's prefix pattern.
                    Returns an empty list if no matching keys are found.
        """
        ...
