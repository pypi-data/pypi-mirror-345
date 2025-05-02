
# This constant defines the number of keys to be deleted in each batch when the Cluster.clear() method is called
REDIS_DELETE_CHUNK_SIZE = 50

# This setting ensures that the Redis key prefixes in clusters begin with a placeholder.
ENFORCE_PREFIX_START_WITH_PLACEHOLDER = True  # Default to True

# This setting governs whether the Time-to-Live (TTL) for keys should be automatically renewed before they expire.
TTL_AUTO_RENEW = False  # Default to False


# Toggle verbose output for method dispatch internals
SHOW_METHOD_DISPATCH_LOGS = False # default is True

