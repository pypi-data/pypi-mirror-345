# Project: ConfigGuard
# File: handlers/base.py
# Author: ParisNeo with Gemini 2.5
# Date: 2025-05-04 (Updated docs for standard keys)
# Description: Abstract base class definition for ConfigGuard storage handlers.
#              Defines the required interface for loading and saving configuration data,
#              potentially handling encryption.

import abc
import typing
from pathlib import Path


# Define the structured dictionary format returned by load
class LoadResult(typing.TypedDict):
    version: typing.Optional[str] # Version from __version__ or legacy 'version'
    schema: typing.Optional[dict] # Schema from __schema__ or legacy 'schema'
    values: dict                  # Values from __settings__ or root object


class StorageHandler(abc.ABC):
    """
    Abstract base class for all configuration storage handlers in ConfigGuard.

    Concrete handlers must implement the `load` and `save` methods to interact
    with specific storage formats (e.g., JSON, YAML, TOML, Database). They should
    also handle encryption and decryption internally if a Fernet instance is
    provided during initialization.
    """

    def __init__(self, fernet: typing.Optional[typing.Any] = None) -> None:
        """
        Initializes the storage handler.

        Args:
            fernet: An optional initialized Fernet instance from the 'cryptography' library.
                    If provided, the handler MUST use it to encrypt data before saving
                    and decrypt data after loading from the physical storage. If None,
                    data is saved/loaded in plain text.
        """
        self._fernet = fernet

    @abc.abstractmethod
    def load(self, filepath: Path) -> LoadResult:
        """
        Load configuration data from the specified file path.

        Implementations must handle reading the file format correctly. If the handler
        was initialized with a Fernet instance (`self._fernet`), this method MUST
        first read the raw bytes, then attempt decryption using `self._decrypt`,
        and finally parse the decrypted data according to the storage format.

        The method should intelligently detect the file structure:
        1. Check for the standard 'full' save format using keys defined in the
           `ConfigGuard` class constants (e.g., `__version__`, `__schema__`, `__settings__`).
        2. Check for the legacy 'full' save format ('version', 'schema', 'values').
        3. Check if the root structure contains just `__version__` alongside other keys
           (indicating a standard 'values' save).
        4. If none of the above, assume the entire loaded structure represents the
           configuration values (legacy 'values' save).

        Args:
            filepath: The absolute or relative Path object pointing to the configuration file.

        Returns:
            A LoadResult dictionary containing:
            - 'version': The version string found (using standard or legacy keys), or None.
            - 'schema': The schema dictionary found (using standard or legacy keys), or None.
            - 'values': A dictionary containing the loaded configuration values. This key MUST
                        always be present, returning an empty dict if the file is empty or
                        only contains metadata.

        Raises:
            FileNotFoundError: If the file specified by `filepath` does not exist.
            HandlerError: If loading, parsing, or data structure validation fails.
            EncryptionError: If decryption fails (only applicable if initialized with Fernet).
        """
        raise NotImplementedError("Subclasses must implement the load method.")

    @abc.abstractmethod
    def save(self, filepath: Path, data: dict, mode: str = "values") -> None:
        """
        Save configuration data to the specified file path using standard keys.

        Implementations must handle serializing the data according to the storage format.
        If the handler was initialized with a Fernet instance (`self._fernet`), this method
        MUST first serialize the appropriate data to bytes, then encrypt these bytes using
        `self._encrypt`, and finally write the encrypted bytes to the file.

        The structure of the saved file depends on the `mode` and uses standard keys
        provided in the `data` payload.

        Args:
            filepath: The absolute or relative Path object pointing to the target file.
                      The handler should ensure parent directories exist.
            data: A dictionary containing the full data payload from ConfigGuard.
                  Expected keys: 'instance_version', 'schema_definition', 'config_values',
                  '__version_key__', '__schema_key__', '__values_key__'.
            mode: Specifies what to save.
                  - 'values': Saves the configuration key-value pairs (`data['config_values']`)
                              prepended with the version key (`data['__version_key__']`) and
                              its value (`data['instance_version']`). The exact file structure
                              depends on the handler (e.g., flat dict for JSON/YAML/TOML,
                              special key in SQLite).
                  - 'full': Saves the instance version, schema definition, and values using the
                            keys provided in the payload (`__version_key__`, `__schema_key__`, `__values_key__`)
                            and their corresponding data values from the `data` dict.

        Raises:
            HandlerError: If saving, serialization, or file writing fails.
            EncryptionError: If encryption fails (only applicable if initialized with Fernet).
            ValueError: If an unsupported `mode` is provided or required keys are missing in `data`.
        """
        raise NotImplementedError("Subclasses must implement the save method.")

    def _encrypt(self, data_bytes: bytes) -> bytes:
        """
        Encrypts the provided bytes using the stored Fernet instance.

        Internal helper method for concrete handlers.

        Args:
            data_bytes: The plain bytes to encrypt.

        Returns:
            The encrypted bytes.

        Raises:
            RuntimeError: If called when no Fernet instance was provided during initialization.
            EncryptionError: If the encryption process fails.
        """
        if not self._fernet:
            raise RuntimeError(
                "Attempted to call _encrypt without a valid Fernet instance."
            )
        from ..exceptions import EncryptionError # Local import

        try:
            return self._fernet.encrypt(data_bytes)
        except Exception as e:
            raise EncryptionError(f"Handler encryption failed: {e}") from e

    def _decrypt(self, encrypted_bytes: bytes) -> bytes:
        """
        Decrypts the provided bytes using the stored Fernet instance.

        Internal helper method for concrete handlers.

        Args:
            encrypted_bytes: The encrypted bytes read from the file.

        Returns:
            The original plain bytes.

        Raises:
            RuntimeError: If called when no Fernet instance was provided during initialization.
            EncryptionError: If the decryption process fails (e.g., invalid token, wrong key).
        """
        if not self._fernet:
            raise RuntimeError(
                "Attempted to call _decrypt without a valid Fernet instance."
            )
        from ..exceptions import EncryptionError # Local import

        try:
            return self._fernet.decrypt(encrypted_bytes)
        except Exception as e:
            raise EncryptionError(f"Handler decryption failed: {e}") from e
