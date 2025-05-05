# Project: ConfigGuard
# File: configguard/handlers/json_handler.py
# Author: ParisNeo with Gemini 2.5
# Date: 2025-05-04 (Updated for standard keys)
# Description: Concrete implementation of StorageHandler for JSON file format.
#              Handles loading and saving configuration data (values-only or full state,
#              including nested structures) to/from JSON files, including optional
#              encryption/decryption. Uses standard keys __version__, __schema__, __settings__.

import json
import typing
from collections.abc import Mapping
from pathlib import Path

from ..exceptions import EncryptionError, HandlerError
from ..log import log
from .base import LoadResult, StorageHandler


class JsonHandler(StorageHandler):
    """
    Handles loading and saving configuration data in JSON format.

    Supports both saving configuration values (prepended with '__version__')
    and saving the full state ('__version__', '__schema__', '__settings__').
    Also handles encryption/decryption transparently if initialized with a Fernet key.
    Nested configuration structures are handled naturally by the JSON format.
    """

    # __init__ is inherited from StorageHandler, takes optional fernet

    def load(self, filepath: Path) -> LoadResult:
        """
        Loads configuration from a JSON file, handling decryption and standard keys.

        Reads the specified JSON file, decrypts its content if a Fernet key was
        provided, parses the JSON data, and determines the structure ('full' or 'values')
        based on standard keys (`__version__`, `__schema__`, `__settings__`) or legacy keys.

        Args:
            filepath: The Path object pointing to the JSON configuration file.

        Returns:
            A LoadResult dictionary containing 'version', 'schema', and 'values'.

        Raises:
            FileNotFoundError: If the file does not exist.
            HandlerError: If the file is not valid JSON, UTF-8, or has an unexpected structure.
            EncryptionError: If decryption fails.
        """
        log.debug(f"JsonHandler: Attempting to load from: {filepath}")
        if not filepath.exists():
            raise FileNotFoundError(f"Configuration file not found: {filepath}")

        try:
            raw_data = filepath.read_bytes()
            if not raw_data:
                log.warning(f"JSON configuration file is empty: {filepath}. Returning empty values.")
                return {"version": None, "schema": None, "values": {}}

            decrypted_bytes: bytes
            if self._fernet:
                log.debug(f"JsonHandler: Decrypting data from {filepath}...")
                decrypted_bytes = self._decrypt(raw_data)
                log.debug(f"JsonHandler: Decryption successful for {filepath}.")
            else:
                decrypted_bytes = raw_data

            try:
                file_content = decrypted_bytes.decode("utf-8")
                loaded_data = json.loads(file_content)
            except UnicodeDecodeError as e:
                raise HandlerError(f"File {filepath} does not contain valid UTF-8 encoded data.") from e
            except json.JSONDecodeError as e:
                raise HandlerError(f"Invalid JSON structure in {filepath}: {e}") from e

            # --- Structure Detection using Standard and Legacy Keys ---
            loaded_version: typing.Optional[str] = None
            loaded_schema: typing.Optional[dict] = None
            loaded_values: typing.Optional[dict] = None

            if isinstance(loaded_data, Mapping):
                # Get standard key names from ConfigGuard constants if possible (future proofing)
                # Fallback to hardcoded strings for now
                VERSION_KEY = "__version__"
                SCHEMA_KEY = "__schema__"
                VALUES_KEY = "__settings__"

                # 1. Check for standard 'full' format
                if all(k in loaded_data for k in (VERSION_KEY, SCHEMA_KEY, VALUES_KEY)):
                    log.debug(f"JsonHandler: Loaded standard 'full' structure ({VERSION_KEY}, {SCHEMA_KEY}, {VALUES_KEY}) from {filepath}")
                    loaded_version = loaded_data.get(VERSION_KEY)
                    loaded_schema = loaded_data.get(SCHEMA_KEY)
                    loaded_values = loaded_data.get(VALUES_KEY)

                # 2. Check for legacy 'full' format
                elif all(k in loaded_data for k in ("version", "schema", "values")):
                     log.debug(f"JsonHandler: Loaded legacy 'full' structure (version, schema, values) from {filepath}")
                     loaded_version = loaded_data.get("version")
                     loaded_schema = loaded_data.get("schema")
                     loaded_values = loaded_data.get("values")

                # 3. Check for standard 'values' format (version + values)
                elif VERSION_KEY in loaded_data:
                    log.debug(f"JsonHandler: Loaded standard 'values' structure ({VERSION_KEY} + data) from {filepath}")
                    loaded_version = loaded_data.get(VERSION_KEY)
                    # Values are everything else in the dict
                    loaded_values = {k: v for k, v in loaded_data.items() if k != VERSION_KEY}

                # 4. Assume legacy 'values' format (entire dict is values)
                else:
                    log.debug(f"JsonHandler: Loaded simple values dictionary/mapping (legacy 'values' format) from {filepath}")
                    loaded_values = dict(loaded_data) # Ensure it's a dict

                # --- Validate extracted components ---
                if loaded_values is None or not isinstance(loaded_values, Mapping):
                    raise HandlerError(f"Could not extract a valid 'values' dictionary from {filepath}.")
                if loaded_schema is not None and not isinstance(loaded_schema, Mapping):
                    raise HandlerError(f"Invalid 'schema' section in {filepath} (must be a dictionary/mapping or null).")
                if loaded_version is not None and not isinstance(loaded_version, str):
                    log.warning(f"Version field in {filepath} is not a string (type: {type(loaded_version).__name__}). Attempting conversion.")
                    try: loaded_version = str(loaded_version)
                    except Exception: raise HandlerError(f"Could not convert 'version' field in {filepath} to string.")

                return {
                    "version": loaded_version,
                    "schema": loaded_schema,
                    "values": loaded_values,
                }
            else:
                # If the top level isn't a dict/mapping, it's invalid
                raise HandlerError(f"Root JSON element in {filepath} must be a dictionary/mapping.")

        except (FileNotFoundError, EncryptionError, HandlerError):
            raise
        except Exception as e:
            log.error(f"JsonHandler: Unexpected error loading from {filepath}: {e}", exc_info=True)
            raise HandlerError(f"Unexpected error loading JSON file {filepath}: {e}") from e

    def save(self, filepath: Path, data: dict, mode: str = "values") -> None:
        """
        Saves configuration data to a JSON file using standard keys and save modes.

        Serializes the provided data payload to JSON.
        - 'values' mode: Saves a dict containing `__version__` key and the config values.
        - 'full' mode: Saves a dict with `__version__`, `__schema__`, `__settings__` keys.
        Encrypts the resulting JSON bytes if a Fernet key was provided.

        Args:
            filepath: The Path object pointing to the target JSON file.
            data: The full data payload from ConfigGuard, containing keys
                  'instance_version', 'schema_definition', 'config_values',
                  '__version_key__', '__schema_key__', '__values_key__'.
            mode: 'values' or 'full'.

        Raises:
            HandlerError: If serialization fails, required keys are missing, or writing fails.
            EncryptionError: If encryption fails.
            ValueError: If an invalid `mode` is provided or required keys are missing.
        """
        log.debug(f"JsonHandler: Saving to: {filepath} (mode: {mode})")

        # Extract necessary info and standard keys from payload
        version = data.get("instance_version")
        schema_def = data.get("schema_definition")
        config_values = data.get("config_values")
        VERSION_KEY = data.get("__version_key__", "__version__") # Fallback just in case
        SCHEMA_KEY = data.get("__schema_key__", "__schema__")
        VALUES_KEY = data.get("__values_key__", "__settings__")

        # --- Construct data structure based on mode ---
        data_to_serialize: typing.Any
        if mode == "full":
            if not all(k in data for k in ('instance_version', 'schema_definition', 'config_values')):
                raise ValueError("Missing required data keys ('instance_version', 'schema_definition', 'config_values') for 'full' save mode.")
            if not isinstance(config_values, Mapping):
                 raise ValueError("'config_values' must be a dictionary/mapping for 'full' save mode.")
            if not isinstance(schema_def, Mapping):
                 raise ValueError("'schema_definition' must be a dictionary/mapping for 'full' save mode.")

            data_to_serialize = {
                VERSION_KEY: version,
                SCHEMA_KEY: schema_def,
                VALUES_KEY: config_values,
            }
            log.debug(f"JsonHandler: Preparing 'full' data structure for JSON serialization using standard keys.")
        elif mode == "values":
            if not all(k in data for k in ('instance_version', 'config_values')):
                 raise ValueError("Missing required data keys ('instance_version', 'config_values') for 'values' save mode.")
            if not isinstance(config_values, Mapping):
                raise ValueError("'config_values' must be a dictionary/mapping for 'values' save mode.")

            # Create dict with version key first, then merge config values
            data_to_serialize = {VERSION_KEY: version, **config_values}
            log.debug(f"JsonHandler: Preparing 'values' data structure ({VERSION_KEY} + values) for JSON serialization.")
        else:
            raise ValueError(f"Invalid save mode specified for JsonHandler: '{mode}'. Must be 'values' or 'full'.")

        try:
            # Serialize to JSON bytes
            try:
                json_bytes = json.dumps(data_to_serialize, indent=4, ensure_ascii=False).encode("utf-8")
            except TypeError as e:
                raise HandlerError(f"Data cannot be serialized to JSON: {e}") from e

            # Encrypt if needed
            bytes_to_write: bytes
            status_log = "(unencrypted)"
            if self._fernet:
                log.debug(f"JsonHandler: Encrypting data for {filepath}...")
                bytes_to_write = self._encrypt(json_bytes)
                status_log = "(encrypted)"
                log.debug(f"JsonHandler: Encryption successful for {filepath}.")
            else:
                bytes_to_write = json_bytes

            # Write bytes to file
            log.debug(f"JsonHandler: Writing {len(bytes_to_write)} bytes to {filepath}")
            try:
                filepath.parent.mkdir(parents=True, exist_ok=True)
                filepath.write_bytes(bytes_to_write)
            except OSError as e:
                raise HandlerError(f"Failed to write configuration file {filepath}: {e}") from e

            log.info(f"JsonHandler: Successfully saved to {filepath} {status_log} (mode: {mode}).")

        except (EncryptionError, HandlerError, ValueError):
            raise
        except Exception as e:
            log.error(f"JsonHandler: Unexpected error saving to {filepath}: {e}", exc_info=True)
            raise HandlerError(f"Unexpected error saving JSON file {filepath}: {e}") from e
