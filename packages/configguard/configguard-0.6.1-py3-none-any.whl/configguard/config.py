# -*- coding: utf-8 -*-
# Project: ConfigGuard
# File: configguard/config.py
# Author: ParisNeo with Gemini 2.5
# Date: 2025-05-04 (Revised based on user request for standard key naming and save-on-migrate)
# Description: Main ConfigGuard class for managing application configurations,
#              designed to be handler-agnostic, support versioning/migration,
#              and handle nested configuration structures including dynamic sections.

import copy
import typing
from collections.abc import Mapping, MutableMapping
from pathlib import Path

from packaging.version import InvalidVersion
from packaging.version import parse as parse_version

from .exceptions import (
    EncryptionError,
    HandlerError,
    SchemaError,
    SettingNotFoundError,
    ValidationError,
)
from .handlers import get_handler  # Factory function
from .handlers.base import LoadResult, StorageHandler
from .handlers.json_handler import JsonHandler  # Used only in _load_schema_definition
from .log import log
from .schema import SUPPORTED_TYPES, SettingSchema
from .section import ConfigSection  # Import the new ConfigSection class
from .setting import ConfigSetting

# Handle optional cryptography import
try:
    from cryptography.fernet import Fernet
except ImportError:
    Fernet = None  # Define Fernet as None if cryptography is not installed


# --- Type Coercion Helper ---
def _try_coerce(
    value: typing.Any, target_type: type, source_type_str: typing.Optional[str] = None
) -> typing.Any:
    """
    Attempts basic coercion between compatible types (int, float, str, bool).

    Args:
        value: The value to coerce.
        target_type: The target Python type (e.g., int, str, bool).
        source_type_str: Optional string representation of the source type for logging.

    Returns:
        The coerced value if successful, otherwise the original value.
    """
    if isinstance(value, target_type):
        return value  # Already correct type

    original_value_repr = repr(value)  # For logging
    log.debug(
        f"Attempting coercion for {original_value_repr} to {target_type.__name__} (source type approx: {source_type_str or type(value).__name__})"
    )

    # Bool coercion
    if target_type is bool:
        if isinstance(value, str):
            val_lower = value.lower()
            if val_lower == "true":
                return True
            if val_lower == "false":
                return False
        if isinstance(value, (int, float)):
            if value == 1:
                return True
            if value == 0:
                return False
        log.warning(f"Could not coerce {original_value_repr} to bool.")
        return value  # Return original for validation to fail clearly

    # Numeric/String coercion
    if target_type in (int, float):
        if isinstance(value, (int, float)):  # Already numeric, just convert type
            try:
                return target_type(value)
            except Exception:
                pass  # Should not fail, but be safe
        elif isinstance(value, str):
            try:
                numeric_val = float(value)  # Try float first
                if target_type is int:
                    if numeric_val.is_integer():
                        return int(numeric_val)
                    else:
                        log.warning(
                            f"Cannot coerce string '{value}' to int (not an integer)."
                        )
                        return value  # Return original string if float needed but int requested
                else:  # Target is float
                    return numeric_val
            except ValueError:
                log.warning(
                    f"Cannot coerce string '{value}' to numeric type {target_type.__name__}."
                )
                return value  # Return original string if not numeric
        # else: Fall through, return original value

    elif target_type is str:
        if isinstance(value, (int, float, bool)):
            return str(value)
        # else: Fall through for other types

    elif target_type is list:
        # TODO: Consider adding optional basic coercion (e.g., comma-separated string to list)
        pass

    log.debug(
        f"No specific coercion rule applied for {original_value_repr} to {target_type.__name__}. Returning original."
    )
    return value


class ConfigGuard(MutableMapping):
    """
    Main class for managing application configurations. Agnostic of storage format.

    Handles configuration schema definition (including nested sections), validation,
    loading/saving via storage handlers, encryption, versioning, and migration.
    Sections defined with an empty schema ({}) act as dynamic dictionaries.
    Access settings via attribute (`config.setting` or `config.section.setting`) or
    dictionary syntax (`config['setting']` or `config['section']['setting']`).
    Access schema details via `config.sc_setting` or `config.sc_section.sc_setting`.

    Standard key naming for storage and export:
    - `__version__`: Used in schema definition, 'values' mode saves, and 'full' mode saves/exports.
    - `__schema__`: Used in 'full' mode saves/exports for the schema definition.
    - `__settings__`: Used in 'full' mode saves/exports for the configuration values structure.
    """

    # --- Constants for standard keys ---
    VERSION_KEY = "__version__"
    SCHEMA_KEY = "__schema__"
    VALUES_KEY = "__settings__"

    SECTION_TYPE_KEY = "section"  # Type identifier for sections in schema

    def __init__(
        self,
        schema: typing.Union[dict, str, Path],
        config_path: typing.Optional[typing.Union[str, Path]] = None,
        encryption_key: typing.Optional[bytes] = None,
        autosave: bool = False,
        handler: typing.Optional[StorageHandler] = None,
        instance_version: typing.Optional[str] = None,
        load_options: typing.Optional[dict] = None, # Options for initial load
    ) -> None:
        """
        Initializes the ConfigGuard instance.

        Args:
            schema: A schema definition dictionary or a path to a JSON schema file.
                    The schema dictionary should contain a `__version__` key unless
                    `instance_version` is provided.
            config_path: Optional path to the configuration file. Used for initial load
                         and as the default path for subsequent `load()` and `save()` calls.
                         The file extension determines the handler used, unless `handler` is provided.
            encryption_key: Optional Fernet encryption key (bytes). If provided, data will
                            be encrypted on save and decrypted on load. Ignored if `handler` is provided.
            autosave: If True, automatically save configuration (values only) whenever a
                      setting's value is changed. Requires `config_path` and a valid handler.
            handler: Optional pre-initialized StorageHandler instance. If provided, it overrides
                     automatic handler detection based on `config_path`. The `encryption_key`
                     argument is ignored if a handler is provided (the handler should be
                     initialized with its own key if needed).
            instance_version: Optional string specifying the version of this ConfigGuard
                              instance. If provided, this version takes precedence over the
                              `__version__` key found in the `schema` dictionary. If neither
                              is provided, the version defaults to "0.0.0". Used for migration logic.
            load_options: Optional dictionary passed directly to the initial `self.load()` call
                          if `config_path` is provided. Allows passing options like
                          `update_file=True` during initialization. Defaults to None.

        Raises:
            SchemaError: If the schema is invalid, has an invalid version format, or is missing
                         a version when `instance_version` is also not provided.
            HandlerError: If a handler cannot be determined or initialized.
            EncryptionError: If the encryption key is invalid.
            TypeError: If `schema` or `handler` have incorrect types.
            ImportError: If a required dependency for the selected handler is missing.
        """
        log.info("Initializing ConfigGuard...")
        self._settings: typing.Dict[str, typing.Union[ConfigSetting, ConfigSection]] = {}
        self._raw_instance_schema: dict = self._load_schema_definition(schema)

        # --- Determine and store instance version ---
        final_version_str: typing.Optional[str] = None
        schema_version_str: typing.Optional[str] = self._raw_instance_schema.get(self.VERSION_KEY)

        if instance_version is not None:
            log.info(f"Using provided instance_version parameter: '{instance_version}'")
            final_version_str = instance_version
            if schema_version_str is not None and str(schema_version_str) != instance_version:
                log.warning(
                    f"Provided instance_version ('{instance_version}') overrides schema {self.VERSION_KEY} ('{schema_version_str}')."
                )
        elif schema_version_str is not None:
            log.info(f"Using {self.VERSION_KEY} found in schema: '{schema_version_str}'")
            final_version_str = str(schema_version_str)
        else:
            log.warning(
                f"Neither instance_version parameter nor schema '{self.VERSION_KEY}' key provided. "
                "Defaulting instance version to '0.0.0'."
            )
            final_version_str = "0.0.0"

        try:
            parse_version(final_version_str)
            self.version: str = final_version_str
            log.debug(f"ConfigGuard instance version set to: {self.version}")
        except InvalidVersion:
            log.error(
                f"Invalid version format determined: '{final_version_str}' "
                f"(Source: {'parameter' if instance_version else 'schema/default'})."
            )
            raise SchemaError(f"Invalid version format for instance: {final_version_str}")
        # --- End Version Determination ---

        self._instance_schema_definition: dict = {
            k: v for k, v in self._raw_instance_schema.items() if k != self.VERSION_KEY
        }

        self._config_path: typing.Optional[Path] = (
            Path(config_path) if config_path else None
        )
        self._handler: typing.Optional[StorageHandler] = None
        self._fernet: typing.Optional[Fernet] = None
        self._autosave: bool = autosave
        self.loaded_file_version: typing.Optional[str] = None

        if encryption_key and handler is None:
            if Fernet is None:
                log.error(
                    "Encryption requires 'cryptography'. Please install it: pip install cryptography"
                )
                raise EncryptionError(
                    "Cryptography library not found, but encryption key provided."
                )
            try:
                self._fernet = Fernet(encryption_key)
                log.info("Encryption enabled (Fernet instance created).")
            except Exception as e:
                log.error(f"Failed to initialize encryption with provided key: {e}")
                raise EncryptionError(
                    f"Invalid encryption key or Fernet setup failed: {e}"
                ) from e
        elif encryption_key and handler is not None:
              log.warning("`encryption_key` argument is ignored when a `handler` instance is provided.")

        # --- Handler Initialization Logic ---
        self._handler: typing.Optional[StorageHandler] = None
        if handler is not None:
            if not isinstance(handler, StorageHandler):
                 raise TypeError(f"Provided handler must be an instance of StorageHandler, not {type(handler).__name__}")
            self._handler = handler
            log.info(f"Using provided pre-configured handler: {type(self._handler).__name__}")
            if hasattr(self._handler,'_fernet') and getattr(self._handler, '_fernet', None) is not None:
                 log.info("Provided handler appears to have encryption enabled.")
            if self._config_path:
                 log.info(f"Using '{self._config_path}' as default load/save path (handler was provided explicitly).")
        elif self._config_path:
            log.info(f"No handler provided, attempting to find handler for path: {self._config_path}")
            try:
                self._handler = get_handler(self._config_path, fernet=self._fernet)
                log.info(f"Initialized handler '{type(self._handler).__name__}' for path: {self._config_path}")
            except HandlerError as e:
                log.warning(f"{e}. Configuration loading/saving might be disabled for this path.")
            except ImportError as e:
                 log.error(f"Missing dependency for handler required by '{self._config_path}': {e}")
                 raise
        else:
            log.info("No configuration path or handler provided. Operating in-memory only unless path specified in load/save.")

        # --- Build Internal Structure ---
        self._build_internal_structure_from_schema(
            self._instance_schema_definition, self._settings, self
        )

        # --- Initial Load ---
        if self._config_path and self._handler:
            try:
                # Pass load_options to the initial load call
                initial_load_options = load_options or {}
                self.load(**initial_load_options) # Unpack options dict
            except FileNotFoundError:
                log.warning(f"Configuration file {self._config_path} not found. Initializing with defaults.")
            except (HandlerError, EncryptionError, ValidationError, SchemaError, SettingNotFoundError) as e:
                log.error(f"Failed to load initial configuration from {self._config_path}: {e}. Continuing with defaults.")
            except Exception as e:
                log.error(f"Unexpected error loading initial configuration from {self._config_path}: {e}", exc_info=True)
        elif self._handler and not self._config_path:
             log.info("Handler provided but no config_path. Initializing with defaults. Use load(filepath=...) for loading.")
        else:
            log.info("No valid handler/path setup, or file not found. Initializing with default values.")

        log.info(f"ConfigGuard initialized successfully (Instance Version: {self.version}).")


    def _trigger_autosave(self, setting_name: str) -> None:
        """Internal helper to trigger autosave if enabled and possible."""
        if self._autosave:
            log.debug(
                f"Autosaving configuration (values) due to change in '{setting_name}'..."
            )
            if self._handler and self._config_path:
                try:
                    # Autosave always uses 'values' mode with the new structure
                    self.save(mode="values")
                except (HandlerError, EncryptionError) as e:
                    log.error(f"Autosave failed: {e}")
                except Exception as e:
                    log.error(f"Unexpected error during autosave: {e}", exc_info=True)
            else:
                log.warning(
                    f"Autosave for '{setting_name}' skipped: No valid handler or config_path."
                )


    def _load_schema_definition(
        self, schema_input: typing.Union[dict, str, Path]
    ) -> dict:
        """
        Loads the raw schema definition from a dictionary or JSON file.
        Handles schema files that might accidentally be full ConfigGuard saves.

        Args:
            schema_input: Dictionary or path to the schema definition file (JSON expected).

        Returns:
            The raw schema dictionary, including the version key if present.

        Raises:
            SchemaError: If loading fails or the format is invalid.
            TypeError: If schema_input is not a dict, str, or Path.
        """
        if isinstance(schema_input, dict):
            log.debug("Loading schema from dictionary.")
            return copy.deepcopy(schema_input)  # Return a copy
        elif isinstance(schema_input, (str, Path)):
            schema_path = Path(schema_input)
            log.debug(f"Loading schema definition from file: {schema_path}")
            if not schema_path.exists():
                raise SchemaError(f"Schema file not found: {schema_path}")
            if schema_path.suffix.lower() != ".json":
                raise SchemaError(
                    f"Schema file must be a JSON file (.json extension). Found: {schema_path.suffix}"
                )
            try:
                # Use minimal handler for schema loading
                temp_json_handler = JsonHandler(fernet=None)
                # Assume schema file contains schema dict as root unless structure suggests otherwise
                load_result = temp_json_handler.load(schema_path)
                raw_schema = load_result["values"]

                # --- Check if loaded data looks like a full save ---
                is_new_full = all(k in load_result for k in (self.VERSION_KEY, self.SCHEMA_KEY, self.VALUES_KEY))
                # Check for old keys too, avoid conflict if new keys happen to be subset of old
                is_old_full = all(k in load_result for k in ("version", "schema", "values")) and not is_new_full

                extracted_schema: typing.Optional[dict] = None
                version_from_full: typing.Optional[str] = None

                if is_new_full:
                     log.warning(f"Schema file {schema_path} appears to be a 'full' ConfigGuard save (new format); extracting '{self.SCHEMA_KEY}' part.")
                     extracted_schema = load_result.get(self.SCHEMA_KEY)
                     version_from_full = load_result.get(self.VERSION_KEY)
                elif is_old_full:
                     log.warning(f"Schema file {schema_path} appears to be a 'full' ConfigGuard save (old format); extracting 'schema' part.")
                     extracted_schema = load_result.get("schema")
                     version_from_full = load_result.get("version")

                # --- Use extracted schema if found and valid ---
                if extracted_schema is not None:
                    if isinstance(extracted_schema, dict):
                         raw_schema = extracted_schema
                         # Add version back using the standard key if it exists
                         if version_from_full:
                             raw_schema[self.VERSION_KEY] = version_from_full
                    else:
                        key_used = self.SCHEMA_KEY if is_new_full else "schema"
                        raise SchemaError(f"Schema file {schema_path} has '{key_used}' but it's not a dictionary.")
                elif not isinstance(raw_schema, dict):
                     # If not full structure and not a dict, it's invalid
                     raise SchemaError(f"Schema file {schema_path} does not contain a valid JSON object at the root.")

                log.info(f"Successfully loaded schema definition from {schema_path}")
                return raw_schema
            except (HandlerError, FileNotFoundError) as e:
                raise SchemaError(
                    f"Failed to load schema definition from {schema_path}: {e}"
                ) from e
            except Exception as e:
                raise SchemaError(
                    f"Unexpected error loading schema from file {schema_path}: {e}"
                ) from e
        else:
            raise TypeError(
                "Schema input must be a dictionary or a file path (str or Path)."
            )


    def _build_internal_structure_from_schema(
        self,
        schema_definition: dict,
        target_container: typing.Dict[str, typing.Union[ConfigSetting, ConfigSection, typing.Any]],
        parent: typing.Union["ConfigGuard", ConfigSection],
    ) -> None:
        """
        Recursively parses the schema definition and creates ConfigSetting or ConfigSection objects.

        Args:
            schema_definition: The part of the schema to process (a dictionary).
            target_container: The dictionary (e.g., self._settings or section._settings)
                              to populate with created objects.
            parent: The parent object (either the ConfigGuard instance or the parent ConfigSection)
                    needed for context like autosave triggering.
        """
        log.debug(
            f"Building structure for schema level with keys: {list(schema_definition.keys())}"
        )
        for name, definition in schema_definition.items():
            if not isinstance(definition, dict):
                raise SchemaError(
                    f"Invalid schema format for '{name}'. Definition must be a dictionary."
                )

            item_type_str = definition.get("type")

            try:
                if item_type_str == self.SECTION_TYPE_KEY:
                    log.debug(f"Creating ConfigSection for '{name}'...")
                    nested_schema = definition.get("schema")
                    if not isinstance(nested_schema, dict):
                        raise SchemaError(
                            f"Section '{name}' must contain a 'schema' dictionary (use {{}} for dynamic sections)."
                        )
                    section = ConfigSection(
                        name=name, schema_definition=nested_schema, parent=parent
                    )
                    target_container[name] = section
                    if nested_schema: # Only recurse if schema is defined
                        self._build_internal_structure_from_schema(
                            nested_schema, section._settings, section
                        )

                elif item_type_str in SUPPORTED_TYPES:
                    log.debug(f"Creating ConfigSetting for '{name}'...")
                    schema = SettingSchema(name, definition)
                    setting = ConfigSetting(schema, parent=parent)
                    target_container[name] = setting
                else:
                    valid_types = list(SUPPORTED_TYPES.keys()) + [self.SECTION_TYPE_KEY]
                    raise SchemaError(
                        f"Invalid or missing 'type' ('{item_type_str}') for '{name}'. Must be one of {valid_types}."
                    )
            except SchemaError as e:
                log.error(f"Schema error processing '{name}': {e}")
                raise
            except Exception as e:
                log.error(f"Unexpected error processing schema item '{name}': {e}")
                raise SchemaError(
                    f"Unexpected error building structure for '{name}'."
                ) from e

        log.debug("Finished building structure level.")


    def load(self, filepath: typing.Optional[typing.Union[str, Path]] = None, update_file: bool = False) -> None:
        """
        Loads configuration using the configured handler. Handles versioning, migration, and nesting.
        Optionally saves the configuration back after successful migration.

        Args:
            filepath: Optional path to load from. Overrides the instance's default config_path.
            update_file: If True and migration occurs (file version is older than instance or
                         file has no version), the configuration will be saved back to the
                         `load_path` in 'values' mode after successful loading and migration.
                         Defaults to False.

        Raises:
            HandlerError: If loading fails (no path, no handler, deserialization, etc.).
            EncryptionError: If decryption specifically fails.
            SchemaError: If the loaded configuration version is newer than the instance version,
                         or if version formats are invalid.
            FileNotFoundError: If the specified file does not exist.
            ValidationError: If loaded values fail validation after potential migration/coercion.
            SettingNotFoundError: If `ignore_unknown=False` is used during load/migration and
                                  unknown keys are encountered (handler-dependent).
        """
        load_path = Path(filepath) if filepath else self._config_path
        current_handler = self._handler

        if not load_path:
            if self._config_path is None and filepath is None:
                 log.info("Load() called without a path on an in-memory instance. No action taken.")
                 return
            raise HandlerError("No configuration file path specified for loading.")

        if not current_handler:
             if load_path:
                  log.warning(f"No handler configured initially, attempting to find handler for load path: {load_path}")
                  try:
                      current_handler = get_handler(load_path, fernet=self._fernet)
                      self._handler = current_handler # Store if successful
                      log.info(f"Dynamically initialized handler '{type(current_handler).__name__}' for load.")
                  except (HandlerError, ImportError) as e:
                       raise HandlerError(f"No valid handler available or could be initialized for the path: {load_path}. Error: {e}")
             else:
                raise HandlerError("No handler and no path available for loading.")

        log.info(
            f"Attempting to load configuration from: {load_path} using {current_handler.__class__.__name__}"
        )

        try:
            # Handler's load method returns the consistent LoadResult structure.
            # Handler is responsible for checking standard keys (__version__, __schema__, __settings__)
            # and potentially falling back to old keys or simple value structures.
            loaded_data: LoadResult = current_handler.load(load_path)

            loaded_version_str = loaded_data.get("version")
            loaded_schema_dict = loaded_data.get("schema")
            loaded_values_dict = loaded_data.get("values")

            if loaded_values_dict is None or not isinstance(loaded_values_dict, Mapping):
                log.error(f"Handler did not return a valid dictionary/mapping for 'values' from {load_path}")
                raise HandlerError(f"Invalid 'values' data loaded from {load_path}")

            self.loaded_file_version = loaded_version_str
            log.info(
                f"File loaded. Version in file: {loaded_version_str or 'N/A'}. Instance version: {self.version}."
            )

            allow_migration = False
            is_older_version = False
            if loaded_version_str is not None:
                load_mode_desc = f"file contains version info ({loaded_version_str})"
                try:
                    loaded_ver = parse_version(loaded_version_str)
                    instance_ver = parse_version(self.version)
                    if loaded_ver > instance_ver:
                        log.error(
                            f"Loaded config version ({loaded_ver}) is NEWER than instance version ({instance_ver})."
                        )
                        raise SchemaError(
                            f"Cannot load configuration: File version {loaded_ver} is newer than instance version {instance_ver}."
                        )
                    elif loaded_ver < instance_ver:
                        log.warning(
                            f"Loaded config version ({loaded_ver}) is OLDER than instance version ({instance_ver}). Enabling migration logic."
                        )
                        allow_migration = True
                        is_older_version = True # Mark specifically as older version
                    else:
                        log.info(f"Configuration versions match ({instance_ver}).")
                        # Check schema consistency only if file contained schema (full mode)
                        if (
                            loaded_schema_dict
                            and loaded_schema_dict != self._instance_schema_definition
                        ):
                            log.warning(
                                "Loaded schema definition differs from instance schema definition, but versions match. Using instance schema for validation."
                            )
                except InvalidVersion as e:
                    log.error(
                        f"Invalid version format found in loaded file ('{loaded_version_str}'): {e}"
                    )
                    raise SchemaError(
                        f"Invalid version format in loaded file: {loaded_version_str}"
                    ) from e
            else:
                load_mode_desc = "no version info"
                log.warning(
                    "Loaded configuration file has no version information. Applying values directly. Migration behavior applies (unknown keys skipped)."
                )
                allow_migration = True # Treat as migration if no version

            # Apply values using the recursive helper method
            log.info(f"Applying loaded values from '{load_mode_desc}' file...")
            self._apply_and_migrate_values(
                current_container=self._settings,
                current_schema_level=self._instance_schema_definition,
                loaded_values_level=loaded_values_dict,
                loaded_schema_level=loaded_schema_dict, # Schema from file (if any)
                allow_migration=allow_migration,
                ignore_unknown=allow_migration, # If migrating (or versionless), ignore unknown keys
                path_prefix="",
            )

            # --- Save After Migration (if requested) ---
            if allow_migration and update_file:
                 if is_older_version:
                     log.info(f"Configuration loaded from older version ({loaded_version_str}). Saving updated values (with instance version {self.version}) to {load_path} as requested.")
                 else: # No version in file
                     log.info(f"Configuration loaded from file with no version. Saving current values (with instance version {self.version}) to {load_path} as requested.")

                 try:
                     self.save(filepath=load_path, mode="values") # Save updated values with new standard version key
                     log.info(f"Successfully saved updated configuration after migration to {load_path}.")
                 except (HandlerError, EncryptionError, ValueError) as e:
                     log.error(f"Failed to save configuration automatically after migration: {e}")
                 except Exception as e:
                      log.error(f"Unexpected error saving configuration automatically after migration: {e}", exc_info=True)
            elif allow_migration and not update_file:
                 log.info("Migration occurred, but update_file=False. File not automatically saved.")

        except FileNotFoundError:
            log.warning(f"Load failed: File not found at {load_path}")
            raise
        except (
            HandlerError,
            EncryptionError,
            ValidationError,
            SchemaError,
            SettingNotFoundError,
        ) as e:
            log.error(f"Failed to load/process configuration from {load_path}: {e}")
            raise
        except Exception as e:
            log.error(
                f"An unexpected error occurred during loading from {load_path}: {e}",
                exc_info=True,
            )
            raise HandlerError(f"Unexpected error loading configuration: {e}") from e


    def _apply_and_migrate_values(
        self,
        current_container: typing.Dict[str, typing.Union[ConfigSetting, ConfigSection, typing.Any]],
        current_schema_level: dict,
        loaded_values_level: Mapping,
        loaded_schema_level: typing.Optional[Mapping],
        allow_migration: bool,
        ignore_unknown: bool,
        path_prefix: str = "",
    ) -> None:
        """
        Recursively applies loaded values, handling schema differences, coercion, migration,
        and dynamic keys in empty-schema sections.

        Args:
            current_container: The dict (_settings) of the current level.
            current_schema_level: The schema definition dict for the current level.
                                  Will be {} for dynamic sections.
            loaded_values_level: Dictionary of values loaded from the file for the current level.
            loaded_schema_level: Schema loaded from the file (if any) for the current level.
            allow_migration: True if loaded version is older than instance version, or if file had no version.
            ignore_unknown: If False, raise SettingNotFoundError for keys in loaded_values_level
                            not defined in current_schema_level (UNLESS current_schema_level is empty {}).
            path_prefix: String prefix for logging the path of the setting/section.
        """
        applied_count = 0
        skipped_validation = 0
        skipped_migration = 0
        coercion_warnings = 0
        dynamic_added = 0
        processed_keys = set()
        is_current_level_dynamic = not bool(current_schema_level)

        log.debug(
            f"Applying values at level '{path_prefix or 'root'}' (Migration: {allow_migration}, IgnoreUnknown: {ignore_unknown}, Dynamic Level: {is_current_level_dynamic}, Loaded Schema: {loaded_schema_level is not None})..."
        )

        # Iterate through the items defined in the *current instance* structure at this level
        for name, current_item in current_container.items():
            full_path = f"{path_prefix}{name}"

            # --- Process schema-defined ConfigSettings ---
            if isinstance(current_item, ConfigSetting):
                current_schema = current_item.schema

                if name in loaded_values_level:
                    processed_keys.add(name)
                    loaded_value = loaded_values_level[name]
                    value_to_validate = loaded_value
                    source_type_str = None

                    # --- Type Coercion Logic ---
                    if loaded_schema_level and name in loaded_schema_level:
                        loaded_item_schema_info = loaded_schema_level.get(name, {})
                        if isinstance(loaded_item_schema_info, dict):
                            loaded_type_str = loaded_item_schema_info.get("type")
                            source_type_str = loaded_type_str
                            if (
                                loaded_type_str
                                and loaded_type_str != current_schema.type_str
                            ):
                                log.warning(
                                    f"Type mismatch for '{full_path}': Instance expects '{current_schema.type_str}', file had '{loaded_type_str}'. Attempting coercion..."
                                )
                                coerced_value = _try_coerce(
                                    loaded_value,
                                    current_schema.type,
                                    source_type_str=loaded_type_str,
                                )
                                if coerced_value is not loaded_value:
                                    log.info(
                                        f"Coerced '{full_path}' value from {type(loaded_value).__name__} to {type(coerced_value).__name__}."
                                    )
                                    value_to_validate = coerced_value
                                else:
                                    log.warning(
                                        f"Coercion from '{loaded_type_str}' to '{current_schema.type_str}' did not succeed for '{full_path}' (value: {loaded_value!r}). Proceeding with original value."
                                    )
                                    coercion_warnings += 1
                        else:
                            log.debug(f"No type information found in loaded schema for '{full_path}'. Skipping coercion.")

                    # --- Validation against *instance* schema ---
                    try:
                        current_item.value = value_to_validate
                        applied_count += 1
                        log.debug(f"Successfully applied value for '{full_path}': {current_item.value!r}")
                    except ValidationError as e:
                        skipped_validation += 1
                        log.warning(f"Validation failed for '{full_path}' with value '{value_to_validate!r}' (original loaded: '{loaded_value!r}'): {e}. RESETTING to instance default.")
                        try:
                            current_item.value = current_schema.default_value
                        except ValidationError as e_default:
                            log.error(f"CRITICAL: Default value for '{full_path}' is invalid: {e_default}.")
                else: # Name not in loaded values
                    try:
                         current_item.value = current_schema.default_value
                    except ValidationError: pass
                    log.debug(f"'{full_path}' not found in loaded values. Using instance default: {current_item.value!r}")

            # --- Process schema-defined ConfigSections ---
            elif isinstance(current_item, ConfigSection):
                processed_keys.add(name)
                nested_loaded_values = loaded_values_level.get(name)
                nested_loaded_schema = None

                if loaded_schema_level and isinstance(loaded_schema_level.get(name), dict):
                     nested_loaded_schema_section = loaded_schema_level.get(name, {})
                     nested_loaded_schema = nested_loaded_schema_section.get("schema")
                     if not isinstance(nested_loaded_schema, dict):
                          nested_loaded_schema = None

                if isinstance(nested_loaded_values, Mapping):
                    log.debug(f"Recursing into section '{full_path}'...")
                    self._apply_and_migrate_values(
                        current_container=current_item._settings,
                        current_schema_level=current_schema_level.get(name, {}).get("schema", {}),
                        loaded_values_level=nested_loaded_values,
                        loaded_schema_level=nested_loaded_schema,
                        allow_migration=allow_migration,
                        ignore_unknown=ignore_unknown,
                        path_prefix=f"{full_path}.",
                    )
                elif name in loaded_values_level:
                    log.warning(f"Expected dictionary/mapping for section '{full_path}' in loaded values, but got {type(nested_loaded_values).__name__}. Skipping section.")
                else:
                    log.debug(f"Section '{full_path}' not found in loaded values. Using instance defaults.")
                    self._apply_and_migrate_values(
                        current_container=current_item._settings,
                        current_schema_level=current_schema_level.get(name, {}).get("schema", {}),
                        loaded_values_level={},
                        loaded_schema_level=None,
                        allow_migration=allow_migration,
                        ignore_unknown=ignore_unknown,
                        path_prefix=f"{full_path}.",
                    )
            # --- Handle pre-existing dynamic keys (less likely) ---
            elif is_current_level_dynamic and name in loaded_values_level:
                  processed_keys.add(name)
                  current_container[name] = loaded_values_level[name]
                  log.debug(f"Applied update to existing dynamic key '{full_path}'.")
                  applied_count += 1

        # --- Check for keys in loaded_values that are NOT in the instance structure at this level ---
        unknown_or_migrated_keys = set(loaded_values_level.keys()) - processed_keys
        skipped_unknown = 0
        for key in unknown_or_migrated_keys:
            full_unknown_path = f"{path_prefix}{key}"
            unknown_value = loaded_values_level[key]

            if is_current_level_dynamic:
                log.info(f"Dynamically adding key '{full_unknown_path}' = {unknown_value!r} to section.")
                current_container[key] = unknown_value
                dynamic_added += 1
            elif allow_migration:
                skipped_migration += 1
                log.warning(f"Migration/Skip: Item '{full_unknown_path}' (value: {unknown_value!r}) loaded from file is not present in current instance version ({self.version}). Skipping.")
            elif not ignore_unknown:
                log.error(f"Unknown item '{full_unknown_path}' found in input data for non-dynamic section/level and ignore_unknown=False.")
                raise SettingNotFoundError(f"Unknown setting/section encountered: '{full_unknown_path}'")
            else:
                skipped_unknown += 1
                log.warning(f"Item '{full_unknown_path}' found in loaded file/data but not defined in current instance schema level. Ignoring (ignore_unknown=True).")

        summary_parts = []
        if applied_count: summary_parts.append(f"Applied/Updated: {applied_count}")
        if dynamic_added: summary_parts.append(f"Dynamic Added: {dynamic_added}")
        if skipped_validation: summary_parts.append(f"Skipped (validation): {skipped_validation}")
        if skipped_migration: summary_parts.append(f"Skipped (migration/unknown): {skipped_migration}")
        if skipped_unknown: summary_parts.append(f"Skipped (ignored unknown): {skipped_unknown}")
        if coercion_warnings: summary_parts.append(f"Coercion Warnings: {coercion_warnings}")

        if summary_parts:
            log.info(f"Value application finished for level '{path_prefix or 'root'}'. " + ", ".join(summary_parts) + ".")
        else:
            log.debug(f"Value application finished for level '{path_prefix or 'root'}'. No changes or issues.")


    def save(
        self,
        filepath: typing.Optional[typing.Union[str, Path]] = None,
        mode: str = "values",
    ) -> None:
        """
        Saves the configuration using the configured handler and specified mode. Handles nesting.

        Args:
            filepath: Optional path to save to. Overrides the instance's config_path.
            mode: Specifies what to save.
                  - 'values': Saves the current configuration key-value pairs, prepended
                              with a '__version__' key indicating the instance version.
                              The structure depends on the handler (e.g., JSON/YAML/TOML dict,
                              SQLite key-value).
                  - 'full': Saves the instance version, schema definition, and values using the
                            standard keys '__version__', '__schema__', and '__settings__'.

        Raises:
            HandlerError: If saving fails (no path, no handler, serialization, encryption).
            EncryptionError: If encryption specifically fails.
            ValueError: If an invalid `mode` is provided.
        """
        save_path = Path(filepath) if filepath else self._config_path
        current_handler = self._handler

        if not save_path:
            raise HandlerError("No configuration file path specified for saving.")

        if not current_handler:
            log.warning(f"No handler configured, attempting to find handler for save path: {save_path}")
            try:
                current_handler = get_handler(save_path, fernet=self._fernet)
                self._handler = current_handler # Store if successful
                log.info(f"Dynamically initialized handler '{type(current_handler).__name__}' for save.")
            except (HandlerError, ImportError) as e:
                raise HandlerError(f"No valid handler available or could be initialized for the path: {save_path}. Error: {e}")

        if mode not in ["values", "full"]:
            raise ValueError(
                f"Invalid save mode: '{mode}'. Must be 'values' or 'full'."
            )

        log.info(
            f"Saving configuration to: {save_path} using {current_handler.__class__.__name__} (mode: {mode})"
        )

        # --- Prepare standard payload for the handler ---
        # The handler is responsible for constructing the final output
        # based on the mode and these components, using the standard keys.
        config_values = self.get_config_dict()
        schema_definition = self.get_instance_schema_definition()

        standard_handler_payload = {
            "instance_version": self.version,
            "schema_definition": schema_definition,
            "config_values": config_values,
            # Provide the standard keys to the handler
            "__version_key__": self.VERSION_KEY,
            "__schema_key__": self.SCHEMA_KEY,
            "__values_key__": self.VALUES_KEY,
        }

        # Log the INTENDED structure for clarity (handler must implement this)
        if mode == "full":
            log.debug(f"Requesting handler to save 'full' structure with keys: '{self.VERSION_KEY}', '{self.SCHEMA_KEY}', '{self.VALUES_KEY}'.")
        elif mode == "values":
            log.debug(f"Requesting handler to save 'values' structure with key '{self.VERSION_KEY}' prepended to config values.")

        try:
            # --- Call handler's save method ---
            # Pass the standard payload and mode. The handler MUST now interpret these
            # correctly to produce the desired output file format using the specified keys.
            current_handler.save(save_path, data=standard_handler_payload, mode=mode)

            # Update internal path if saved to a new location
            if filepath and save_path != self._config_path:
                 self._config_path = save_path
                 log.info(f"Default config path updated to: {self._config_path}")

        except (HandlerError, EncryptionError, ValueError) as e:
            log.error(f"Failed to save configuration to {save_path} (mode={mode}): {e}")
            raise
        except Exception as e:
            log.error(
                f"An unexpected error occurred during saving to {save_path} (mode={mode}): {e}",
                exc_info=True,
            )
            raise HandlerError(f"Unexpected error saving configuration: {e}") from e


    # --- Public Data Access Methods ---

    def get_instance_schema_definition(self) -> dict:
        """Returns the schema definition used by this ConfigGuard instance (excludes version key)."""
        return copy.deepcopy(self._instance_schema_definition)


    def get_config_dict(self) -> dict:
        """
        Returns the current configuration values as a potentially nested dictionary.
        Includes dynamically added keys within dynamic sections.
        Does NOT include the '__version__' key itself.
        """
        config_dict = {}
        for name, item in self._settings.items():
            if isinstance(item, ConfigSetting):
                config_dict[name] = item.value
            elif isinstance(item, ConfigSection):
                config_dict[name] = item.get_config_dict()
        return config_dict

    def export_schema_with_values(self) -> dict:
        """
        Exports the *current* state (instance schema + values, including nested structures
        and dynamic keys) using the standard '__version__', '__schema__', '__settings__' keys.

        Returns:
            A dictionary containing '__version__', '__schema__', and '__settings__'.
            The '__settings__' dict maps names to {'schema': ..., 'value': ...} structures.
            For dynamic keys within dynamic sections, 'schema' will indicate its dynamic nature.
        """
        log.debug("Recursively exporting current instance schema with values...")
        settings_export = {}
        self._export_level(self._settings, settings_export)

        # Construct the final export dictionary using the standard keys
        full_export = {
            self.VERSION_KEY: self.version,
            self.SCHEMA_KEY: self.get_instance_schema_definition(),
            self.VALUES_KEY: settings_export,
        }
        log.debug(f"Generated export for instance version {self.version}.")
        return full_export

    def _export_level(
        self,
        container: typing.Dict[str, typing.Union[ConfigSetting, ConfigSection, typing.Any]],
        export_target: dict
    ) -> None:
        """Recursive helper for export_schema_with_values."""
        for name, item in container.items():
            if isinstance(item, ConfigSetting):
                export_target[name] = {
                    "schema": item.schema.to_dict(),
                    "value": item.value,
                }
            elif isinstance(item, ConfigSection):
                nested_values_export = {}
                self._export_level(item._settings, nested_values_export)
                export_target[name] = {
                    "schema": item.get_schema_dict(),
                    "value": nested_values_export,
                }
            else: # Dynamically added values
                 export_target[name] = {
                      "schema": {
                           "type": f"dynamic ({type(item).__name__})",
                           "help": "Dynamically added value.",
                           "nullable": True,
                           "default": None
                      },
                      "value": item
                 }


    def import_config(self, data: Mapping, ignore_unknown: bool = True) -> None:
        """
        Imports configuration *values* from a potentially nested dictionary,
        validating against the instance schema and adding keys to dynamic sections.

        The input dictionary `data` is expected to contain only the configuration
        values structure, potentially including a `__version__` key which will be ignored
        during the import process (version is determined by the instance).

        Args:
            data: A dictionary (potentially nested) of {setting_name: value} or {section_name: {sub_setting: value}}.
                  May optionally contain a `__version__` key, which is ignored.
            ignore_unknown: If True (default), ignores keys/sections in `data` not present in the instance schema,
                            UNLESS the target section is dynamic (defined with schema: {}), in which case
                            keys from `data` will be added to the section.
                            If False, raises SettingNotFoundError for unknown keys/sections in non-dynamic parts.
        """
        if not isinstance(data, Mapping):
            raise TypeError(
                f"Input data for import_config must be a dictionary or mapping, got {type(data).__name__}"
            )

        # Create a copy excluding the version key, if present, to avoid processing it as a setting
        values_to_import = {k: v for k, v in data.items() if k != self.VERSION_KEY}

        log.info(
            f"Importing configuration values from dictionary ({len(values_to_import)} top-level items processed, ignore_unknown={ignore_unknown})..."
        )
        try:
            self._apply_and_migrate_values(
                current_container=self._settings,
                current_schema_level=self._instance_schema_definition,
                loaded_values_level=values_to_import, # Use the filtered data
                loaded_schema_level=None, # Import only deals with values
                allow_migration=False, # Import is not migration
                ignore_unknown=ignore_unknown, # Pass the flag
                path_prefix="",
            )

        except ValidationError as e:
            log.error(
                f"Validation errors occurred during import. See previous warnings. Last error detail: {e}"
            )
            raise
        except SettingNotFoundError as e:
            log.error(f"Import failed due to unknown setting/section: {e}")
            raise
        except Exception as e:
            log.error(f"Unexpected error during dictionary import: {e}", exc_info=True)
            raise HandlerError(f"Unexpected error during dictionary import: {e}") from e

        log.info("Dictionary import finished.")


    # --- Magic methods (No changes needed) ---

    def __getattr__(self, name: str) -> typing.Any:
        if name.startswith("_"):
            return super().__getattribute__(name)

        is_schema_access = name.startswith("sc_")
        actual_name = name[3:] if is_schema_access else name

        if actual_name in self._settings:
            item = self._settings[actual_name]
            if is_schema_access:
                if isinstance(item, ConfigSetting):
                    return item.schema
                elif isinstance(item, ConfigSection):
                    return item.get_schema_dict()
            elif isinstance(item, ConfigSetting):
                return item.value
            elif isinstance(item, ConfigSection):
                return item
        else:
            if hasattr(super(), '__getattribute__'):
                 try:
                      return super().__getattribute__(name)
                 except AttributeError:
                      pass

            prefix = "schema attribute" if is_schema_access else "attribute or setting/section"
            raise AttributeError(
                f"'{type(self).__name__}' object has no {prefix} '{name}'. Available top-level items: {list(self._settings.keys())}"
            ) from None


    def __setattr__(self, name: str, value: typing.Any) -> None:
        if name.startswith("sc_"):
            raise AttributeError("Cannot set schema attributes directly (use 'config.sc_name' to access).")

        known_internals = {
            "_settings", "_raw_instance_schema", "_instance_schema_definition", "version",
            "_config_path", "_handler", "_fernet", "_autosave", "loaded_file_version",
            "VERSION_KEY", "SCHEMA_KEY", "VALUES_KEY", "SECTION_TYPE_KEY" # Add constants
        }
        if name.startswith("_") or name in known_internals or hasattr(type(self), name):
            super().__setattr__(name, value)
        elif name in self._settings and isinstance(self._settings[name], ConfigSetting):
            setting = self._settings[name]
            try:
                setting.value = value
            except ValidationError as e:
                raise e
        elif name in self._settings and isinstance(self._settings[name], ConfigSection):
            raise AttributeError(
                f"Cannot assign directly to section '{name}'. Modify settings/keys within the section."
            )
        else:
            raise AttributeError(
                f"Cannot set attribute '{name}'. It's not a defined top-level setting or internal attribute. Available: {list(self._settings.keys())}"
            )


    def __getitem__(self, key: str) -> typing.Any:
        is_schema_access = key.startswith("sc_")
        actual_key = key[3:] if is_schema_access else key

        if actual_key in self._settings:
            item = self._settings[actual_key]
            if is_schema_access:
                if isinstance(item, ConfigSetting):
                    return item.schema
                elif isinstance(item, ConfigSection):
                    return item.get_schema_dict()
            elif isinstance(item, ConfigSetting):
                return item.value
            elif isinstance(item, ConfigSection):
                return item
        else:
            prefix = "Schema for setting/section" if is_schema_access else "Setting or section"
            raise SettingNotFoundError(f"{prefix} '{actual_key}' not found. Available: {list(self._settings.keys())}")


    def __setitem__(self, key: str, value: typing.Any) -> None:
        if key.startswith("sc_"):
            raise KeyError("Cannot set schema items directly (use config['sc_name'] to access).")

        if key in self._settings:
            item = self._settings[key]
            if isinstance(item, ConfigSetting):
                try:
                    item.value = value
                except ValidationError as e:
                    raise e
            elif isinstance(item, ConfigSection):
                 raise TypeError(
                    f"Cannot assign directly to section '{key}'. Modify settings/keys within the section."
                )
        else:
            raise SettingNotFoundError(
                f"Setting '{key}' not found. Cannot set undefined top-level settings. Available: {list(self._settings.keys())}"
            )


    def __delitem__(self, key: str) -> None:
        raise TypeError("Deleting configuration settings or sections is not supported.")


    def __iter__(self) -> typing.Iterator[str]:
        return iter(self._settings.keys())


    def __len__(self) -> int:
        return len(self._settings)


    def __contains__(self, key: object) -> bool:
        return isinstance(key, str) and key in self._settings


    def __repr__(self) -> str:
        path_str = f"'{self._config_path}'" if self._config_path else "None"
        handler_name = self._handler.__class__.__name__ if self._handler else "None"
        encrypted_str = ", encrypted" if hasattr(self._handler, '_fernet') and getattr(self._handler, '_fernet', None) else ""
        num_items = len(self._settings)
        item_types = {"settings": 0, "sections": 0}
        for item in self._settings.values():
            if isinstance(item, ConfigSetting): item_types["settings"] += 1
            elif isinstance(item, ConfigSection): item_types["sections"] += 1

        return (
            f"<{type(self).__name__}(version='{self.version}', config_path={path_str}, "
            f"handler='{handler_name}', items={num_items} "
            f"(settings={item_types['settings']}, sections={item_types['sections']})"
            f"{encrypted_str})>"
        )

