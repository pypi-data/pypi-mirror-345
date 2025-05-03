### 🔑 Secure Key Handling (Secrets & Passwords)

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