import os
import pickle
import logging
from typing import Dict, List, Optional, Any, Set, Type
import numpy as np
import tables

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_config(**context) -> Dict[str, Any]:
    import logging

    venv_logger = logging.getLogger(f"{__name__}.get_config_venv")
    if not venv_logger.hasHandlers():
         logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    venv_logger.info("Executing get_config inside virtualenv.")
    params = context['params']
    channel_mapper = params.get('channel_mapper', {})
    if not isinstance(channel_mapper, dict):
         venv_logger.warning(f"channel_mapper is not a dict: {type(channel_mapper)}. Using empty mapper.")
         channel_mapper = {}

    config = {
        'base_input_folder': params['base_input_folder'],
        'output_folder': params['output_folder'],
        'ros_distro': params['ros_distro'],
        'custom_msg_definition_folders': params.get('custom_msg_definition_folders', []),
    }
    venv_logger.info(f"Configuration loaded: {config}")
    return config

def create_directories(config: Dict[str, Any]) -> Dict[str, Any]:
    import os
    import logging

    venv_logger = logging.getLogger(f"{__name__}.create_directories_venv")
    if not venv_logger.hasHandlers():
         logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    venv_logger.info("Executing create_directories inside virtualenv.")
    output_f = config.get('output_folder')
    if not output_f:
        venv_logger.error("Output folder path missing in config.")
        raise ValueError("Output folder path missing in config.")

    try:
        venv_logger.info(f"Ensuring directory exists: {output_f}")
        os.makedirs(output_f, exist_ok=True)
    except OSError as e:
        venv_logger.error(f"Failed to create directory {output_f}: {e}", exc_info=True)
        raise
    return config

def save_ros_topics_to_pytables(
    output_hdf5_path: str,
    topic_data: Dict[str, Any],
    ) -> bool:
    import os
    import logging
    import tables
    import numpy as np

    writer_logger = logging.getLogger(f"{__name__}.save_pytables_data_venv")
    if not writer_logger.hasHandlers():
         logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    writer_logger.info(f"Attempting to write ROS topic data to {output_hdf5_path}")

    output_dir = os.path.dirname(output_hdf5_path)
    try:
        os.makedirs(output_dir, exist_ok=True)
    except OSError as e:
        writer_logger.error(f"Failed to create output directory {output_dir}: {e}", exc_info=True)
        return False

    try:
        with tables.open_file(output_hdf5_path, mode="w", title="Processed ROS Bag Data") as h5file:
            filters = tables.Filters(complib='zlib', complevel=5)

            for topic_name, data_info in topic_data.items():
                structured_array = data_info.get('data')
                table_description = data_info.get('description')

                if structured_array is None or table_description is None:
                    writer_logger.warning(f"Skipping topic '{topic_name}' due to missing data or description.")
                    continue

                safe_topic_name = topic_name.strip('/').replace('/', '__')
                group_path = f"/{safe_topic_name}"

                if group_path not in h5file:
                     topic_group = h5file.create_group(h5file.root, safe_topic_name, f"Data for topic {topic_name}")
                else:
                     topic_group = h5file.get_node(group_path)

                table_name = "messages"
                data_table = h5file.create_table(topic_group, table_name,
                                                 description=table_description,
                                                 title=f"Messages for {topic_name}",
                                                 filters=filters)

                if len(structured_array) > 0:
                    data_table.append(structured_array)
                    writer_logger.info(f"Successfully wrote {len(structured_array)} messages for topic '{topic_name}' to table '{table_name}' in group '{group_path}'.")
                else:
                    writer_logger.info(f"No messages to write for topic '{topic_name}'. Created empty table.")

                data_table.flush()

            writer_logger.info(f"Finished writing all topics to {output_hdf5_path}")
            return True
    except Exception as e:
        writer_logger.error(f"Failed during PyTables file write operation for {output_hdf5_path}: {e}", exc_info=True)
        if os.path.exists(output_hdf5_path):
            try:
                os.remove(output_hdf5_path)
                writer_logger.info(f"Removed partially created/failed file: {output_hdf5_path}")
            except OSError as rm_err:
                writer_logger.error(f"Failed to remove partially created/failed file {output_hdf5_path}: {rm_err}")
        return False


def _extract_ros_data_logic(config: Dict[str, Any], subfolder_path: str) -> Optional[Dict[str, Any]]:
    import os
    import logging
    import numpy as np
    import pickle
    from rosbags.rosbag2 import Reader as Rosbag2Reader
    from rosbags.serde import deserialize_cdr
    from rosbags.typesys import Stores, get_types_from_msg, register_types, get_typestore
    from rosbags.typesys.base import TypesysError
    from pathlib import Path
    import time
    from datetime import datetime
    from preprocessing.ros_etl_utils import _scan_msg_definitions, _get_flattened_fields, _flatten_message

    venv_logger = logging.getLogger(f"{__name__}._extract_ros_data_venv")
    if not venv_logger.hasHandlers():
         logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    venv_logger.info(f"Starting ROS data extraction for subfolder: {subfolder_path} inside virtualenv.")
    start_time = time.time()

    output_folder = config.get('output_folder')
    ros_distro = config.get('ros_distro', 'humble')
    custom_msg_paths = config.get('custom_msg_definition_folders', [])

    if not output_folder:
        venv_logger.error("Output folder path missing in config.")
        return None

    try:
        os.makedirs(output_folder, exist_ok=True)
    except OSError as e:
        venv_logger.error(f"Failed to ensure output directory exists {output_folder}: {e}")
        return None

    typestore_member_name = f'ROS2_{ros_distro.upper()}'
    try:
        typestore_enum_member = getattr(Stores, typestore_member_name)
        typestore = get_typestore(typestore_enum_member)
        venv_logger.info(f"Using base typestore: {typestore_member_name}")
    except AttributeError:
        venv_logger.error(f"Unsupported ROS distro '{ros_distro}'. Could not find attribute '{typestore_member_name}' in rosbags.typesys.Stores.")
        return None
    except Exception as e:
         venv_logger.error(f"An unexpected error occurred getting the typestore: {e}", exc_info=True)
         return None

    if custom_msg_paths:
        venv_logger.info("Parsing external message definitions...")
        try:
            external_types = _scan_msg_definitions(custom_msg_paths)
            if external_types:
                 venv_logger.info(f"Registering {len(external_types)} external types with the typestore...")
                 register_types(external_types)
                 venv_logger.info("Registration of external types complete.")
            else:
                 venv_logger.info("No external message definitions found or parsed.")
        except Exception as e:
            venv_logger.error(f"Error processing external message definitions: {e}", exc_info=True)

    extracted_data_py = {}
    timestamps_py = {}
    topic_field_map = {}
    topic_msg_type = {}
    processed_connections = set()
    skipped_connections_unknown_type = set()
    skipped_connections_no_fields = set()
    total_messages_processed = 0

    try:
        with Rosbag2Reader(Path(subfolder_path)) as reader:
            venv_logger.info(f"Opened bag: {subfolder_path}. Found {len(reader.connections)} connections.")

            bag_types = {}
            failed_bag_types = set()
            for conn in reader.connections:
                 if conn.msgtype not in typestore.types and conn.msgtype not in bag_types and conn.msgtype not in failed_bag_types:
                     venv_logger.info(f"Found potential msgdef in bag for type '{conn.msgtype}' (Topic: '{conn.topic}'). Length: {len(conn.ext.offered_cdr_message_definitions)}. Attempting parse.")
                     msgdef_to_parse = conn.ext.offered_cdr_message_definitions or conn.msgdef
                     if msgdef_to_parse:
                         try:
                             type_dict = get_types_from_msg(msgdef_to_parse, conn.msgtype)
                             bag_types.update(type_dict)
                         except (TypesysError, AssertionError, Exception) as parse_err:
                             venv_logger.warning(f"Failed to parse/register message definition from bag for type '{conn.msgtype}' (Topic: '{conn.topic}'): {parse_err}")
                             failed_bag_types.add(conn.msgtype)
                     else:
                         venv_logger.warning(f"No message definition found in bag connection for type '{conn.msgtype}' (Topic: '{conn.topic}').")
                         failed_bag_types.add(conn.msgtype)

            if bag_types:
                 venv_logger.info(f"Registering {len(bag_types)} types found within the bag...")
                 register_types(bag_types)
                 venv_logger.info("Registration of bag types complete.")
            if failed_bag_types:
                 venv_logger.error(f"Failed to parse definitions found within the bag for types: {failed_bag_types}")

            venv_logger.info("Determining flattened fields for each topic...")
            for conn in reader.connections:
                topic = conn.topic
                msgtype = conn.msgtype
                topic_msg_type[topic] = msgtype

                if topic not in topic_field_map:
                    if msgtype in typestore.types:
                        try:
                            fields = _get_flattened_fields(msgtype, typestore)
                            if fields:
                                topic_field_map[topic] = fields
                                extracted_data_py[topic] = {field: [] for field in fields}
                                timestamps_py[topic] = []
                                processed_connections.add(conn.id)
                            else:
                                venv_logger.warning(f"No processable fields found for type '{msgtype}' (Topic: '{topic}'). Skipping.")
                                skipped_connections_no_fields.add(conn.id)
                        except KeyError: 
                            venv_logger.warning(f"Message type '{msgtype}' for topic '{topic}' not found in the final typestore. Cannot determine fields or deserialize.")
                            skipped_connections_unknown_type.add(conn.id)
                        except Exception as e:
                            venv_logger.error(f"Error getting fields for type '{msgtype}' (Topic: '{topic}'): {e}. Skipping.")
                            skipped_connections_no_fields.add(conn.id)
                    else:
                        venv_logger.warning(f"Message type '{msgtype}' for topic '{topic}' not found in the final typestore. Cannot determine fields or deserialize.")
                        skipped_connections_unknown_type.add(conn.id)

            venv_logger.info("Starting message iteration and data extraction...")
            valid_connections = [c for c in reader.connections if c.id in processed_connections]
            num_valid_connections = len(valid_connections)
            num_total_connections = len(reader.connections)
            venv_logger.info(f"Processing messages from {num_valid_connections} valid connections.")
            if skipped_connections_unknown_type:
                 venv_logger.info(f"Excluded {len(skipped_connections_unknown_type)} connections due to unknown types.")
            if skipped_connections_no_fields:
                 venv_logger.info(f"Excluded {len(skipped_connections_no_fields)} connections due to missing fields/processability.")

            message_count = reader.message_count
            log_interval = max(1, message_count // 20)
            last_log_time = start_time

            for i, (conn, timestamp, rawdata) in enumerate(reader.messages(connections=valid_connections)):
                if conn.id in processed_connections:
                    topic = conn.topic
                    msgtype = conn.msgtype
                    try:
                        msg = deserialize_cdr(rawdata, msgtype)
                        timestamps_py[topic].append(timestamp / 1e9)

                        flat_msg = _flatten_message(msg)
                        for field in topic_field_map[topic]:
                            extracted_data_py[topic][field].append(flat_msg.get(field, None))

                        total_messages_processed += 1

                        if (i + 1) % log_interval == 0 or time.time() - last_log_time > 10:
                            elapsed = time.time() - start_time
                            venv_logger.info(f"Processed {i+1}/{message_count} messages... ({elapsed:.2f}s)")
                            last_log_time = time.time()

                    except Exception as e:
                        venv_logger.error(f"Error deserializing/processing message for topic '{topic}' (type: {msgtype}): {e}", exc_info=False)

            venv_logger.info(f"Finished iterating messages. Processed {total_messages_processed} messages total.")

    except Exception as e:
        venv_logger.error(f"Failed to read or process bag {subfolder_path}: {e}", exc_info=True)
        return None

    venv_logger.info("Converting extracted data to NumPy arrays...")
    extracted_data_np = {}
    topics_skipped_conversion = 0
    for topic, data_dict in extracted_data_py.items():
        topic_timestamps = timestamps_py.get(topic)
        if not topic_timestamps:
            venv_logger.warning(f"No timestamps (and likely no data) extracted for topic: {topic}. Skipping.")
            topics_skipped_conversion += 1
            continue

        try:
            np_arrays = {}
            np_arrays['timestamp_ns'] = np.array(topic_timestamps, dtype=np.int64) * 1_000_000_000
            np_arrays['timestamp_s'] = np.array(topic_timestamps, dtype=np.float64)

            for field, data_list in data_dict.items():
                 try:
                     np_array = np.array(data_list)
                     np_arrays[field] = np_array
                 except Exception as arr_e:
                     venv_logger.error(f"Error converting field '{field}' for topic '{topic}' to NumPy array: {arr_e}. Skipping field.")
                     np_arrays[field] = np.full(len(data_list), None, dtype=object)

            extracted_data_np[topic] = np_arrays
        except Exception as e:
            venv_logger.error(f"Error converting data for topic '{topic}' to NumPy: {e}. Skipping topic.")
            topics_skipped_conversion += 1

    if not extracted_data_np:
         venv_logger.error(f"No topics successfully extracted and converted for {subfolder_path}. Returning None.")
         return None

    base_name = Path(subfolder_path).name
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    temp_filename = f"extracted_ros_data_{base_name}_{timestamp_str}.pkl"
    temp_filepath = os.path.join(output_folder, temp_filename)

    venv_logger.info(f"Saving extracted NumPy data to temporary file: {temp_filepath}")
    try:
        with open(temp_filepath, 'wb') as f:
            pickle.dump(extracted_data_np, f, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception as e:
        venv_logger.error(f"Failed to save extracted data to {temp_filepath}: {e}", exc_info=True)
        return None

    end_time = time.time()
    duration = end_time - start_time
    venv_logger.info(f"Finished extraction and saving for {subfolder_path} in {duration:.2f}s.")
    if topics_skipped_conversion > 0:
        venv_logger.warning(f"Total topics skipped during NumPy conversion: {topics_skipped_conversion}")

    return {
        "subfolder_path": subfolder_path,
        "output_folder": output_folder,
        "temp_data_path": temp_filepath,
        "topic_msg_type": topic_msg_type,
    }


def _transform_load_ros_data_logic(extracted_info: Optional[Dict[str, Any]], config: Dict[str, Any]) -> Optional[Dict[str, str]]:
    import os
    import logging
    import pickle
    import numpy as np
    import tables
    from pathlib import Path

    venv_logger = logging.getLogger(f"{__name__}._transform_load_ros_venv")
    if not venv_logger.hasHandlers():
         logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    if not isinstance(extracted_info, dict) or not extracted_info.get("temp_data_path"):
        venv_logger.error(f"Invalid or missing 'extracted_info' received: {extracted_info}")
        return None

    temp_filepath = extracted_info["temp_data_path"]
    subfolder_path = extracted_info.get("subfolder_path", "unknown_subfolder")
    output_folder = extracted_info.get("output_folder")
    topic_msg_type = extracted_info.get("topic_msg_type", {})

    venv_logger.info(f"Starting transform/load process for data from: {temp_filepath}")

    if not output_folder:
        venv_logger.error("Output folder path missing in extracted_info.")
        # Attempt cleanup even if config is bad
        if os.path.exists(temp_filepath):
            try:
                os.remove(temp_filepath)
                venv_logger.info(f"Cleaned up temporary file due to config error: {temp_filepath}")
            except OSError as rm_err:
                venv_logger.error(f"Error removing temporary file {temp_filepath} after config error: {rm_err}")
        return None

    extracted_data_np = None
    try:
        venv_logger.info(f"Loading extracted data from {temp_filepath}...")
        with open(temp_filepath, 'rb') as f:
            extracted_data_np = pickle.load(f)
        venv_logger.info(f"Successfully loaded data for {len(extracted_data_np)} topics.")

        base_name = Path(subfolder_path).name
        hdf5_filename = f"{base_name}.h5"
        hdf5_filepath = os.path.join(output_folder, hdf5_filename)
        venv_logger.info(f"Target HDF5 file path: {hdf5_filepath}")

        pytables_data_to_save = {}
        for topic, np_arrays in extracted_data_np.items():
            description_dict = {}
            example_row = {field: arr[0] for field, arr in np_arrays.items() if len(arr) > 0}

            if 'timestamp_s' in np_arrays:
                 description_dict['timestamp_s'] = tables.Float64Col(pos=0)
            if 'timestamp_ns' in np_arrays:
                 description_dict['timestamp_ns'] = tables.Int64Col(pos=1)

            pos_counter = 2
            valid_fields_for_table = {}
            for field, arr in np_arrays.items():
                if field in ['timestamp_s', 'timestamp_ns']:
                    continue
                if len(arr) > 0:
                    col_type = tables.Col.from_dtype(arr.dtype)
                    if col_type:
                        description_dict[field] = col_type(pos=pos_counter)
                        valid_fields_for_table[field] = arr
                        pos_counter += 1
                    else:
                        venv_logger.warning(f"Could not determine PyTables column type for field '{field}' (dtype: {arr.dtype}) in topic '{topic}'. Skipping field.")
                else:
                     venv_logger.warning(f"Field '{field}' in topic '{topic}' has no data. Skipping field.")

            if not description_dict or not valid_fields_for_table:
                venv_logger.warning(f"No valid columns found or created for topic '{topic}'. Skipping topic.")
                continue

            TableDescription = type(f"{topic.replace('/', '_')}TableDesc", (tables.IsDescription,), description_dict)

            num_rows = len(np_arrays.get('timestamp_s', next(iter(valid_fields_for_table.values()), [])))
            if num_rows > 0:
                structured_array = np.empty(num_rows, dtype=TableDescription.columns)
                for field, col_instance in TableDescription.columns.items():
                     if field in np_arrays:
                         try:
                             target_dtype = structured_array.dtype[field]
                             source_arr = np_arrays[field]
                             if (np.issubdtype(target_dtype, np.integer) or np.issubdtype(target_dtype, np.bool_)) and np.issubdtype(source_arr.dtype, np.floating) and np.isnan(source_arr).any():
                                 fill_value = 0 if np.issubdtype(target_dtype, np.integer) else False
                                 venv_logger.warning(f"NaNs found in column '{field}' for topic '{topic}'; replacing with {fill_value} before casting to {target_dtype}.")
                                 arr_filled = np.nan_to_num(source_arr, nan=fill_value)
                                 structured_array[field] = arr_filled.astype(target_dtype)
                             else:
                                 structured_array[field] = source_arr.astype(target_dtype)
                         except Exception as cast_err:
                             venv_logger.error(f"Failed to cast data for column '{field}' to type {target_dtype} for topic '{topic}': {cast_err}. Skipping field assignment.", exc_info=True)
                     else:
                          venv_logger.warning(f"Field '{field}' in description but not found in extracted NumPy arrays for topic '{topic}'.")
            else:
                 structured_array = np.empty(0, dtype=TableDescription.columns)

            pytables_data_to_save[topic] = {
                'data': structured_array,
                'description': TableDescription
            }

        venv_logger.info(f"Calling save_ros_topics_to_pytables to write data to {hdf5_filepath}...")
        success = save_ros_topics_to_pytables(
            hdf5_filepath,
            pytables_data_to_save
        )

        if success:
            venv_logger.info(f"save_ros_topics_to_pytables reported SUCCESS for {subfolder_path}")
            return {'subfolder_path': subfolder_path, 'output_hdf5_path': hdf5_filepath}
        else:
            venv_logger.error(f"save_ros_topics_to_pytables reported FAILURE for {subfolder_path}.")
            return None

    except FileNotFoundError:
        venv_logger.error(f"Temporary data file not found during load: {temp_filepath}")
        return None
    except Exception as e:
        venv_logger.error(f"Error during transform/load process for {subfolder_path}: {e}", exc_info=True)
        return None
    finally:
        # Ensure temporary file is always cleaned up if it exists
        if os.path.exists(temp_filepath):
            try:
                os.remove(temp_filepath)
                venv_logger.info(f"Cleaned up temporary file: {temp_filepath}")
            except OSError as rm_err:
                venv_logger.error(f"Error removing temporary file {temp_filepath}: {rm_err}")


def _scan_msg_definitions(root_folders: List[str]) -> Dict[str, str]:
    import os
    import logging
    from pathlib import Path

    scanner_logger = logging.getLogger(f"{__name__}._scan_msg_definitions")
    if not scanner_logger.hasHandlers():
         logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    all_defs = {}
    scanner_logger.info(f"Scanning for .msg files in: {root_folders}")
    for root_folder_str in root_folders:
        root_folder = Path(root_folder_str)
        if not root_folder.is_dir():
            scanner_logger.warning(f"Provided custom message path is not a directory or does not exist: {root_folder}")
            continue

        scanner_logger.info(f"Searching for .msg files recursively in {root_folder}...")
        msg_files_found = 0
        for path in root_folder.rglob('*.msg'):
            msg_files_found += 1
            try:
                relative_path = path.relative_to(root_folder)
                parts = list(relative_path.parts)
                if len(parts) >= 3 and parts[-2] == 'msg':
                     type_name = f"{parts[0]}/{path.stem}"
                     with open(path, 'r') as f:
                         content = f.read()
                     all_defs[type_name] = content
                else:
                     scanner_logger.warning(f"Could not determine type name from path structure: {path}")

            except Exception as e:
                scanner_logger.error(f"Error reading or processing .msg file {path}: {e}")
        scanner_logger.info(f"Found {msg_files_found} .msg files in {root_folder}.")

    scanner_logger.info(f"Finished scanning external definition folders. Processed {len(all_defs)} unique type definitions.")
    return all_defs

def _get_flattened_fields(msg_type_name: str, typestore) -> List[str]:
    import logging
    import numpy as np

    flat_logger = logging.getLogger(f"{__name__}._get_flattened_fields")
    if not flat_logger.hasHandlers():
         logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    fields = []
    try:
        fields_tuples = typestore.get_fields(msg_type_name)

        def flatten(prefix, typename):
            nested_fields = []
            try:
                sub_fields_tuples = typestore.get_fields(typename)
                for sub_name, sub_type in sub_fields_tuples:
                    new_prefix = f"{prefix}.{sub_name}"
                    if sub_type in typestore.types:
                         nested_fields.append(new_prefix + "__complex")
                    else:
                         nested_fields.append(new_prefix)
            except KeyError:
                 flat_logger.error(f"Type '{typename}' not found in typestore during flattening.")
                 nested_fields.append(prefix + "__unknown")
            except Exception as e:
                 flat_logger.error(f"Error flattening type '{typename}' with prefix '{prefix}': {e}")
                 nested_fields.append(prefix + "__error")
            return nested_fields

        for name, type_info in fields_tuples:
             type_name = type_info[0] if isinstance(type_info, tuple) else type_info
             if type_name in typestore.types:
                 fields.append(name + "__complex")
             else:
                 fields.append(name)

    except KeyError:
        flat_logger.error(f"Message type '{msg_type_name}' not found in typestore for getting fields.")
        return []
    except Exception as e:
        flat_logger.error(f"Error getting flattened fields for '{msg_type_name}': {e}")
        return []
    return fields


def _flatten_message(msg: Any, prefix: str = '') -> Dict[str, Any]:
    import numpy as np

    flat_dict = {}
    if hasattr(msg, '__slots__'):
        for slot in msg.__slots__:
            val = getattr(msg, slot)
            if isinstance(val, (list, tuple, np.ndarray)):
                 flat_dict[f"{prefix}{slot}__array"] = repr(val)
            elif hasattr(val, '__slots__'):
                 flat_dict[f"{prefix}{slot}__complex"] = repr(val)
            else:
                 flat_dict[f"{prefix}{slot}"] = val
    elif not hasattr(msg, '__dict__'):
         if prefix:
             flat_dict[prefix.rstrip('.')] = msg

    return flat_dict


def _log_processed_subfolders_logic(processed_results: List[Optional[Dict[str, str]]], unpacked_state: Dict[str, Any]) -> None:
    import os
    import pickle
    import logging

    venv_logger = logging.getLogger(f"{__name__}._log_processed_venv")
    if not venv_logger.hasHandlers():
         logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    venv_logger.info("Executing log_processed_subfolders_logic inside virtualenv.")

    config = unpacked_state.get('config')
    previously_processed_set = unpacked_state.get('processed_set', set())

    if not config:
        venv_logger.error("Config missing in unpacked state! Cannot update state file.")
        raise ValueError("Config not found in unpacked_state")

    output_folder = config.get('output_folder')
    if not output_folder:
        venv_logger.error("Output folder path missing in config! Cannot update state file.")
        raise ValueError("Output folder path missing in config")

    successfully_processed_info = [item for item in processed_results if item is not None and isinstance(item, dict) and 'subfolder_path' in item]

    if not successfully_processed_info:
        venv_logger.info("No new subfolders were successfully processed and loaded in this run.")
        return

    pickle_path = os.path.join(output_folder, "processed_ros_subfolders.pkl")
    newly_processed_subfolders = {info['subfolder_path'] for info in successfully_processed_info}

    venv_logger.info(f"Logging {len(newly_processed_subfolders)} newly processed subfolders.")
    venv_logger.debug(f"Newly processed subfolders: {newly_processed_subfolders}")

    updated_files_set = previously_processed_set.union(newly_processed_subfolders)

    try:
        with open(pickle_path, 'wb') as f:
            pickle.dump(updated_files_set, f)
        venv_logger.info(f"Updated processed subfolders state log at {pickle_path}. Total count: {len(updated_files_set)}")
    except Exception as e:
        venv_logger.critical(f"CRITICAL: Failed to write state file {pickle_path}: {e}", exc_info=True)
        raise IOError(f"CRITICAL: Failed to write state to {pickle_path}") from e

    return None

def _get_config_logic(**context) -> Dict[str, Any]:
     import logging
     logger = logging.getLogger(__name__)
     params = context['params']
     config = {
          'base_input_folder': params['base_input_folder'],
          'output_folder': params['output_folder'],
          'ros_distro': params.get('ros_distro', 'humble'),
          'custom_msg_definition_folders': params.get('custom_msg_definition_folders', []),
     }
     logger.info(f"ROS Config: {config}")
     return config

def _create_output_directory_logic(config: Dict[str, Any]) -> Dict[str, Any]:
     import os
     import logging
     logger = logging.getLogger(__name__)
     output_f = config['output_folder']
     try:
          logger.info(f"Ensuring ROS output directory exists: {output_f}")
          os.makedirs(output_f, exist_ok=True)
     except OSError as e:
          logger.error(f"Failed to create ROS output directory: {e}", exc_info=True)
          raise
     return config

def prepare_extraction_kwargs_logic(unpacked_state: Dict[str, Any], subfolders_to_process: List[str], **context) -> List[Dict[str, Any]]:
    prep_logger = logging.getLogger(f"{__name__}._prepare_extraction_kwargs_logic")
    config = unpacked_state.get('config')
    if not config:
        prep_logger.error("Config missing in unpacked state!")
        return []

    if not subfolders_to_process:
        prep_logger.info("No new subfolders found to process.")
        return []

    kwargs_list = []
    for subfolder in subfolders_to_process:
        kwargs_list.append({
            "config": config,
            "subfolder_path": subfolder,
        })
    prep_logger.info(f"Prepared {len(kwargs_list)} sets of arguments for extraction.")
    return kwargs_list

def prepare_transform_load_kwargs_logic(
    extraction_results: List[Optional[Dict[str, Any]]],
    **context
) -> List[Dict[str, Any]]:
    prep_logger = logging.getLogger(f"{__name__}._prepare_transform_load_kwargs_logic")
    kwargs_list = []

    if extraction_results is None:
        prep_logger.info("Received None as extraction result (upstream likely skipped all). No data to transform/load.")
        return []

    if not isinstance(extraction_results, list):
        prep_logger.warning(f"Received non-list extraction result: {type(extraction_results)}. Wrapping in list.")
        extraction_results = [extraction_results]

    valid_results_count = 0
    for result in extraction_results:
        if isinstance(result, dict) and result.get('temp_data_path') is not None: # Check for the path key
            kwargs_list.append({
                "extracted_info": result,
            })
            valid_results_count += 1
        else:
            prep_logger.warning(f"Skipping transform/load preparation for invalid/None extraction result: {result}")

    prep_logger.info(f"Prepared {len(kwargs_list)} sets of arguments for transform/load from {valid_results_count} valid extraction results.")
    return kwargs_list


def _load_processed_subfolders_state_logic(config: Dict[str, Any]) -> tuple[Dict[str, Any], set[str]]:
     import os
     import pickle
     import logging
     logger = logging.getLogger(__name__)
     output_folder = config['output_folder']
     pickle_path = os.path.join(output_folder, "processed_ros_subfolders.pkl")
     processed_set: Set[str] = set()
     if os.path.exists(pickle_path):
          try:
               with open(pickle_path, 'rb') as f:
                    loaded_data = pickle.load(f)
                    if isinstance(loaded_data, set):
                         processed_set = loaded_data
                         logger.info(f"Loaded {len(processed_set)} processed subfolder names from {pickle_path}")
                    else:
                         logger.warning(f"ROS state file {pickle_path} did not contain a set. Ignoring.")
          except Exception as e:
               logger.warning(f"Error loading ROS state file {pickle_path}: {e}. Assuming empty state.")
     else:
          logger.info(f"ROS state file {pickle_path} not found. Assuming no subfolders processed previously.")
     return config, processed_set

def _unpack_state_data(state_tuple: tuple[Dict[str, Any], set[str]]) -> Dict[str, Any]:
     if not isinstance(state_tuple, tuple) or len(state_tuple) != 2:
          raise ValueError(f"Expected a tuple of (config, processed_set), got: {type(state_tuple)}")
     config, processed_set = state_tuple
     return {"config": config, "processed_set": processed_set}

def _find_unprocessed_subfolders_logic(config_processed_tuple: tuple[Dict[str, Any], set[str]]) -> List[str]:
     import os
     import logging
     logger = logging.getLogger(__name__)
     config, processed_subfolders = config_processed_tuple
     base_input_folder = config['base_input_folder']
     unprocessed_list = []
     logger.info(f"Scanning {base_input_folder} for ROS bag subfolders...")
     try:
          for item in os.listdir(base_input_folder):
               item_path = os.path.join(base_input_folder, item)
               metadata_path = os.path.join(item_path, 'metadata.yaml')
               if os.path.isdir(item_path) and os.path.exists(metadata_path):
                    if item_path not in processed_subfolders:
                         unprocessed_list.append(item_path)
                         logger.debug(f"Found unprocessed subfolder: {item_path}")
                    else:
                         logger.debug(f"Skipping already processed subfolder: {item_path}")
               else:
                    logger.debug(f"Skipping item (not a valid rosbag folder or no metadata.yaml): {item_path}")

     except FileNotFoundError:
          logger.error(f"Base input directory not found: {base_input_folder}")
          return []
     except OSError as e:
          logger.error(f"Error listing base input directory {base_input_folder}: {e}", exc_info=True)
          raise

     count = len(unprocessed_list)
     if count > 0:
          logger.info(f"Found {count} new ROS bag subfolders to process.")
     else:
          logger.info("No new ROS bag subfolders found to process.")
     return sorted(unprocessed_list)

