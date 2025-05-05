# -*- coding: utf-8 -*-
# Project: ConfigGuard
# File: configguard/handlers/yaml_handler.py
# Author: ParisNeo with Gemini 2.5
# Date: 2025-05-04 (Updated for standard keys)
# Description: Concrete implementation of StorageHandler for YAML file format.
#              Handles loading and saving configuration data (values-only or full state,
#              including nested structures) to/from YAML files, including optional
#              encryption/decryption. Requires the 'PyYAML' library. Uses standard keys.

import typing
from collections.abc import Mapping
from pathlib import Path

from ..exceptions import EncryptionError, HandlerError
from ..log import log
from .base import LoadResult, StorageHandler

try:
    import yaml
except ImportError:
    yaml = None


class YamlHandler(StorageHandler):
    """
    Handles loading and saving configuration data in YAML format using standard keys.

    Supports saving configuration values (prepended with `__version__`) and saving
    the full state (`__version__`, `__schema__`, `__settings__`). Handles encryption.
    Requires the 'PyYAML' library. Uses `yaml.safe_load`.
    """

    def __init__(self, fernet: typing.Optional[typing.Any] = None) -> None:
        if yaml is None:
            log.error("The 'PyYAML' library is required for YamlHandler.")
            raise ImportError("YamlHandler requires the 'PyYAML' library. Please install it.")
        super().__init__(fernet)

    def load(self, filepath: Path) -> LoadResult:
        """
        Loads configuration from a YAML file, handling standard keys and decryption.

        Args:
            filepath: Path to the YAML configuration file.

        Returns:
            A LoadResult dictionary containing 'version', 'schema', and 'values'.

        Raises:
            FileNotFoundError, HandlerError, EncryptionError, ImportError.
        """
        log.debug(f"YamlHandler: Attempting to load from: {filepath}")
        if not filepath.exists():
            raise FileNotFoundError(f"Configuration file not found: {filepath}")

        try:
            raw_data = filepath.read_bytes()
            if not raw_data:
                log.warning(f"YAML configuration file is empty: {filepath}. Returning empty values.")
                return {"version": None, "schema": None, "values": {}}

            decrypted_bytes: bytes
            if self._fernet:
                log.debug(f"YamlHandler: Decrypting data from {filepath}...")
                decrypted_bytes = self._decrypt(raw_data)
                log.debug(f"YamlHandler: Decryption successful.")
            else:
                decrypted_bytes = raw_data

            try:
                file_content = decrypted_bytes.decode("utf-8")
                # Use safe_load!
                loaded_data = yaml.safe_load(file_content)
            except UnicodeDecodeError as e:
                raise HandlerError(f"File {filepath} does not contain valid UTF-8 encoded data.") from e
            except yaml.YAMLError as e:
                raise HandlerError(f"Invalid YAML structure in {filepath}: {e}") from e

            # Handle empty or null YAML
            if loaded_data is None:
                 log.warning(f"YAML file {filepath} parsed as None. Returning empty values.")
                 return {"version": None, "schema": None, "values": {}}

            # --- Structure Detection ---
            loaded_version: typing.Optional[str] = None
            loaded_schema: typing.Optional[dict] = None
            loaded_values: typing.Optional[dict] = None
            VERSION_KEY = "__version__"
            SCHEMA_KEY = "__schema__"
            VALUES_KEY = "__settings__"

            if isinstance(loaded_data, Mapping):
                # 1. Check standard 'full' format
                if all(k in loaded_data for k in (VERSION_KEY, SCHEMA_KEY, VALUES_KEY)):
                    log.debug(f"YamlHandler: Loaded standard 'full' structure ({VERSION_KEY}, {SCHEMA_KEY}, {VALUES_KEY})")
                    loaded_version = loaded_data.get(VERSION_KEY)
                    loaded_schema = loaded_data.get(SCHEMA_KEY)
                    loaded_values = loaded_data.get(VALUES_KEY)
                # 2. Check legacy 'full' format
                elif all(k in loaded_data for k in ("version", "schema", "values")):
                     log.debug(f"YamlHandler: Loaded legacy 'full' structure (version, schema, values)")
                     loaded_version = loaded_data.get("version")
                     loaded_schema = loaded_data.get("schema")
                     loaded_values = loaded_data.get("values")
                # 3. Check standard 'values' format
                elif VERSION_KEY in loaded_data:
                    log.debug(f"YamlHandler: Loaded standard 'values' structure ({VERSION_KEY} + data)")
                    loaded_version = loaded_data.get(VERSION_KEY)
                    loaded_values = {k: v for k, v in loaded_data.items() if k != VERSION_KEY}
                # 4. Assume legacy 'values' format
                else:
                    log.debug(f"YamlHandler: Loaded simple values dictionary (legacy 'values' format)")
                    loaded_values = dict(loaded_data)

                # --- Validate extracted components ---
                if loaded_values is None or not isinstance(loaded_values, Mapping):
                    raise HandlerError(f"Could not extract a valid 'values' dictionary from {filepath}.")
                if loaded_schema is not None and not isinstance(loaded_schema, Mapping):
                     raise HandlerError(f"Invalid 'schema' section in {filepath} (must be a mapping or null).")
                if loaded_version is not None and not isinstance(loaded_version, str):
                    log.warning(f"Version field in {filepath} is not a string. Attempting conversion.")
                    try: loaded_version = str(loaded_version)
                    except Exception: raise HandlerError(f"Could not convert 'version' field in {filepath} to string.")

                return {
                    "version": loaded_version,
                    "schema": dict(loaded_schema) if loaded_schema else None,
                    "values": dict(loaded_values),
                }
            else:
                raise HandlerError(f"Root YAML element in {filepath} must be a mapping (dictionary).")

        except (FileNotFoundError, EncryptionError, HandlerError):
            raise
        except Exception as e:
            log.error(f"YamlHandler: Unexpected error loading from {filepath}: {e}", exc_info=True)
            raise HandlerError(f"Unexpected error loading YAML file {filepath}: {e}") from e

    def save(self, filepath: Path, data: dict, mode: str = "values") -> None:
        """
        Saves configuration data to a YAML file using standard keys and save modes.

        Args:
            filepath: Path to the target YAML file.
            data: Full data payload from ConfigGuard including standard keys.
            mode: 'values' or 'full'.

        Raises:
            HandlerError, EncryptionError, ValueError, ImportError.
        """
        log.debug(f"YamlHandler: Saving to: {filepath} (mode: {mode})")

        version = data.get("instance_version")
        schema_def = data.get("schema_definition")
        config_values = data.get("config_values")
        VERSION_KEY = data.get("__version_key__", "__version__")
        SCHEMA_KEY = data.get("__schema_key__", "__schema__")
        VALUES_KEY = data.get("__values_key__", "__settings__")

        data_to_serialize: typing.Any
        if mode == "full":
            if not all(k in data for k in ('instance_version', 'schema_definition', 'config_values')):
                raise ValueError("Missing required data keys for 'full' save mode.")
            if not isinstance(config_values, Mapping): raise ValueError("'config_values' must be a mapping.")
            if not isinstance(schema_def, Mapping): raise ValueError("'schema_definition' must be a mapping.")

            data_to_serialize = {
                VERSION_KEY: version,
                SCHEMA_KEY: schema_def,
                VALUES_KEY: config_values,
            }
            log.debug("YamlHandler: Preparing 'full' data structure for YAML serialization.")

        elif mode == "values":
            if not all(k in data for k in ('instance_version', 'config_values')):
                 raise ValueError("Missing required data keys for 'values' save mode.")
            if not isinstance(config_values, Mapping):
                raise ValueError("'config_values' must be a dictionary/mapping for 'values' save mode.")

            data_to_serialize = {VERSION_KEY: version, **config_values}
            log.debug(f"YamlHandler: Preparing 'values' data structure ({VERSION_KEY} + values).")
        else:
            raise ValueError(f"Invalid save mode specified for YamlHandler: '{mode}'. Must be 'values' or 'full'.")

        try:
            # Serialize to YAML string bytes
            try:
                yaml_string = yaml.dump(data_to_serialize, default_flow_style=False, sort_keys=False, allow_unicode=True)
                yaml_bytes = yaml_string.encode("utf-8")
            except yaml.YAMLError as e:
                raise HandlerError(f"Data cannot be serialized to YAML: {e}") from e

            # Encrypt if needed
            bytes_to_write: bytes
            status_log = "(unencrypted)"
            if self._fernet:
                log.debug(f"YamlHandler: Encrypting data for {filepath}...")
                bytes_to_write = self._encrypt(yaml_bytes)
                status_log = "(encrypted)"
                log.debug(f"YamlHandler: Encryption successful.")
            else:
                bytes_to_write = yaml_bytes

            # Write bytes to file
            log.debug(f"YamlHandler: Writing {len(bytes_to_write)} bytes to {filepath}")
            try:
                filepath.parent.mkdir(parents=True, exist_ok=True)
                filepath.write_bytes(bytes_to_write)
            except IOError as e:
                raise HandlerError(f"Failed to write configuration file {filepath}: {e}") from e

            log.info(f"YamlHandler: Successfully saved to {filepath} {status_log} (mode: {mode}).")

        except (EncryptionError, HandlerError, ValueError):
            raise
        except Exception as e:
            log.error(f"YamlHandler: Unexpected error saving to {filepath}: {e}", exc_info=True)
            raise HandlerError(f"Unexpected error saving YAML file {filepath}: {e}") from e
