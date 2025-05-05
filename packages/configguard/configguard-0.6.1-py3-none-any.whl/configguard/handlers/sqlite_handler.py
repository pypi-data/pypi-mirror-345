# -*- coding: utf-8 -*-
# Project: ConfigGuard
# File: configguard/handlers/sqlite_handler.py
# Author: ParisNeo with Gemini 2.5
# Date: 2025-05-04 (Updated for standard keys)
# Description: Concrete implementation of StorageHandler for SQLite database format.
#              Uses a simple key-value table, storing values as potentially encrypted
#              JSON strings. Handles nested structures via dot notation keys.
#              Uses standard keys like __configguard_version__, __configguard_schema__.

import base64
import json
import sqlite3
import typing
from collections.abc import Mapping
from pathlib import Path

from ..exceptions import EncryptionError, HandlerError
from ..log import log
from .base import LoadResult, StorageHandler

# # Define special keys used in the database for full mode (now passed via payload)
# VERSION_DB_KEY = "__configguard_version__" # Use payload['__version_key__'] instead
# SCHEMA_DB_KEY = "__configguard_schema__"   # Use payload['__schema_key__'] instead


class SqliteHandler(StorageHandler):
    """
    Handles loading and saving configuration data to an SQLite database file.

    Uses a simple key-value table (`config`) where keys represent the setting path
    (using dot notation for nesting) or standard metadata keys (`__version__`, `__schema__`).
    Values are stored as potentially encrypted JSON strings.

    Supports both 'values' and 'full' save modes. In 'full' mode, version and schema
    are stored under standard keys. In 'values' mode, only the version and config values
    are stored.
    """

    # __init__ is inherited, takes optional fernet

    def _connect(self, filepath: Path) -> sqlite3.Connection:
        """Establish SQLite connection and ensure table exists."""
        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(filepath, isolation_level=None) # Autocommit
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS config (
                    key TEXT PRIMARY KEY,
                    value BLOB
                )
                """
            )
            log.debug(f"SqliteHandler: Connected to DB and ensured 'config' table exists: {filepath}")
            return conn
        except sqlite3.Error as e:
            raise HandlerError(f"Failed to connect to or setup SQLite DB {filepath}: {e}") from e

    def _flatten_dict(
        self, nested_dict: Mapping, parent_key: str = "", sep: str = "."
    ) -> typing.Dict[str, typing.Any]:
        """Flattens a nested dictionary into a single level with dot-separated keys."""
        items = {}
        for k, v in nested_dict.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, Mapping):
                items.update(self._flatten_dict(v, new_key, sep=sep))
            else:
                items[new_key] = v
        return items

    def _unflatten_dict(
        self, flat_dict: typing.Dict[str, typing.Any], sep: str = "."
    ) -> dict:
        """Reconstructs a nested dictionary from a flat dictionary with dot-separated keys."""
        unflattened = {}
        for k, v in flat_dict.items():
            parts = k.split(sep)
            d = unflattened
            for i, part in enumerate(parts[:-1]):
                if part not in d:
                    d[part] = {}
                if not isinstance(d[part], dict):
                     log.warning(f"SqliteHandler: Key conflict during unflattening. Key '{part}' used as section path conflicts with existing value. Overwriting with section structure.")
                     d[part] = {}
                d = d[part]
            final_key = parts[-1]
            if final_key in d and isinstance(d[final_key], dict):
                 log.warning(f"SqliteHandler: Key conflict during unflattening. Key '{final_key}' conflicts with section path. Overwriting section with value.")
            d[final_key] = v
        return unflattened

    def load(self, filepath: Path) -> LoadResult:
        """
        Loads configuration from an SQLite database file, handling standard keys.

        Reads the key-value pairs, decrypts values if necessary, parses the
        JSON value strings, and reconstructs the nested configuration structure.
        Checks for standard keys (`__version__`, `__schema__`) to determine structure.

        Args:
            filepath: The Path object pointing to the SQLite database file.

        Returns:
            A LoadResult dictionary containing 'version', 'schema', and 'values'.

        Raises:
            FileNotFoundError: If the file does not exist.
            HandlerError: If database connection, reading, JSON parsing fails, or structure is invalid.
            EncryptionError: If decryption fails.
        """
        log.debug(f"SqliteHandler: Attempting to load from: {filepath}")
        if not filepath.exists():
            log.warning(f"SQLite file not found: {filepath}. Returning empty values.")
            return {"version": None, "schema": None, "values": {}}

        conn: typing.Optional[sqlite3.Connection] = None
        try:
            conn = self._connect(filepath)
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM config")
            rows = cursor.fetchall()

            # Use standard keys (these should ideally be passed from ConfigGuard, but hardcoded as fallback)
            VERSION_KEY = "__version__"
            SCHEMA_KEY = "__schema__"
            # VALUES_KEY = "__settings__" # Not directly used for loading structure here

            loaded_version: typing.Optional[str] = None
            loaded_schema_str: typing.Optional[str] = None # Store raw JSON string for schema
            flat_values: typing.Dict[str, typing.Any] = {}

            for key, value_blob in rows:
                try:
                    # Decrypt blob if needed
                    decrypted_bytes: bytes
                    if self._fernet:
                        if not value_blob: continue # Skip NULL blobs
                        decrypted_bytes = self._decrypt(value_blob)
                    else:
                        decrypted_bytes = value_blob if value_blob is not None else b'null'

                    # Decode UTF-8 and parse JSON value string
                    value_str = decrypted_bytes.decode("utf-8")
                    parsed_value = json.loads(value_str)

                    # Check for standard metadata keys
                    if key == VERSION_KEY:
                        if isinstance(parsed_value, str):
                            loaded_version = parsed_value
                        else:
                            log.warning(f"SqliteHandler: Invalid type for version key '{VERSION_KEY}'. Expected string, got {type(parsed_value).__name__}.")
                    elif key == SCHEMA_KEY:
                         # Only store the raw schema string if it represents a dict
                         if isinstance(parsed_value, dict):
                              loaded_schema_str = value_str # Store the valid JSON string
                         else:
                              log.warning(f"SqliteHandler: Invalid type for schema key '{SCHEMA_KEY}'. Expected JSON object, got {type(parsed_value).__name__}.")
                    else:
                        # Regular configuration key
                        flat_values[key] = parsed_value

                except UnicodeDecodeError as e:
                    raise HandlerError(f"Invalid UTF-8 data in DB for key '{key}'.") from e
                except json.JSONDecodeError as e:
                    raise HandlerError(f"Invalid JSON data in DB for key '{key}'.") from e
                except EncryptionError as e:
                    raise EncryptionError(f"Decryption failed for key '{key}' in DB.") from e
                except Exception as e:
                     raise HandlerError(f"Unexpected error processing key '{key}' from DB.") from e

            # Parse schema string if found
            loaded_schema: typing.Optional[dict] = None
            if loaded_schema_str:
                try:
                    # We already know it's JSON representing a dict from the check above
                    loaded_schema = json.loads(loaded_schema_str)
                except Exception as e: # Should not happen, but safety first
                    log.error(f"SqliteHandler: Unexpected error parsing stored schema string: {e}", exc_info=True)

            # Reconstruct nested dictionary from flat values
            values_dict = self._unflatten_dict(flat_values)

            log.debug(f"SqliteHandler: Load successful from {filepath}. Version='{loaded_version}', Schema loaded={'Yes' if loaded_schema else 'No'}.")
            return {
                "version": loaded_version,
                "schema": loaded_schema,
                "values": values_dict,
            }

        except sqlite3.Error as e:
            raise HandlerError(f"SQLite error loading configuration: {e}") from e
        except (EncryptionError, HandlerError):
            raise # Re-raise specific errors
        except Exception as e:
            raise HandlerError(f"Unexpected error loading SQLite file {filepath}: {e}") from e
        finally:
            if conn: conn.close()

    def save(self, filepath: Path, data: dict, mode: str = "values") -> None:
        """
        Saves configuration data to an SQLite database file using standard keys.

        Flattens nested structures using dot notation keys, serializes values
        to JSON strings, encrypts the JSON string if needed, and stores key-value
        pairs in the 'config' table. Uses standard keys from the `data` payload.

        Args:
            filepath: The Path object pointing to the target SQLite database file.
            data: The full data payload from ConfigGuard including standard keys.
            mode: 'values' or 'full'.

        Raises:
            HandlerError: If database connection, serialization, or writing fails.
            EncryptionError: If encryption fails.
            ValueError: If an invalid `mode` is provided or required keys are missing.
        """
        log.debug(f"SqliteHandler: Saving to: {filepath} (mode: {mode})")

        # Extract necessary info and standard keys from payload
        version = data.get("instance_version")
        schema_def = data.get("schema_definition")
        config_values = data.get("config_values")
        VERSION_KEY = data.get("__version_key__", "__version__")
        SCHEMA_KEY = data.get("__schema_key__", "__schema__")
        # VALUES_KEY = data.get("__values_key__", "__settings__") # Not used for DB keys

        items_to_insert: typing.List[typing.Tuple[str, bytes]] = []

        # --- Validate payload and Prepare items based on mode ---
        if mode == "full":
            if not all(k in data for k in ('instance_version', 'schema_definition', 'config_values')):
                raise ValueError("Missing required data keys for 'full' save mode.")
            if not isinstance(config_values, Mapping):
                 raise ValueError("'config_values' must be a dictionary/mapping for 'full' save mode.")
            if not isinstance(schema_def, Mapping):
                 raise ValueError("'schema_definition' must be a dictionary/mapping for 'full' save mode.")

            # Add version and schema as special keys
            try:
                version_json = json.dumps(version).encode("utf-8")
                version_blob = self._encrypt(version_json) if self._fernet else version_json
                items_to_insert.append((VERSION_KEY, version_blob))

                schema_json = json.dumps(schema_def).encode("utf-8")
                schema_blob = self._encrypt(schema_json) if self._fernet else schema_json
                items_to_insert.append((SCHEMA_KEY, schema_blob))
            except (TypeError, EncryptionError) as e:
                 raise HandlerError(f"Failed to prepare metadata for 'full' mode: {e}") from e

            values_to_flatten = config_values
            log.debug("SqliteHandler: Preparing 'full' data for SQLite save.")

        elif mode == "values":
            if not all(k in data for k in ('instance_version', 'config_values')):
                 raise ValueError("Missing required data keys for 'values' save mode.")
            if not isinstance(config_values, Mapping):
                raise ValueError("'config_values' must be a dictionary/mapping for 'values' save mode.")

            # Add only version as special key
            try:
                version_json = json.dumps(version).encode("utf-8")
                version_blob = self._encrypt(version_json) if self._fernet else version_json
                items_to_insert.append((VERSION_KEY, version_blob))
            except (TypeError, EncryptionError) as e:
                 raise HandlerError(f"Failed to prepare version metadata for 'values' mode: {e}") from e

            values_to_flatten = config_values
            log.debug("SqliteHandler: Preparing 'values' data (version + values) for SQLite save.")
        else:
            raise ValueError(f"Invalid save mode specified for SqliteHandler: '{mode}'. Must be 'values' or 'full'.")

        conn: typing.Optional[sqlite3.Connection] = None
        try:
            # Flatten the dictionary to get dot-notation keys
            flat_values = self._flatten_dict(values_to_flatten)

            # Process regular config values
            for key, value in flat_values.items():
                try:
                    value_json_bytes = json.dumps(value).encode("utf-8")
                    value_blob = self._encrypt(value_json_bytes) if self._fernet else value_json_bytes
                    items_to_insert.append((key, value_blob))
                except TypeError as e:
                    raise HandlerError(f"Data for key '{key}' cannot be serialized to JSON: {e}") from e
                except EncryptionError as e:
                    raise # Re-raise specific error

            # Perform database operations
            conn = self._connect(filepath)
            cursor = conn.cursor()
            try:
                conn.execute("BEGIN")
                log.debug("SqliteHandler: Clearing existing config table data.")
                cursor.execute("DELETE FROM config") # Clear all before insert

                log.debug(f"SqliteHandler: Inserting/Replacing {len(items_to_insert)} items.")
                cursor.executemany("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", items_to_insert)
                conn.commit()
                log.info(f"SqliteHandler: Successfully saved to {filepath} (mode: {mode}).")

            except sqlite3.Error as e:
                conn.rollback()
                raise HandlerError(f"SQLite transaction error during save: {e}") from e

        except sqlite3.Error as e:
            raise HandlerError(f"SQLite error saving configuration: {e}") from e
        except (EncryptionError, HandlerError, ValueError):
            raise # Re-raise specific errors
        except Exception as e:
            raise HandlerError(f"Unexpected error saving SQLite file {filepath}: {e}") from e
        finally:
            if conn: conn.close()

