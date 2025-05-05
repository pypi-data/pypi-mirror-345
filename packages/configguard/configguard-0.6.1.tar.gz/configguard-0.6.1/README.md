# ConfigGuard

[![PyPI version](https://img.shields.io/pypi/v/configguard.svg)](https://pypi.org/project/configguard/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/configguard.svg)](https://pypi.org/project/configguard/)
[![PyPI license](https://img.shields.io/pypi/l/configguard.svg)](https://github.com/ParisNeo/ConfigGuard/blob/main/LICENSE)
[![Downloads](https://static.pepy.tech/badge/configguard)](https://pepy.tech/project/configguard)
[![Documentation Status](https://img.shields.io/badge/docs-latest-blue.svg)](https://parisneo.github.io/ConfigGuard/)
<!-- [![Build Status](https://github.com/ParisNeo/ConfigGuard/actions/workflows/ci.yml/badge.svg)](https://github.com/ParisNeo/ConfigGuard/actions/workflows/ci.yml) Placeholder -->
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

**Stop fighting inconsistent, error-prone, and insecure configuration files!** 🚀

**ConfigGuard** transforms your Python application's configuration management from a potential source of bugs and security risks into a robust, reliable, and developer-friendly system. Moving beyond simple dictionaries or basic file parsing, ConfigGuard introduces a **schema-driven fortress** for your settings, offering unparalleled control and safety.

Leverage a comprehensive suite of features designed for modern applications:

*   Define strict **Type Safety** and complex **Validation Rules** (`min`, `max`, `options`, `nullable`).
*   Protect sensitive data effortlessly with built-in, handler-transparent **Encryption**.
*   Manage configuration changes across application updates with seamless **Versioning** (using standard `__version__` key) and automated **Migration** (with optional automatic file updates).
*   Choose your preferred **Storage Format** (JSON, YAML, TOML, SQLite included) without altering your core logic.
*   Organize complex configurations intuitively using **Nested Sections**.
*   Accommodate unpredictable structures with flexible **Dynamic Sections**.

**Why waste time debugging subtle configuration typos or managing insecure secrets manually?** ConfigGuard catches errors early, simplifies maintenance, and secures your sensitive data, allowing you to focus on building great features.

**Adopt ConfigGuard and configure with confidence!**

---

## ✨ Key Features

*   📝 **Schema-Driven:** Define your configuration's expected structure, types, defaults, and validation rules within a Python dictionary or a JSON file. This acts as the single source of truth, ensuring consistency and enabling static analysis benefits. Use the standard `__version__` key for robust version tracking, or override with the `instance_version` parameter during initialization.
*   <0xF0><0x9F><0xA7><0xB1> **Nested Configuration:** Structure complex settings logically using **sections**, defined directly within your schema (`"type": "section"`). Access nested settings intuitively through standard attribute or dictionary notation (e.g., `config.database.connection.pool_size`, `config['server']['ssl']['enabled']`).
*   <0xF0><0x9F><0x94><0x91> **Dynamic Sections:** Define sections with an empty schema (`"schema": {}`) to allow adding/removing arbitrary key-value pairs at runtime, bypassing schema validation for those items while still benefiting from saving, loading, and encryption.
*   🔒 **Built-in Encryption:** Secure sensitive configuration values transparently using Fernet symmetric encryption (requires `cryptography`). Encryption is handled automatically by the storage backend during save/load operations.
*   💾 **Multiple Backends:** Persist configurations in various formats (JSON, YAML, TOML, SQLite). ConfigGuard automatically detects the format based on the file extension.
*   🔄 **Versioning & Migration:** Embed a version string (e.g., `"1.2.0"`) using the standard `__version__` key or provide it via `instance_version`. ConfigGuard compares file version with instance version during `load()`, preventing loading of newer configurations and migrating older ones (merging existing values, applying new defaults, skipping removed items). Migration operates recursively through nested sections. **Optionally auto-save** the migrated configuration back to the file using `load(update_file=True)`.
*   <0xF0><0x9F><0x97><0x84>️ **Standardized Save/Export Keys:** Uses consistent keys for metadata:
    *   `__version__`: Holds the configuration version. Included in both `values` and `full` save modes.
    *   `__schema__`: Holds the schema definition. Included only in `mode='full'` saves and exports.
    *   `__settings__`: Holds the configuration values structure. Included only in `mode='full'` saves and exports.
*   <0xF0><0x9F><0x97><0x84>️ **Flexible Save Modes:** Control the granularity of saved data:
    *   `mode='values'` (default): Saves only the current configuration key-value pairs, prepended with the `__version__` key.
    *   `mode='full'`: Saves the complete state using standard keys: `__version__`, `__schema__`, and `__settings__`.
*   <0xF0><0x9F><0xA7><0xB1> **Supported Types:** Define settings with standard Python types: `str`, `int`, `float`, `bool`, `list`. Dynamic sections can store any JSON-serializable type.
*   🐍 **Intuitive Access:** Interact naturally via attribute (`config.section.setting`) or dictionary (`config['section']['setting']`) syntax. Retrieve schema details using `config.sc_section.sc_setting`. Use `section.get_schema_dict()` and `section.get_config_dict()` for section introspection.
*   ✔️ **Automatic Validation:** Validates values against schema rules on modification or load for standard settings. Dynamic section values bypass schema validation.
*   📤 **Easy Export/Import:**
    *   `export_schema_with_values()`: Get a snapshot using standard keys (`__version__`, `__schema__`, `__settings__`).
    *   `import_config(data, ignore_unknown=True)`: Update values from a dictionary, merging data, validating standard settings, and adding/updating dynamic keys. Ignores `__version__` key in input `data`.
*   🧩 **Extensible:** Implement custom `StorageHandler` classes for additional backends.

---

## 🤔 Why Choose ConfigGuard?

(Reasons remain largely the same, but updated phrasing for versioning/keys)

*   **Eliminate Runtime Config Errors:** Catch errors early with schema validation.
*   **Secure Your Secrets with Ease:** Integrated, transparent encryption.
*   **Future-Proof Your Application:** Versioning (`__version__`) allows confident schema updates. Migration handles older files, and `load(update_file=True)` can automatically bring them up-to-date.
*   **Improve Code Clarity and Maintainability:** Schemas act as self-documentation. Standard keys (`__version__`, `__schema__`, `__settings__`) provide predictable structure.
*   **Manage Complexity Effectively:** Organize settings with nested and dynamic sections.
*   **Increase Developer Productivity:** Reduces boilerplate for parsing, validation, defaults, and encryption.
*   **Gain Storage Freedom:** Switch backends (JSON, YAML, TOML, SQLite) easily.

---

## 🚀 Installation

(Installation instructions remain the same)

```bash
# Base
pip install configguard

# Extras (encryption, yaml, toml, all, dev)
pip install configguard[encryption]
pip install configguard[yaml]
pip install configguard[toml]
pip install configguard[all]

# For development
git clone https://github.com/ParisNeo/ConfigGuard.git
cd ConfigGuard
pip install -e .[dev]
```

---

## ⚡ Quick Start

```python
from configguard import ConfigGuard, ValidationError, generate_encryption_key
from pathlib import Path
import typing

# 1. Define schema with standard __version__ key
SCHEMA_VERSION = "1.1.0"
my_schema: typing.Dict[str, typing.Any] = {
    "__version__": SCHEMA_VERSION,
    # ... (rest of schema definition as before) ...
    "server": {
        "type": "section", "help": "Core web server settings.",
        "schema": {
            "host": { "type": "str", "default": "127.0.0.1", "help": "IP address to bind to." },
            "port": { "type": "int", "default": 8080, "min_val": 1024, "max_val": 65535, "help": "Port number." }
        }
    },
    "plugin_data": { "type": "section", "schema": {}, "help": "Dynamic data."}, # Dynamic
    "log_level": { "type": "str", "default": "INFO", "options": [...], "help": "Verbosity."}
}

# 2. Setup
config_file = Path("my_app_config.yaml")
encryption_key = generate_encryption_key()

# 3. Initialize (using schema version in this case)
try:
    config = ConfigGuard(
        schema=my_schema,
        config_path=config_file,
        encryption_key=encryption_key
    )
    print(f"Initialized with Version: {config.version}") # -> 1.1.0

# Handle missing dependencies
except ImportError as e: print(f"ERROR: Missing dependency for {config_file.suffix}: {e}"); exit()
except Exception as e: print(f"ERROR: Failed to initialize: {e}"); exit()

# 4. Access defaults
print(f"Initial Host: {config.server.host}") # -> '127.0.0.1'

# 5. Modify values
config.server.port = 9090
config.plugin_data['active'] = True # Dynamic add

# 6. Save configuration (values mode)
# This will save {'__version__': '1.1.0', 'server': {'host': ..., 'port': 9090}, ...}
config.save()
print(f"Config saved to {config_file} (encrypted, with version key).")

# To save full state (version, schema, settings) using standard keys:
# config.save(mode='full', filepath='my_app_config_full.yaml')

# 7. Load older version and auto-update file (Example)
# Assume 'old_config_v1.yaml' exists (saved with version 1.0.0)
# try:
#     print("\nLoading old config with auto-update...")
#     # Load V1 data into V1.1.0 instance, triggering migration and save
#     config_migrated = ConfigGuard(
#         schema=my_schema, # V1.1.0 schema
#         config_path="old_config_v1.yaml",
#         load_options={'update_file': True} # <--- Enable auto-save on migrate
#     )
#     # Now 'old_config_v1.yaml' should contain migrated data with '__version__': '1.1.0'
#     print(f"Loaded and potentially updated file. New instance version: {config_migrated.version}")
# except Exception as e:
#     print(f"Error during migration load: {e}")

```

---

## 📚 Core Concepts Detailed

*   **Schema:** Definition using Python dict or JSON.
    *   **Versioning:** Use `__version__` key in schema or `instance_version` parameter (priority). Standard `packaging` format. Defaults to `"0.0.0"`.
    *   **Standard Keys:** `__version__`, `__schema__`, `__settings__` used for save/export structure.
    *   **Sections & Dynamic Sections:** As before (`"type": "section"`, `"schema": {}`).
*   **ConfigGuard Object:** Main interaction point. Version set at init. Handles load/save/access.
*   **ConfigSection Object:** Represents nested sections. Access/modify contents. `get_schema_dict()`/`get_config_dict()`.
*   **Dynamic Sections:** Flexible key-value stores within the config.
*   **Storage Handlers:** Abstract persistence (JSON, YAML, TOML, SQLite built-in). Handle standard keys and encryption.
*   **Save Modes (`values` vs `full`):**
    *   `mode='values'`: Saves `__version__` + config values structure.
    *   `mode='full'`: Saves `__version__`, `__schema__`, `__settings__`.
*   **Versioning & Migration:** Compares instance vs file `__version__`. Migrates older files. `load(update_file=True)` saves migrated state back to file in `values` mode.
*   **Encryption:** Fernet-based, transparent via handlers.

---

## 📖 Detailed Usage

### 1. Defining the Schema

(Use `__version__` standard key)

```python
# Example schema definition (use __version__)
schema_v3 = {
    "__version__": "3.0.0",
    # ... rest of complex_schema definition ...
}
```

### 2. Initializing ConfigGuard

(Pass schema, path, key, optional `instance_version`, `load_options`)

```python
# Example init with auto-update on migration enabled
config = ConfigGuard(
    schema=schema_v3,
    config_path="app_v3.db",
    encryption_key=enc_key,
    load_options={'update_file': True} # Enable save on migrate
)
```

### 3. Accessing Settings and Schema

(Remains the same: `config.section.setting`, `config['section']['setting']`, `config.sc_section.sc_setting`)

### 4. Modifying Settings

(Remains the same: attribute/item assignment triggers validation)

### 5. Working with Sections: Introspection

(Remains the same: `section.get_schema_dict()`, `section.get_config_dict()`)

### 6. Saving & Loading

`save()` uses standard keys based on `mode`. `load()` detects standard/legacy keys and structure. `load(update_file=True)` triggers save after migration.

```python
# Save values (includes __version__)
config.save() # or config.save(mode='values')

# Save full state (__version__, __schema__, __settings__)
config.save(mode='full', filepath='backup.json')

# Load (will check standard keys first)
try:
    config.load() # Load from default path
    # Load older file and update it automatically
    config.load(filepath='old_config.toml', update_file=True)
except Exception as e:
    print(f"Load failed: {e}")
```

### 7. Versioning & Migration

(Mostly automatic. Use `load(update_file=True)` to persist migrated state).

### 8. Encryption

(Remains the same: provide key at init)

### 9. Handling Nested Configurations

(Remains the same: access follows structure)

### 10. Import/Export

`export_schema_with_values()` uses standard keys. `import_config()` ignores `__version__` in input data.

```python
# Export (uses __version__, __schema__, __settings__)
full_state = config.export_schema_with_values()
# print(json.dumps(full_state, indent=2))

# Import (input data should be value structure, __version__ ignored)
update_data = {
    "server": {"port": 8888},
    "__version__": "ignored", # This key is skipped on import
    # ... other values ...
}
config.import_config(update_data)
```

---

## 💡 Use Cases

(Use cases remain the same)

---

## 🔧 Advanced Topics

(Advanced topics remain the same, focusing on custom handlers and potential future features)

---

## 🤝 Contributing

(Contributing guidelines remain the same)

---

## 📜 License

(License remains the same: Apache 2.0)

---

<p align="center">
  Built with ❤️ by ParisNeo with the help of Gemini 2.5
</p>