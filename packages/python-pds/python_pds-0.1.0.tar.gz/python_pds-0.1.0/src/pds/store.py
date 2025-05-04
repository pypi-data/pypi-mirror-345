import json
import zstandard as zstd
import struct
import tempfile
import shutil
import os
import uuid
import random
import io
from typing import Any, List, Dict, Optional, Tuple, Union


class PDS:
    """
    Portable Data Store (PDS) class - Revised Format v2 (Keys Index at End)
    Handles zstandard compression with optional dictionary.
    """

    # Constants for struct packing
    _UINT4 = "<I"
    _INT4 = "<i"
    _UINT8 = "<Q"

    # Constants for dictionary length field
    _ZSTD_NO_DICT = -1
    _NO_COMPRESSION = -2

    # Default sample size for dictionary training
    _DEFAULT_DICT_SAMPLE_SIZE = 2 * 1024 * 1024 * 1024  # 2 GB
    _DEFAULT_DICT_SIZE = 112640  # ~110 KB zstd default

    def __init__(
        self,
        compression_mode: str = "zstd_dict",
        dict_sample_size: int = _DEFAULT_DICT_SAMPLE_SIZE,
        dict_target_size: int = _DEFAULT_DICT_SIZE,
    ):
        self.meta_data: Dict[str, Any] = {}
        self.keys_index: Dict[str, Any] = {}
        self.value_locations: Dict[str, Dict[str, Any]] = {}

        if compression_mode not in ["zstd_dict", "zstd_no_dict", "none"]:
            raise ValueError("Invalid compression_mode.")
        # User's *intended* mode for the *next* save
        self._intended_save_compression_mode: str = compression_mode
        # Training parameters
        self._dict_sample_size: int = dict_sample_size
        self._dict_target_size: int = dict_target_size

        # --- State related to an opened file or the last save ---
        self._opened_file_handle: Optional[io.BufferedReader] = None
        self._filename: Optional[str] = None
        # Compression mode *of the currently open file or last saved file*
        self._active_compression_mode: str = "none"
        # Dictionary bytes *of the currently open file or last saved file*
        self._active_zstd_dictionary_bytes: Optional[bytes] = None
        self._values_start_offset: int = 0
        # --- End File/Save State ---

        # Temporary directory management
        self._temp_dir_path: Optional[str] = None
        self._create_temp_dir()

    # --- Helper Methods ---
    def _create_temp_dir(self):
        if self._temp_dir_path is None or not os.path.exists(self._temp_dir_path):
            temp_dir_name = f"pds_temp_{uuid.uuid4().hex[:8]}"
            base_temp_dir = tempfile.gettempdir()
            self._temp_dir_path = os.path.join(base_temp_dir, temp_dir_name)
            os.makedirs(self._temp_dir_path, exist_ok=True)

    def _clean_temp_dir(self):
        if self._temp_dir_path and os.path.exists(self._temp_dir_path):
            try:
                shutil.rmtree(self._temp_dir_path)
            except OSError as e:
                print(
                    f"Warning: Could not remove temporary directory {self._temp_dir_path}: {e}"
                )
            finally:
                self._temp_dir_path = None

    def _get_nested_dict(
        self, keys_list: List[str], create_if_missing: bool = False
    ) -> Tuple[Dict, str]:
        if not keys_list:
            raise ValueError("keys_list cannot be empty.")
        current_level = self.keys_index
        for i, key in enumerate(keys_list[:-1]):
            node = current_level.get(key)
            if not isinstance(node, dict):
                if create_if_missing:
                    if node is not None:  # Path conflict if key exists but isn't a dict
                        raise TypeError(
                            f"Path conflict: Element '{key}' exists but is not a dictionary."
                        )
                    current_level[key] = {}
                    node = current_level[key]
                else:  # Not creating and node is missing or not a dict
                    if node is None:
                        raise KeyError(
                            f"Key path not found: {' -> '.join(keys_list[: i + 1])}"
                        )
                    else:
                        raise TypeError(
                            f"Invalid path: Element '{key}' is not a dictionary."
                        )
            current_level = node
        final_key = keys_list[-1]
        return current_level, final_key

    # --- Public API Methods ---
    def get_keys(self) -> Union[List, Dict]:
        return json.loads(json.dumps(self.keys_index))  # Cheap deep copy

    def set_meta_data(self, meta_data: Dict[str, Any]):
        if not isinstance(meta_data, dict):
            raise TypeError("Metadata must be a dictionary.")
        try:
            json.dumps(meta_data)
        except TypeError as e:
            raise TypeError(f"Metadata is not JSON serializable: {e}")
        self.meta_data = meta_data

    def add_key(self, keys_list: List[str], value: Any):
        if not keys_list:
            raise ValueError("keys_list cannot be empty.")
        try:
            value_bytes = json.dumps(value, separators=(",", ":")).encode("utf-8")
        except TypeError as e:
            raise TypeError(
                f"Value for key '{' -> '.join(keys_list)}' is not JSON serializable: {e}"
            )

        # Compress temporary data simply (no dict)
        cctx = zstd.ZstdCompressor(level=3)
        compressed_value_bytes = cctx.compress(value_bytes)
        value_id = uuid.uuid4().hex
        self._create_temp_dir()  # Ensure temp dir exists
        if not self._temp_dir_path:
            raise IOError("Temporary directory path is not set.")
        temp_filename = os.path.join(self._temp_dir_path, f"{value_id}.zst")

        try:
            with open(temp_filename, "wb") as f_temp:
                f_temp.write(compressed_value_bytes)
        except IOError as e:
            raise IOError(f"Failed to write temporary file {temp_filename}: {e}")

        # Remove existing key/value reference if it exists, but don't remove from index yet
        try:
            self.remove_key(keys_list, _remove_from_index=False)
        except KeyError:
            pass  # Key didn't exist, ignore

        # Add to index and value locations
        parent_dict, final_key = self._get_nested_dict(
            keys_list, create_if_missing=True
        )
        parent_dict[final_key] = value_id
        self.value_locations[value_id] = {"location": "temp", "filename": temp_filename}

    # --- Internal Read/Decompress Helpers ---
    def _read_value_data_bytes(self, value_id: str) -> bytes:
        if value_id not in self.value_locations:
            raise KeyError(f"Value ID '{value_id}' not found in value locations.")
        loc_info = self.value_locations[value_id]
        location_type = loc_info.get("location")

        if location_type == "temp":
            temp_filename = loc_info.get("filename")
            if not temp_filename:
                raise KeyError(f"Missing filename for temp value ID '{value_id}'.")
            try:
                with open(temp_filename, "rb") as f_temp:
                    return f_temp.read()
            except FileNotFoundError:
                raise KeyError(
                    f"Temp file '{temp_filename}' not found for value ID '{value_id}'."
                )
            except IOError as e:
                raise IOError(f"Failed to read temp file {temp_filename}: {e}")

        elif location_type == "inplace":
            if not self._opened_file_handle or self._opened_file_handle.closed:
                raise ValueError(
                    f"PDS file '{self._filename}' not open for reading inplace value ID '{value_id}'."
                )
            try:
                offset = loc_info.get("offset")  # Offset should point to data start
                length = loc_info.get("length")  # Length of compressed data
                if offset is None or length is None:
                    raise KeyError(
                        f"Missing offset ({offset}) or length ({length}) for inplace value ID '{value_id}'."
                    )

                # Seek to data start and read known length
                self._opened_file_handle.seek(offset)
                value_data = self._opened_file_handle.read(length)
                if len(value_data) != length:
                    raise IOError(
                        f"Could not read value data ({length} bytes required) for ID '{value_id}' starting at offset {offset}."
                    )
                return value_data
            except IOError as e:
                raise IOError(f"Failed to read inplace value for ID '{value_id}': {e}")
        else:
            raise ValueError(
                f"Unknown location type '{location_type}' for value ID '{value_id}'."
            )

    def _decompress_value_data(
        self,
        value_data_bytes: bytes,
        location: str,
        value_id_for_error: str = "unknown",
    ) -> bytes:
        """Decompresses value data bytes based on location and active file state."""
        if location == "temp":
            # Temp files always compressed with zstd, no dictionary
            dctx = zstd.ZstdDecompressor()
            try:
                return dctx.decompress(value_data_bytes)
            except zstd.ZstdError as e:
                raise zstd.ZstdError(
                    f"Failed to decompress temp value data for ID '{value_id_for_error}': {e}"
                ) from e
        elif location == "inplace":
            # Use the compression mode associated with the file/last save
            mode = self._active_compression_mode
            if mode == "none":
                return value_data_bytes  # No decompression needed
            elif mode == "zstd_no_dict":
                dctx = zstd.ZstdDecompressor()
                try:
                    return dctx.decompress(value_data_bytes)
                except zstd.ZstdError as e:
                    raise zstd.ZstdError(
                        f"Failed to decompress inplace value (no dict) for ID '{value_id_for_error}': {e}"
                    ) from e
            elif mode == "zstd_dict":
                # Get the dictionary bytes associated with the file/last save
                dict_bytes = self._active_zstd_dictionary_bytes
                if not dict_bytes:
                    raise ValueError(
                        f"Active mode is 'zstd_dict' but no dictionary loaded/available for ID '{value_id_for_error}'."
                    )
                try:
                    # Create dictionary object on the fly from bytes
                    zdict = zstd.ZstdCompressionDict(dict_bytes)
                    dctx = zstd.ZstdDecompressor(dict_data=zdict)
                    return dctx.decompress(value_data_bytes)
                except ValueError as e:  # Error creating ZstdCompressionDict
                    raise ValueError(
                        f"Error initializing decompressor dictionary for ID '{value_id_for_error}': {e}"
                    ) from e
                except (
                    zstd.ZstdError
                ) as e:  # Decompression error (includes dictionary mismatch)
                    raise zstd.ZstdError(
                        f"Failed to decompress inplace value (with dict) for ID '{value_id_for_error}': {e}"
                    ) from e
            else:
                raise ValueError(
                    f"Unknown active compression mode '{mode}' for inplace value ID '{value_id_for_error}'."
                )
        else:
            raise ValueError(f"Unknown location type '{location}' for decompression.")

    # --- Public Read/Remove Methods ---
    def read_key(self, keys_list: List[str]) -> Any:
        if not keys_list:
            raise ValueError("keys_list cannot be empty.")
        key_path_str = " -> ".join(keys_list)
        try:
            parent_dict, final_key = self._get_nested_dict(keys_list)
            if final_key not in parent_dict:
                raise KeyError(f"Key not found: {key_path_str}")

            value_id = parent_dict[final_key]
            if not isinstance(value_id, str):
                raise TypeError(
                    f"Invalid data found at key path {key_path_str} (expected value ID string)."
                )
            if value_id not in self.value_locations:
                raise KeyError(
                    f"Value ID '{value_id}' (key: '{key_path_str}') not found in value locations map. PDS state inconsistent."
                )

            loc_info = self.value_locations[value_id]
            location_type = loc_info.get("location", "unknown")

            # Read the raw/compressed bytes
            value_data_bytes = self._read_value_data_bytes(value_id)
            # Decompress using the active state's settings
            decompressed_bytes = self._decompress_value_data(
                value_data_bytes, location_type, value_id
            )
            # Decode JSON
            return json.loads(decompressed_bytes.decode("utf-8"))

        except KeyError as e:
            raise KeyError(f"Failed to read key {key_path_str}: {e}")
        except TypeError as e:
            raise TypeError(
                f"Invalid key path or data structure for {key_path_str}: {e}"
            )
        except (ValueError, zstd.ZstdError, IOError) as e:
            raise type(e)(f"Error reading/processing value for key {key_path_str}: {e}")
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Failed to decode JSON for key {key_path_str}: {e.msg}", e.doc, e.pos
            )
        except Exception as e:
            raise RuntimeError(f"Unexpected error reading key {key_path_str}: {e}")

    def remove_key(self, keys_list: List[str], _remove_from_index=True):
        """Removes a key and its associated value reference/temp file."""
        if not keys_list:
            raise ValueError("keys_list cannot be empty.")
        key_path_str = " -> ".join(keys_list)
        try:
            parent_dict, final_key = self._get_nested_dict(keys_list)
            if final_key not in parent_dict:
                if _remove_from_index:
                    raise KeyError(f"Key not found for removal: {key_path_str}")
                else:
                    return  # Internal call, key not present, nothing to clean

            value_id = parent_dict.get(final_key)  # Use .get() for safety

            # Only proceed if it looks like a value ID we manage
            if isinstance(value_id, str) and value_id in self.value_locations:
                loc_info = self.value_locations[value_id]
                # Clean up temp file if applicable
                if loc_info.get("location") == "temp":
                    temp_filename = loc_info.get("filename")
                    if temp_filename and os.path.exists(temp_filename):
                        try:
                            os.remove(temp_filename)
                        except Exception as e:
                            print(
                                f"Warning: Failed to remove temp file {temp_filename}: {e}"
                            )
                # Always remove from value_locations map
                del self.value_locations[value_id]

            # Remove from the key index structure if requested
            if _remove_from_index:
                del parent_dict[final_key]
                # Optional: Cleanup empty parent dicts if desired
                # self._cleanup_empty_dicts(keys_list[:-1])

        except KeyError as e:
            if _remove_from_index:
                raise KeyError(
                    f"Key not found during removal attempt: {key_path_str} ({e})"
                )
        except TypeError as e:
            raise TypeError(
                f"Invalid key path/structure for removal: {key_path_str} ({e})"
            )

    def _cleanup_empty_dicts(self, keys_list_to_parent: List[str]):
        """Recursively removes empty dictionaries up the path (Optional)."""
        # (Implementation omitted for brevity, can be added if needed)
        pass

    # --- File Open Method ---
    def open(self, filename: str):
        """Opens an existing PDS file for reading."""
        # Reset state before opening
        self.dispose()  # Close previous file, clean temp dir etc.

        # Re-initialize core state, preserving user's intended *next* save settings
        intended_save_mode = self._intended_save_compression_mode
        sample_size = self._dict_sample_size
        target_size = self._dict_target_size
        self.__init__(
            compression_mode=intended_save_mode,
            dict_sample_size=sample_size,
            dict_target_size=target_size,
        )
        # Temp dir not needed just for opening

        try:
            f = open(filename, "rb")
        except FileNotFoundError:
            raise FileNotFoundError(f"PDS file not found: {filename}")
        except IOError as e:
            raise IOError(f"Could not open PDS file {filename}: {e}")

        self._opened_file_handle = f
        self._filename = filename
        print(f"DEBUG OPEN: Opened file {filename}")

        # Reset active state variables before reading from file
        self._active_compression_mode = "none"
        self._active_zstd_dictionary_bytes = None
        self._values_start_offset = 0
        self.meta_data = {}
        self.keys_index = {}
        self.value_locations = {}

        try:
            # 1. Read Metadata
            len_bytes = f.read(4)
            meta_data_length = struct.unpack(self._UINT4, len_bytes)[0]
            # Add sanity check for length
            MAX_META_SIZE = 50 * 1024 * 1024
            if meta_data_length > MAX_META_SIZE:
                raise ValueError(f"Metadata length ({meta_data_length}) exceeds limit.")
            print(f"DEBUG OPEN: Meta data length: {meta_data_length}")
            meta_data_bytes = f.read(meta_data_length)
            if len(meta_data_bytes) != meta_data_length:
                raise IOError("Could not read metadata.")
            self.meta_data = json.loads(meta_data_bytes.decode("utf-8"))
            print("DEBUG OPEN: Read metadata.")

            # 2. Read Dictionary Info
            len_bytes = f.read(4)
            dictionary_length_field = struct.unpack(self._INT4, len_bytes)[0]
            print(f"DEBUG OPEN: Dictionary length field: {dictionary_length_field}")

            if dictionary_length_field > 0:
                MAX_DICT_SIZE = 200 * 1024 * 1024
                if dictionary_length_field > MAX_DICT_SIZE:
                    raise ValueError(
                        f"Dictionary length ({dictionary_length_field}) exceeds limit."
                    )
                # Read the dictionary bytes
                dict_bytes = f.read(dictionary_length_field)
                if len(dict_bytes) != dictionary_length_field:
                    raise IOError("Could not read dictionary data.")
                # Validate dictionary bytes eagerly
                try:
                    _ = zstd.ZstdCompressionDict(dict_bytes)  # Validate structure
                    self._active_compression_mode = "zstd_dict"
                    self._active_zstd_dictionary_bytes = (
                        dict_bytes  # Store the validated bytes
                    )
                    print(
                        f"DEBUG OPEN: Read and validated dictionary ({dictionary_length_field} bytes). Mode set to 'zstd_dict'."
                    )
                except ValueError as e:
                    raise ValueError(f"Loaded dictionary data is invalid: {e}") from e
            elif dictionary_length_field == self._ZSTD_NO_DICT:
                self._active_compression_mode = "zstd_no_dict"
                print("DEBUG OPEN: Mode set to 'zstd_no_dict'.")
            elif dictionary_length_field == self._NO_COMPRESSION:
                self._active_compression_mode = "none"
                print("DEBUG OPEN: Mode set to 'none'.")
            else:
                raise ValueError(
                    f"Invalid dictionary_length value in file: {dictionary_length_field}"
                )

            # Store offset where value blocks START
            self._values_start_offset = f.tell()
            print(
                f"DEBUG OPEN: Values start offset recorded: {self._values_start_offset}"
            )

            # 3. Read Keys Index from End
            keys_compressed_bytes = b""
            keys_index_length = 0
            try:
                f.seek(0, os.SEEK_END)
                file_size = f.tell()
                print(f"DEBUG OPEN: Total file size: {file_size}")
                if file_size >= self._values_start_offset + 4:
                    f.seek(-4, os.SEEK_END)
                    keys_index_length_bytes = f.read(4)
                    keys_index_length = struct.unpack(
                        self._UINT4, keys_index_length_bytes
                    )[0]
                    print(
                        f"DEBUG OPEN: Keys index length (read from end): {keys_index_length}"
                    )

                    keys_data_start_offset = file_size - 4 - keys_index_length
                    if keys_index_length > 0:
                        if keys_data_start_offset < self._values_start_offset:
                            raise IOError(
                                f"Keys index data offset calculation error (start {keys_data_start_offset} < values_end {self._values_start_offset}). Length {keys_index_length} likely corrupt."
                            )
                        MAX_INDEX_SIZE = 500 * 1024 * 1024
                        if keys_index_length > MAX_INDEX_SIZE:
                            raise ValueError(
                                f"Keys index length ({keys_index_length}) exceeds limit."
                            )

                        f.seek(keys_data_start_offset)
                        keys_compressed_bytes = f.read(keys_index_length)
                        if len(keys_compressed_bytes) != keys_index_length:
                            raise IOError(
                                f"Could not read keys index data (expected {keys_index_length}, got {len(keys_compressed_bytes)})."
                            )
                        print(
                            f"DEBUG OPEN: Read keys index data ({keys_index_length} bytes) from offset {keys_data_start_offset}."
                        )
                    elif keys_index_length == 0:
                        print("DEBUG OPEN: Keys index length is 0. Index is empty.")
                    else:
                        pass  # Negative length is impossible for UINT4

                else:
                    print(
                        f"DEBUG OPEN: File size ({file_size}) suggests no keys index present. Assuming empty index."
                    )

            except (IOError, struct.error, ValueError) as e:
                raise IOError(
                    f"Error reading keys index structure from file end: {e}"
                ) from e

            # 4. Decompress and Process Keys Index
            self.keys_index = {}  # Reset before loading
            self.value_locations = {}  # Reset before loading
            if keys_compressed_bytes:
                try:
                    dctx_keys = zstd.ZstdDecompressor()
                    keys_bytes = dctx_keys.decompress(keys_compressed_bytes)
                    raw_keys_index_with_offsets = json.loads(keys_bytes.decode("utf-8"))
                    print("DEBUG OPEN: Decompressed and parsed keys index.")
                    self._process_loaded_keys(
                        raw_keys_index_with_offsets, self.keys_index
                    )
                    print("DEBUG OPEN: Processed keys index into internal structures.")
                except zstd.ZstdError as e:
                    raise zstd.ZstdError(f"Failed to decompress keys index: {e}") from e
                except json.JSONDecodeError as e:
                    raise json.JSONDecodeError(
                        f"Failed to decode JSON from keys index: {e.msg}", e.doc, e.pos
                    ) from e
                except (TypeError, ValueError) as e:
                    raise ValueError(
                        f"Error processing loaded keys index structure: {e}"
                    ) from e
            else:
                print("DEBUG OPEN: No keys index data to process (index is empty).")

            # File handle remains open at end of index or file

        except (
            struct.error,
            json.JSONDecodeError,
            zstd.ZstdError,
            IOError,
            ValueError,
            EOFError,
        ) as e:
            print(f"ERROR during open: {type(e).__name__}: {e}")
            self.dispose()
            raise e
        except Exception as e:
            print(f"UNEXPECTED ERROR during open: {type(e).__name__}: {e}")
            import traceback

            traceback.print_exc()
            self.dispose()
            raise

    # --- Helper for processing loaded keys ---
    def _process_loaded_keys(self, source_node: Any, target_node: Union[Dict, List]):
        """Recursively processes loaded keys, extracting offsets/lengths into value_locations."""
        if isinstance(source_node, dict):
            if not isinstance(target_node, dict):
                raise TypeError("Type mismatch: target expected dict.")
            for key, value in source_node.items():
                if isinstance(value, str) and value.startswith("|"):
                    try:
                        parts = value[1:].split(":")
                        offset = int(parts[0])
                        length = int(parts[1]) if len(parts) > 1 else None
                        if offset < self._values_start_offset:
                            print(
                                f"Warning: Offset {offset} for key '{key}' is before values start {self._values_start_offset}."
                            )
                        if length is None:
                            raise ValueError(
                                "Length missing in offset string"
                            )  # Require length now
                        if length < 0:
                            raise ValueError("Negative length found")

                        value_id = uuid.uuid4().hex
                        target_node[key] = value_id
                        self.value_locations[value_id] = {
                            "location": "inplace",
                            "offset": offset,
                            "length": length,
                        }
                    except (ValueError, TypeError, IndexError) as e:
                        raise ValueError(
                            f"Invalid offset:length format '{value}' for key '{key}': {e}."
                        )
                elif isinstance(value, (dict, list)):
                    target_node[key] = type(value)()  # Create empty dict or list
                    self._process_loaded_keys(value, target_node[key])
                else:
                    raise TypeError(
                        f"Unexpected data type '{type(value)}' for key '{key}'."
                    )
        elif isinstance(source_node, list):
            if not isinstance(target_node, list):
                raise TypeError("Type mismatch: target expected list.")
            for i, item in enumerate(source_node):
                if isinstance(item, str) and item.startswith("|"):
                    try:
                        parts = item[1:].split(":")
                        offset = int(parts[0])
                        length = int(parts[1]) if len(parts) > 1 else None
                        if offset < self._values_start_offset:
                            print(
                                f"Warning: Offset {offset} at index {i} is before values start {self._values_start_offset}."
                            )
                        if length is None:
                            raise ValueError("Length missing in offset string")
                        if length < 0:
                            raise ValueError("Negative length found")

                        value_id = uuid.uuid4().hex
                        target_node.append(value_id)
                        self.value_locations[value_id] = {
                            "location": "inplace",
                            "offset": offset,
                            "length": length,
                        }
                    except (ValueError, TypeError, IndexError) as e:
                        raise ValueError(
                            f"Invalid offset:length format '{item}' at index {i}: {e}."
                        )
                elif isinstance(item, (dict, list)):
                    new_node = type(item)()
                    target_node.append(new_node)
                    self._process_loaded_keys(item, new_node)
                else:
                    raise TypeError(
                        f"Unexpected data type '{type(item)}' at index {i}."
                    )
        else:
            raise TypeError(
                f"Keys index structure must be dict or list, found {type(source_node)}."
            )

    # --- Dictionary Training ---
    def _train_dictionary(self) -> Optional[bytes]:
        """Trains a zstd dictionary using a sample of current values."""
        # Use the instance's *intended* save mode for training decision
        if self._intended_save_compression_mode != "zstd_dict":
            return None

        sample_data = []
        current_sample_size = 0
        value_ids = list(self.value_locations.keys())
        random.shuffle(value_ids)
        print(
            f"Starting dictionary training. Target sample size: {self._dict_sample_size / (1024 * 1024):.2f} MB"
        )
        processed_count = 0
        skipped_count = 0

        for value_id in value_ids:
            if current_sample_size >= self._dict_sample_size:
                print(
                    f"Reached dictionary sample size limit ({current_sample_size / (1024 * 1024):.2f} MB) after {processed_count} values."
                )
                break
            try:
                loc_info = self.value_locations[value_id]
                location_type = loc_info.get("location")
                if not location_type:
                    skipped_count += 1
                    continue

                # Read raw/compressed bytes
                value_data_bytes = self._read_value_data_bytes(value_id)
                # Decompress using the *active* file/state settings
                decompressed_bytes = self._decompress_value_data(
                    value_data_bytes, location_type, value_id
                )

                sample_data.append(decompressed_bytes)
                current_sample_size += len(decompressed_bytes)
                processed_count += 1
            except (
                KeyError,
                IOError,
                zstd.ZstdError,
                ValueError,
                FileNotFoundError,
            ) as e:
                print(
                    f"Warning: Skipping value ID {value_id} during dictionary sampling: {type(e).__name__}: {e}"
                )
                skipped_count += 1
            except Exception as e:
                print(
                    f"Warning: Skipping value ID {value_id} during dictionary sampling (unexpected): {type(e).__name__}: {e}"
                )
                import traceback

                traceback.print_exc()
                skipped_count += 1

        if skipped_count > 0:
            print(f"Skipped {skipped_count} values during dictionary sampling.")
        if not sample_data:
            print(
                "Warning: No data available to train dictionary. Will save without dictionary."
            )
            return None  # Indicate training failed/yielded no dictionary

        try:
            print(
                f"Training dictionary with {len(sample_data)} samples, size {current_sample_size / (1024 * 1024):.2f} MB. Target dict size: {self._dict_target_size} bytes."
            )
            trained_dictionary = zstd.train_dictionary(
                dict_size=self._dict_target_size, samples=sample_data, level=5
            )
            # Extract bytes safely
            if hasattr(trained_dictionary, "as_bytes"):
                trained_dict_bytes = trained_dictionary.as_bytes()
            elif hasattr(trained_dictionary, "data"):
                trained_dict_bytes = trained_dictionary.data  # Older versions
            else:
                raise TypeError("Cannot extract bytes from trained dictionary object.")

            if not isinstance(trained_dict_bytes, bytes):
                raise TypeError("Extracted dictionary data is not bytes.")
            if len(trained_dict_bytes) == 0:
                print(
                    "Warning: Trained dictionary is empty. Will save without dictionary."
                )
                return None

            print(
                f"Dictionary training complete. Actual size: {len(trained_dict_bytes)} bytes."
            )
            return trained_dict_bytes
        except (zstd.ZstdError, TypeError, AttributeError, MemoryError) as e:
            print(
                f"Error during dictionary training: {type(e).__name__}: {e}. Will save without dictionary."
            )
            return None
        except Exception as e:
            print(
                f"Unexpected error during dictionary training: {type(e).__name__}: {e}. Will save without dictionary."
            )
            import traceback

            traceback.print_exc()
            return None

    # --- File Save Method ---
    def save(self, filename: str):
        final_file_handle = None
        # Determine the effective mode and dictionary for *this specific save operation*
        effective_save_mode = self._intended_save_compression_mode
        dictionary_bytes_for_this_save: Optional[bytes] = None

        try:
            # 1. Train Dictionary if intended mode requires it
            if effective_save_mode == "zstd_dict":
                dictionary_bytes_for_this_save = self._train_dictionary()
                if dictionary_bytes_for_this_save is None:
                    print(
                        "Dictionary training failed or yielded no dictionary. Falling back to 'zstd_no_dict' for this save."
                    )
                    effective_save_mode = "zstd_no_dict"

            # 2. Determine dictionary length field for header
            dictionary_length_field = self._NO_COMPRESSION  # Default 'none'
            if effective_save_mode == "zstd_no_dict":
                dictionary_length_field = self._ZSTD_NO_DICT
            elif effective_save_mode == "zstd_dict" and dictionary_bytes_for_this_save:
                dictionary_length_field = len(dictionary_bytes_for_this_save)
                if (
                    dictionary_length_field == 0
                ):  # Should have been caught by _train_dictionary, but safety
                    print(
                        "ERROR: Save mode 'zstd_dict' but dictionary is empty. Forcing 'zstd_no_dict'."
                    )
                    effective_save_mode = "zstd_no_dict"
                    dictionary_length_field = self._ZSTD_NO_DICT
                    dictionary_bytes_for_this_save = None
            elif (
                effective_save_mode == "zstd_dict"
                and not dictionary_bytes_for_this_save
            ):
                print(
                    "ERROR: Save mode 'zstd_dict' but no dictionary available. Forcing 'zstd_no_dict'."
                )
                effective_save_mode = "zstd_no_dict"
                dictionary_length_field = self._ZSTD_NO_DICT

            # 3. Prepare Value Compressor based on effective mode
            cctx_values = None
            if effective_save_mode == "zstd_no_dict":
                cctx_values = zstd.ZstdCompressor(level=5)
            elif effective_save_mode == "zstd_dict" and dictionary_bytes_for_this_save:
                try:
                    # Create compressor with the dictionary *for this save*
                    zdict_save = zstd.ZstdCompressionDict(
                        dictionary_bytes_for_this_save
                    )
                    cctx_values = zstd.ZstdCompressor(dict_data=zdict_save, level=5)
                except (ValueError, TypeError, zstd.ZstdError) as e:
                    print(
                        f"Error creating compressor with dictionary: {e}. Reverting save mode to 'none'."
                    )
                    effective_save_mode = "none"
                    dictionary_length_field = self._NO_COMPRESSION
                    dictionary_bytes_for_this_save = None
                    cctx_values = None

            # 4. Prepare Metadata Bytes
            final_meta_data_bytes = json.dumps(
                self.meta_data, separators=(",", ":")
            ).encode("utf-8")
            final_meta_data_len = len(final_meta_data_bytes)

            # === Write File Sequentially ===
            print(f"Writing final PDS file: {filename}")
            print(f"Effective save mode: {effective_save_mode}")
            if dictionary_bytes_for_this_save:
                print(
                    f"Using dictionary size: {len(dictionary_bytes_for_this_save)} bytes"
                )

            final_locations_map: Dict[str, Tuple[int, int]] = {}
            calculated_values_start_offset = 0
            temp_files_used_in_save = set()  # Track temp files successfully read

            with open(filename, "wb") as f_out:
                final_file_handle = f_out

                # Write Meta Block
                f_out.write(struct.pack(self._UINT4, final_meta_data_len))
                f_out.write(final_meta_data_bytes)

                # Write Dictionary Block Header & Data
                f_out.write(struct.pack(self._INT4, dictionary_length_field))
                if dictionary_bytes_for_this_save:
                    f_out.write(dictionary_bytes_for_this_save)

                values_start_offset = f_out.tell()
                calculated_values_start_offset = values_start_offset

                # Write Value Blocks
                value_write_count = 0
                total_value_bytes_written = 0
                value_ids_to_process = list(self.value_locations.keys())

                for value_id in value_ids_to_process:
                    if value_id not in self.value_locations:
                        continue  # Skip if removed concurrently

                    loc_info = self.value_locations[value_id]
                    try:
                        location_type = loc_info.get("location")
                        # Read source data bytes
                        value_data_bytes = self._read_value_data_bytes(value_id)
                        # Decompress source data using *active* state (from open/last save)
                        decompressed_bytes = self._decompress_value_data(
                            value_data_bytes, location_type, value_id
                        )

                        # Mark temp file as used if source was temp
                        if location_type == "temp" and "filename" in loc_info:
                            temp_files_used_in_save.add(loc_info["filename"])

                        # Re-compress using the settings for *this* save (cctx_values)
                        final_value_bytes_to_write = decompressed_bytes
                        if cctx_values:  # Use compressor if mode is zstd_*
                            final_value_bytes_to_write = cctx_values.compress(
                                decompressed_bytes
                            )

                        # Record final offset (of data) and length
                        current_offset = f_out.tell()
                        value_len = len(final_value_bytes_to_write)
                        final_locations_map[value_id] = (
                            current_offset + 8,
                            value_len,
                        )  # Data offset, data length

                        # Write length prefix (UINT8) and data
                        f_out.write(struct.pack(self._UINT8, value_len))
                        f_out.write(final_value_bytes_to_write)

                        value_write_count += 1
                        total_value_bytes_written += 8 + value_len

                    except (
                        FileNotFoundError,
                        KeyError,
                    ) as e:  # Handle missing temp file or ID
                        print(
                            f"Warning: Skipping value ID {value_id} during save: {e}. Ensure it wasn't removed unexpectedly."
                        )
                        if value_id in final_locations_map:
                            del final_locations_map[value_id]
                        if value_id in self.value_locations:
                            del self.value_locations[
                                value_id
                            ]  # Clean up inconsistent state
                    except (
                        IOError,
                        zstd.ZstdError,
                        ValueError,
                        struct.error,
                        TypeError,
                    ) as e:
                        raise IOError(
                            f"Failed to process/write value ID {value_id}: {type(e).__name__}: {e}"
                        ) from e
                    except Exception as e:
                        raise IOError(
                            f"Unexpected error processing/writing value ID {value_id}: {e}"
                        ) from e

                print(
                    f"Wrote {value_write_count} values, total value block bytes: {total_value_bytes_written}"
                )

                # Build and Write Keys Index Block
                final_keys_compressed_bytes = b""
                final_keys_compressed_len = 0
                if self.keys_index:
                    try:
                        final_keys_index_structure = self._build_final_keys_index(
                            self.keys_index, final_locations_map
                        )
                        final_keys_bytes = json.dumps(
                            final_keys_index_structure, separators=(",", ":")
                        ).encode("utf-8")
                        keys_cctx = zstd.ZstdCompressor(level=5)
                        final_keys_compressed_bytes = keys_cctx.compress(
                            final_keys_bytes
                        )
                        final_keys_compressed_len = len(final_keys_compressed_bytes)
                    except Exception as e:
                        raise ValueError(
                            f"Failed to build or compress the final keys index: {e}"
                        ) from e
                else:
                    print("No keys found in index, writing 0 length.")

                # Write keys index data THEN length
                if final_keys_compressed_bytes:
                    f_out.write(final_keys_compressed_bytes)
                f_out.write(struct.pack(self._UINT4, final_keys_compressed_len))

                expected_final_size = f_out.tell()

                # Force OS sync
                try:
                    f_out.flush()
                    os.fsync(f_out.fileno())
                except Exception as sync_e:
                    print(f"Info: os.fsync failed or not supported: {sync_e}")

            # File closed here
            final_file_handle = None

            # Log Actual File Size
            try:
                actual_size = os.path.getsize(filename)
                if actual_size != expected_final_size:
                    print(
                        f"WARNING: File size mismatch after close! Expected {expected_final_size}, Got {actual_size}."
                    )
            except OSError as e:
                print(f"ERROR: Could not get file size after close: {e}")

            # === Finalization ===
            print(f"Successfully saved PDS to {filename}")

            # Clean Temp Files that were *successfully read* during this save
            for temp_file in temp_files_used_in_save:
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except OSError as e:
                        print(
                            f"Warning: Failed to remove used temp file {temp_file}: {e}"
                        )

            # --- Update Internal State to Reflect the File Just Written ---
            # Close old handle if any
            if self._opened_file_handle and not self._opened_file_handle.closed:
                try:
                    self._opened_file_handle.close()
                except IOError:
                    pass
            self._opened_file_handle = None

            # Update value locations to 'inplace' using the map from *this* save
            new_value_locations = {}
            for value_id, (final_offset, final_length) in final_locations_map.items():
                new_value_locations[value_id] = {
                    "location": "inplace",
                    "offset": final_offset,
                    "length": final_length,
                }
            self.value_locations = new_value_locations

            # Update active state to match the file just written
            self._filename = filename
            self._active_compression_mode = effective_save_mode
            self._active_zstd_dictionary_bytes = (
                dictionary_bytes_for_this_save  # Store the dict bytes used
            )
            self._values_start_offset = calculated_values_start_offset

            # Re-open the newly saved file for reading
            try:
                self._opened_file_handle = open(filename, "rb")
                print(f"Successfully re-opened {filename} for reading.")
            except IOError as e:
                print(f"Warning: Could not re-open saved file {filename}: {e}")
                self.dispose()  # If re-open fails, reset state completely

        # === Exception Handling & Cleanup ===
        except Exception as e:
            print(f"Error during PDS save to {filename}: {type(e).__name__}: {e}")
            import traceback

            traceback.print_exc()
            if final_file_handle and not final_file_handle.closed:
                try:
                    final_file_handle.close()
                except Exception as ce:
                    print(f"Error closing file during exception: {ce}")
            if os.path.exists(filename):
                print(
                    f"Warning: Save failed. Output file '{filename}' might be incomplete/corrupted."
                )
            # Reset file-specific state, keep data in memory
            self._filename = None
            if self._opened_file_handle and not self._opened_file_handle.closed:
                try:
                    self._opened_file_handle.close()
                except OSError as close_e:
                    print(
                        f"Warning: Error closing file handle during exception cleanup: {close_e}"
                    )
                    pass
            self._opened_file_handle = None
            # Keep _active_compression_mode etc. as they were *before* the failed save attempt? Or reset? Reset is safer.
            self._active_compression_mode = "none"
            self._active_zstd_dictionary_bytes = None
            self._values_start_offset = 0

            raise  # Re-raise the original exception

    # --- Helper to build final keys index ---
    def _build_final_keys_index(
        self, current_node: Any, id_to_offset_length_map: Dict[str, Tuple[int, int]]
    ) -> Any:
        """Recursively builds keys index for saving, replacing value IDs with '|offset:length'."""
        if isinstance(current_node, dict):
            new_dict = {}
            for key, value in current_node.items():
                new_dict[key] = self._build_final_keys_index(
                    value, id_to_offset_length_map
                )
            return new_dict
        elif isinstance(current_node, list):
            new_list = []
            for item in current_node:
                new_list.append(
                    self._build_final_keys_index(item, id_to_offset_length_map)
                )
            return new_list
        elif isinstance(current_node, str):
            # Is it a value ID we have successfully written and mapped?
            if current_node in id_to_offset_length_map:
                offset, length = id_to_offset_length_map[current_node]
                if not isinstance(offset, int) or offset < 0:
                    raise ValueError(f"Invalid offset {offset} for ID {current_node}.")
                if not isinstance(length, int) or length < 0:
                    raise ValueError(f"Invalid length {length} for ID {current_node}.")
                return f"|{offset}:{length}"  # Format as "|offset:length"
            else:
                # String is not a key in the map - assume it's an ID that failed processing or was never added correctly
                raise ValueError(
                    f"Found untracked/unprocessed value ID '{current_node}' in keys index during final build."
                )
        else:
            raise TypeError(
                f"Found unexpected data type '{type(current_node)}' in keys index during final build."
            )

    # --- Cleanup Methods ---
    def dispose(self):
        """Cleans up resources: closes file handle and removes temp directory."""
        if self._opened_file_handle and not self._opened_file_handle.closed:
            try:
                self._opened_file_handle.close()
            except IOError as e:
                print(f"Warning: Error closing file handle for {self._filename}: {e}")
        self._opened_file_handle = None
        self._filename = None
        self._clean_temp_dir()
        # Reset state
        self.meta_data = {}
        self.keys_index = {}
        self.value_locations = {}
        self._active_compression_mode = "none"
        self._active_zstd_dictionary_bytes = None
        self._values_start_offset = 0
        # Keep user's intended save mode for next time
        # self._intended_save_compression_mode = 'zstd_dict' # Or whatever it was initialized with

    def __del__(self):
        self.dispose()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.dispose()
