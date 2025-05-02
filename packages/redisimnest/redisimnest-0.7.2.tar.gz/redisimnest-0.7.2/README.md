# Redisimnest _(Redis Imaginary Nesting)_

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**_A sophisticated, prefix-based Redis key management system with customizable, nestable clusters, dynamic key types, and parameterized prefix resolution. It supports secure secret management and password handling, making it ideal for organizing application state and simplifying Redis interactions in complex systems._**



## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Detailed Information](#detailed-information)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)



## Features <a name="features"></a>

- **`Prefix-Based Cluster Management:`** _Organize Redis keys with flexible, dynamic prefixes._
- **`Support for Parameterized Keys:`** _Create keys with placeholders that can be dynamically replaced._
- **`TTL Management:`** _Automatic and manual control over key TTLs._
- **`Cluster Hierarchies:`** _Nested clusters with inherited parameters._
- **`Auto-Binding & Dynamic Access:`** _Smart access to nested clusters and runtime bindings._
- **`Command Dispatching:`** _Type-aware command routing with serialization/deserialization support._
- **`Secret Management:`** _Store and access sensitive information like API keys securely within the key._
- **`Password Handling:`** _Built-in support for managing and validating passwords as part of the key parameters._


## Installation <a name="installation"></a>

You can install Redisimnest via pip:

### Install via pip:
```bash
pip install redisimnest
```

### Install from source:
```bash
git clone https://github.com/yourusername/redisimnest.git
cd redisimnest
pip install .
```

## Usage <a name="usage"></a>

Here’s a basic example of how to use Redisimnest in your project:

```python
from asyncio import run
from redisimnest import BaseCluster, Key
from redisimnest.utils import RedisManager

# Define structured key clusters with dynamic TTL and parameterized keys
class App:
    __prefix__ = 'app'
    __ttl__ = 80  # TTL for keys within this cluster
    tokens = Key('tokens', default=[])
    pending_users = Key('pending_users')

class User:
    __prefix__ = 'user:{user_id}'  # Parameterized prefix for user-specific keys
    __ttl__ = 120  # TTL for user keys
    age = Key('age', 0)
    name = Key('name', "Unknown")

    password = Key('password', 'simple_pass', is_password=True)
    sensitive_data = Key('sensitive_data', None, is_secret=True)


class RootCluster(BaseCluster):
    __prefix__ = 'root'
    app = App
    user = User
    project_name = Key('project_name')

# Initialize the Redis client and root cluster
redis = RedisManager.get_client()
root = RootCluster(redis_client=redis)

# Async operation: Setting and getting keys
async def main():
    await root.project_name.set("RedisimNest")
    await root.user(1).age.set(30)
    print(await root.user(1).age.get())  # ➜ 30
    await root.app.tokens.set(["token1", "token2"])
    await root.app.tokens.expire(60)
    await root.app.clear()  # Clear all keys under the 'app' prefix

    the_type = await root.project_name.the_type # we don't have to call since it's property, but don't forget `await` expression
    assert the_type is str # the type of value was `string` (every value is serialized with metadata `__type__` under the hood)

    await root.project_name.delete()
    the_type = await root.project_name.the_type
    assert the_type is None # deleted keys have no type

    # PASSWORD: Set and verify correct password
    await user_key.password.set("hunter2")
    assert await user_key.password.verify_password("hunter2") is True

    # SECRET: Set and retrieve
    await user_key.sensitive_data.set("some top secret")
    val = await user_key.sensitive_data.get()
    assert val == "some top secret"



run(main())
```



## Detailed Information <a name="detailed-information"></a>

### Cluster and Key: Advanced Redis Management with Flexibility and Control

**Redisimnest** offers a sophisticated and elegant approach to managing Redis data with its core concepts of **Cluster** and **Key**. These components, designed with flexibility and fine-grained control in mind, enable you to organize, manage, and scale your Redis keys efficiently. This system also integrates key features like TTL drilling, parameterized prefixes, efficient clearing of cluster data, and robust secret and password management for secure handling of sensitive information.


### Cluster: Prefix-Based Grouping and Management

A **Cluster** in **Redisimnest** is a logical grouping of Redis keys that share a common **prefix**. The cluster's prefix acts as an identity for the keys within it, allowing them to be easily managed as a cohesive unit. Each cluster is self-contained and has several key attributes:

- **`__prefix__`**: Every cluster must have a unique prefix that distinguishes it from others. This prefix is fundamental to its identity and is used in the construction of all keys within the cluster.
- **`__ttl__`**: Optional Time-To-Live (TTL) setting at the cluster level. If a child cluster does not have its own TTL, it inherits the TTL from its parent cluster. However, if the child cluster has its own TTL, it takes precedence over the parent's TTL. This structure allows for flexible TTL management while ensuring that keys without a specified TTL default to the parent's TTL settings.
- **`get_full_prefix()`**: This method returns the complete Redis key prefix for the cluster. It resolves the prefix by concatenating the prefixes of all ancestor clusters, starting from the root cluster down to the current cluster. Additionally, it resolves and includes any parameters specific to the current cluster, ensuring that the final prefix is fully formed with all necessary contextual information.

- **`subkeys()`**: The `subkeys` method allows you to retrieve a list of keys that begin with the current cluster's full prefix. It uses Redis’s SCAN method to efficiently scan and identify all keys that match the current cluster's prefix, including any subkeys that are nested under the cluster. This ensures a comprehensive and performant way of discovering keys associated with the cluster and its parameters.

- **`clear()`**: The `clear` method is used to delete all keys within the cluster. **Warning**: Clearing a cluster will delete all data within it, and **Redisimnest** does **not** prevent accidental data loss. It is **highly recommended to use caution when invoking this method**, especially for clusters that are important or non-recoverable. **Redisimnest** does not enforce safety on clear operations, so be careful when clearing clusters, particularly the **root cluster**.

- **`describe()`**: Returns a structured summary of the cluster's internal structure. This includes the declared prefix, required parameters (and which are still missing), as well as all defined keys and nested subclusters. It’s useful for introspection, debugging, documentation generation, and tooling support. Unlike `clear()`, this method is completely safe to call and can be used to visualize or programmatically analyze cluster structure without touching any Redis data.



### Key: Parameterized, Flexible Redis Keys

Each **Key** in a cluster represents an individual Redis entry and follows the cluster’s prefix conventions. Keys can be parameterized, making them more flexible and dynamic. Here's how it works:

- **Parameterized Prefixes**: The prefix of a key is based on the cluster’s prefix, and can also accept dynamic parameters. For example, a key might have a structure like `user:{user_id}:session`, where the `{user_id}` is a placeholder that is replaced with the actual value when the key is created or accessed.
- **TTL Management**: Keys within a cluster inherit TTL settings from their parent cluster but can also have their own TTL, which takes precedence. The TTL behavior is further refined with **TTL drilling**, enabling you to set expiration policies at various levels (cluster, key) to fine-tune how long data persists in Redis.
- **Password Keys (`is_password=True`)**: Password keys automatically hash values using secure algorithms. You can set passwords, verify them without ever retrieving the raw hash, and optionally reveal the stored hash for debugging. Passwords are never stored or returned in plain text.
- **Secret Keys (`is_secret=True`)**: Secret keys store string data in encrypted form. Even the same value produces different ciphertexts on each set. Secrets can be retrieved normally with `.get()`, and you can inspect the raw encrypted value with `.raw()` if needed. Useful for storing API keys, private notes, or other sensitive information.


### Key Configuration Options

```python
Key(
    prefix_template="user:{user_id}:password",
    default=None,
    ttl=86400,
    ttl_auto_renew=True,
    is_secret=False,
    is_password=True
)
```

#### Parameters

- **`prefix_template`** (`str`):  
  Redis key pattern with named parameters (e.g., `"user:{user_id}:session"`).

- **`default`** (`Any`, optional):  
  Returned if the key doesn't exist in Redis. Not persisted.

- **`ttl`** (`int`, optional):  
  Per-key TTL in seconds. Overrides cluster TTL if defined.

- **`ttl_auto_renew`** (`bool`):  
  Automatically renews TTL on access. Defaults to `TTL_AUTO_RENEW`.

- **`is_secret`** (`bool`):  
  Encrypts the value at rest. Each `set()` generates a new ciphertext, even for identical input. Ideal for API keys, tokens, or personal data.

- **`is_password`** (`bool`):  
  Hashes and secures password values. Can only be checked with `.verify_password("candidate")`. Plain values are never returned from `.get()`.



### Key Usage Warnings

**Warning**: When defining clusters or keys with parameterized prefixes, ensure that parameters are passed **at the correct place**. 

- If a cluster’s prefix includes parameters (e.g., `'user:{user_id}'`), make sure to provide the required values for those parameters **when chaining to subclusters or keys**. Failure to do so will result in an error.
  
  **Example**:  
  ```python
  # Correct usage:
  await root.user(123).age.set(30)
  
  # Incorrect usage (will raise an error):
  await root.user.age.set(30)  # 'user:{user_id}' is missing the user_id parameter
  ```
  
- Similarly, for keys with parameterized prefixes, **always pass the necessary parameters when accessing them**. Omitting them will lead to an error.

  **Example**:  
  ```python
  # Correct usage:
  await root.user(123).name.set("John")
  
  # Incorrect usage (will raise an error):
  await root.user.name.set("John")  # Missing the required parameter 'user_id'
  ```

Always pass parameters as part of the chaining syntax to avoid errors and ensure correct key resolution.

### **Allowed Usage with `[]` Brackets**

You can use **`[]` brackets** for clusters or keys that require **only a single parameter**. This allows for a simplified, compact syntax when accessing parameters.

- **Allowed usage**: If a key or cluster requires just **one parameter**, you can pass it inside the brackets:

  **Example**:  
  ```python
  await root.user[123].name.set("John")
  ```

- **Forbidden usage**: **Multiple parameters cannot** be passed using `[]` syntax. If more than one parameter is required, use the regular chaining syntax to properly pass each one.

  **Example**:  
  ```python
  # Incorrect usage (raises an error):
  await root.user[123, 'extra_param'].name.set("John")
  
  # Correct usage:
  await root.user(123, 'extra_param').name.set("John")
  ```

Using `[]` is a convenient shorthand, but it’s important to remember it is limited to a **single parameter** only.



### 🔐 Secure Key Types: `is_password` and `is_secret`

The `Key` definition now supports two secure key types:

- `is_password=True`: for securely storing hashed passwords with verification.
- `is_secret=True`: for encrypting/decrypting sensitive strings using symmetric encryption.

Example usage:

```python
password = Key('password', 'user_pass', is_password=True)
sensitive_data = Key('sensitive_data', None, is_secret=True)
```

#### Password Behavior (`is_password=True`)

- Values are automatically hashed with a secure salt.
- Use `.verify_password("raw_input")` to check a candidate string.
- Accessing the raw value via `.get()` raises `AccessDeniedError`.
- Use `.get(reveal=True)` to retrieve the hashed value (if needed).
- Hashes change even for the same password input on re-set.

#### Secret Behavior (`is_secret=True`)

- Strings are encrypted with a unique key per value.
- Use `.get()` to retrieve the original string.
- Use `.raw()` to see the encrypted ciphertext (for testing/debug).
- Setting `None` is allowed.
- Same input encrypted multiple times will result in different ciphertext.

---

#### ✅ Example Test

```python
user_key = root.user(user_id=42)

# Password
await user_key.password.set("hunter2")
assert await user_key.password.verify_password("hunter2") is True
assert await user_key.password.verify_password("wrong") is False
await user_key.password.delete()
assert await user_key.password.verify_password("anything") is None

# Secret
await user_key.sensitive_data.set("top secret")
assert await user_key.sensitive_data.get() == "top secret"
await user_key.sensitive_data.set(None)
assert await user_key.sensitive_data.get() is None
```


In `redisimnest`, keys can optionally hold sensitive data such as passwords and secrets. The following packages are used for this functionality but are **lazily loaded**, meaning they are only imported when explicitly needed:

#### Required Packages

1. **`bcrypt`** (for password hashing)
   - **Purpose**: Used for securely hashing and verifying passwords.
   - **Installation**: 
     ```bash
     pip install bcrypt
     ```

2. **`cryptography`** (for secret encryption)
   - **Purpose**: Used for encrypting and decrypting sensitive data.
   - **Installation**:
     ```bash
     pip install cryptography
     ```

3. **`python-dotenv`** (for loading the encryption key)
   - **Purpose**: Loads the encryption key (`MY_ENCRYPTION_KEY`) from environment variables.
   - **Installation**:
     ```bash
     pip install python-dotenv
     ```

#### Lazy Loading

These dependencies are only loaded when you use a key with `is_secret=True` or `is_password=True`. If not needed, the system remains lightweight and does not require these packages.

#### Encryption Key

To use encryption for secrets, set the environment variable `MY_ENCRYPTION_KEY` with a generated key:

```bash
export MY_ENCRYPTION_KEY=<your-encryption-key>
```

This key is required for encrypting/decrypting sensitive data stored in keys marked as `is_secret=True`.



### Advanced Use Cases

- **Native deserialization with type detection** – When it's important to recover both the original value **and** its precise type.

  ``` python
  from redisimnest.utils import serialize, deserialize
  from datetime import datetime

  value = datetime.now()
  
  # Serialize with no type return
  raw = serialize(value)

  # Deserialize and recover the actual Python type
  value_type, restored_value = deserialize(raw, with_type=True)

  assert value_type is datetime
  assert restored_value == value
  ```

- **Get type as string** – Useful when storing or logging metadata, or for lightweight type comparison across systems.

  ``` python
  from redisimnest.utils import serialize, deserialize
  from uuid import UUID

  original = UUID("12345678-1234-5678-1234-567812345678")
  _, raw = serialize(original, with_type=True, with_type_str=True)

  # Deserialize and get the type as a string
  type_str, restored = deserialize(raw, with_type=True, with_type_str=True)

  assert type_str == "uuid"
  assert restored == original
  ```



### **Redisimnest allows you to customize the following settings:**

- `REDIS_HOST`: Redis server hostname (default: localhost).
- `REDIS_PORT`: Redis server port (default: 6379).
- `REDIS_USERNAME` / `REDIS_PASS`: Optional authentication credentials.
- `REDIS_DELETE_CHUNK_SIZE`: Number of items deleted per operation (default: 50).
- `SHOW_METHOD_DISPATCH_LOGS`: Toggle verbose output for method dispatch internals.

You can set these via environment variables or within your settings.py:
```python
import os

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DELETE_CHUNK_SIZE = 50
SHOW_METHOD_DISPATCH_LOGS = False # if you want to disable dispatch logs
```

To apply your custom settings file, add the following line to your `.env` file:

```bash
USER_SETTINGS_FILE=./your_settings.py
```

## Contributing <a name="contributing"> </a>

We welcome contributions! To contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Write tests for your changes.
5. Submit a pull request.

Please ensure all tests pass before submitting your PR.

## License <a name="license"></a>

This project is licensed under the MIT License - see the LICENSE file for details.

