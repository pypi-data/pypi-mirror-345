import os
import pickle
import logging
from typing import Dict, List, Optional, Callable, Any, Tuple, Set
import time
import re
import keyword
import importlib

import numpy as np
import tables
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore, get_types_from_msg
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

RosbagHdf5Writer = Callable[[str, Dict[str, Dict[str, Any]]], bool]

def sanitize_hdf5_identifier(name: str) -> str:
    sanitized = re.sub(r'\W|^(?=\d)', '_', name)
    if keyword.iskeyword(sanitized):
        sanitized += '_'
    if not sanitized:
        return '_'
    return sanitized

def get_all_fields(typename: str, typestore: Any, current_prefix: str = '', visited: Optional[Set[str]] = None) -> List[str]:
    task_logger = logging.getLogger(__name__)
    if visited is None:
        visited = set()
    if typename in visited:
        task_logger.debug(f"Cycle detected or already visited: {typename}. Stopping recursion.")
        return []
    visited.add(typename)

    fields_list = []
    try:
        if typename not in typestore.types:
             task_logger.warning(f"Type '{typename}' not found in typestore. Known types: {list(typestore.types.keys())[:20]}...")
             return []

        type_definition = typestore.get_msgdef(typename)
        if not hasattr(type_definition, 'fields'):
            return []

        fields_definition = type_definition.fields
    except KeyError:
        task_logger.warning(f"Type '{typename}' not found in typestore during field recursion.")
        return []
    except AttributeError:
        task_logger.warning(f"Type '{typename}' definition in typestore lacks 'fields' attribute.")
        return []

    for field in fields_definition:
        field_name = field[0]
        field_type = field[1][1][0]
        flat_name = f"{current_prefix}{field_name}"

        if hasattr(field_type, 'name'):
            field_type_name = field_type.name
            is_array = hasattr(field_type, 'count')
            element_type_name = field_type_name

            if is_array and hasattr(field_type, 'basetype') and hasattr(field_type.basetype, 'name'):
                 element_type_name = field_type.basetype.name

            if element_type_name in typestore.types and hasattr(typestore.types[element_type_name], 'fields'):
                 nested_fields = get_all_fields(
                     element_type_name,
                     typestore,
                     current_prefix=f"{flat_name}_",
                     visited=visited.copy()
                 )
                 if nested_fields:
                     fields_list.extend(nested_fields)
            else:
                 fields_list.append(flat_name)

        elif isinstance(field_type, str):
            fields_list.append(flat_name)
        elif isinstance(field_type, Tuple):
            fields_list.append(flat_name)
        else:
             task_logger.warning(f"Field '{field_name}' in type '{typename}' has an unexpected type structure: {type(field_type)}. Skipping.")
             continue

    return fields_list

def parse_external_msg_definitions(
    definition_folders: List[str],
    logger: logging.Logger
) -> Dict[str, Any]:
    all_external_types = {}
    files_processed = 0
    parse_errors = 0

    if not definition_folders:
        logger.info("No external definition folders provided to parse.")
        return {}

    logger.info(f"Scanning for .msg files in: {definition_folders}")

    for folder_path_str in definition_folders:
        base_path = Path(folder_path_str)
        if not base_path.is_dir():
            logger.warning(f"Provided definition path is not a directory, skipping: {folder_path_str}")
            continue

        logger.info(f"Searching for .msg files recursively in {base_path}...")
        msg_files = list(base_path.rglob('*.msg'))
        logger.info(f"Found {len(msg_files)} .msg files in {base_path}.")

        for msg_file_path in msg_files:
            files_processed += 1
            try:
                relative_path = msg_file_path.relative_to(base_path)
                type_name_parts = list(relative_path.parts[:-1])
                type_name_parts.append(relative_path.stem)

                if len(type_name_parts) < 3 or type_name_parts[-2] not in ('msg', 'srv', 'action'):
                       logger.warning(f"Unexpected file structure, skipping type name generation for: {msg_file_path}. Relative path: {relative_path}")
                       continue

                ros_type_name = '/'.join(type_name_parts)

                logger.debug(f"Reading and parsing {msg_file_path} for type {ros_type_name}")
                content = msg_file_path.read_text()

                parsed_types = get_types_from_msg(content, ros_type_name)

                for name, definition in parsed_types.items():
                    if name in all_external_types:
                         logger.warning(f"Duplicate definition found for type '{name}' from file {msg_file_path}. Overwriting previous definition.")
                    all_external_types[name] = definition

                logger.debug(f"Parsed {len(parsed_types)} types from {msg_file_path}. Primary: {ros_type_name}")

            except ValueError as e:
                 logger.error(f"Error parsing {msg_file_path} (ValueError): {e}", exc_info=False)
                 parse_errors += 1
            except OSError as e:
                 logger.error(f"Error reading file {msg_file_path}: {e}", exc_info=False)
                 parse_errors += 1
            except Exception as e:
                 logger.error(f"Unexpected error processing {msg_file_path}: {e}", exc_info=False)
                 parse_errors += 1

    logger.info(f"Finished scanning external definition folders. Processed {files_processed} files.")
    if parse_errors > 0:
         logger.error(f"Encountered {parse_errors} errors during external definition parsing.")
    logger.info(f"Collected {len(all_external_types)} type definitions externally.")
    return all_external_types

def _get_config_logic(default_ros_distro: str, **context) -> Dict[str, Any]:
    task_logger = logging.getLogger(__name__)
    params = context['params']
    if not params.get('base_input_folder') or not params.get('output_folder'):
        raise ValueError("Missing required DAG parameters: 'base_input_folder' or 'output_folder'")
    config = {
        'base_input_folder': params['base_input_folder'],
        'output_folder': params['output_folder'],
        'ros_distro': params.get('ros_distro', default_ros_distro),
        'custom_msg_definition_folders': params.get('custom_msg_definition_folders', []) or []
    }
    task_logger.info(f"Configuration: Base Input={config['base_input_folder']}, Output={config['output_folder']}, ROS Distro={config['ros_distro']}")
    if config['custom_msg_definition_folders']:
        task_logger.info(f"Custom .msg definition folders: {config['custom_msg_definition_folders']}")
    else:
        task_logger.info("No external custom .msg definition folders provided.")
    return config

def _create_output_directory_logic(config: Dict[str, Any]) -> Dict[str, Any]:
    task_logger = logging.getLogger(__name__)
    output_f = config['output_folder']
    task_logger.info(f"Ensuring output directory exists: {output_f}")
    try:
        os.makedirs(output_f, exist_ok=True)
    except OSError as e:
        task_logger.error(f"Failed to create output directory {output_f}: {e}", exc_info=True)
        raise
    return config

def _load_processed_subfolders_state_logic(config: Dict[str, Any]) -> Tuple[Dict[str, Any], Set[str]]:
    task_logger = logging.getLogger(__name__)
    state_file = os.path.join(config['output_folder'], "processed_ros2_subfolders.pkl")
    processed_subfolders: Set[str] = set()
    if os.path.exists(state_file):
        try:
            with open(state_file, 'rb') as f:
                loaded_data = pickle.load(f)
            if isinstance(loaded_data, set):
                validated_data = {item for item in loaded_data if isinstance(item, str) and item}
                if len(validated_data) != len(loaded_data):
                      task_logger.warning(f"State file {state_file} contained non-string or empty items. Filtering them out.")
                processed_subfolders = validated_data
                task_logger.info(f"Loaded {len(processed_subfolders)} processed subfolder paths from {state_file}")
            else:
                 task_logger.warning(f"State file {state_file} did not contain a set. Re-initializing state. File content type: {type(loaded_data)}")
        except (pickle.UnpicklingError, EOFError, TypeError, ValueError) as e:
            task_logger.warning(f"Error loading state file {state_file}: {e}. Assuming empty state and attempting to remove corrupt file.")
            try:
                 os.remove(state_file)
            except OSError as rm_err:
                 task_logger.error(f"Could not remove corrupted state file {state_file}: {rm_err}")
        except FileNotFoundError:
            task_logger.info(f"State file {state_file} disappeared after check. Assuming empty state.")
        except Exception as e:
            task_logger.error(f"Unexpected error loading state file {state_file}: {e}", exc_info=True)
    else:
        task_logger.info(f"State file {state_file} not found. Assuming no subfolders processed previously.")
    return config, processed_subfolders

def _unpack_state_data(state_tuple: Tuple[Dict[str, Any], Set[str]]) -> Dict[str, Any]:
    task_logger = logging.getLogger(__name__)
    if not isinstance(state_tuple, tuple) or len(state_tuple) != 2:
        err_msg = f"Expected a tuple of length 2 for state data, but received: {type(state_tuple)}"
        task_logger.error(err_msg)
        raise ValueError(err_msg)

    config, processed_set = state_tuple

    if not isinstance(config, dict):
         task_logger.warning(f"Expected first element of state tuple to be a dict, got {type(config)}")
    if not isinstance(processed_set, set):
         task_logger.warning(f"Expected second element of state tuple to be a set, got {type(processed_set)}")
         try:
             processed_set = set(processed_set)
         except TypeError:
             task_logger.error("Could not convert second element of state tuple to a set.")

    unpacked_data = {"config": config, "processed_set": list(processed_set)}
    task_logger.info(f"Unpacked state data. Config keys: {list(config.keys())}, Processed items count: {len(unpacked_data['processed_set'])}")
    return unpacked_data

def prepare_extract_arguments(
    config: Dict[str, Any], unprocessed_subfolders: List[str]
) -> List[Dict[str, Any]]: 
    """
    Prepares a list of op_kwargs dictionaries for extract task expansion.

    Args:
        config: The main configuration dictionary.
        unprocessed_subfolders: List of subfolder paths to process.

    Returns:
        List of dictionaries, each suitable for op_kwargs of the extract task.
    """
    prep_logger = logging.getLogger(__name__) 
    if not unprocessed_subfolders: 
        prep_logger.info("No unprocessed subfolders provided to prepare_extract_arguments.")
       
        return [] 

    kwargs_list = [] 
    for subfolder in unprocessed_subfolders: 
        kwargs_list.append({"config": config, "subfolder_path": subfolder}) 
    prep_logger.info( 
        f"Prepared {len(kwargs_list)} sets of arguments for extraction." 
    )
    return kwargs_list 

def prepare_transform_arguments(config: Dict[str, Any], extracted_results: List[Optional[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    prep_logger = logging.getLogger(__name__)
    kwargs_list = []
    successful_extractions = 0
    if extracted_results is None: return []
    if not isinstance(extracted_results, list): extracted_results = [extracted_results]

    for result in extracted_results:
        if isinstance(result, dict) and result.get('status') == 'success' and 'temp_npz_path' in result and 'output_hdf5_path' in result:
            kwargs_list.append(
                {"transform_input_info": {
                       'input_subfolder_path': result.get('input_subfolder_path', 'unknown'),
                       'temp_npz_path': result['temp_npz_path'],
                       'output_hdf5_path': result['output_hdf5_path'],
                       'msgtypes': result.get('msgtypes', {}),
                    }, "config": config}
            )
            successful_extractions += 1
        else:
            input_path = result.get("input_subfolder_path", "unknown") if isinstance(result, dict) else "unknown"
            status = result.get("status", "unknown") if isinstance(result, dict) else "unknown"
            prep_logger.warning(f"Skipping transform arg prep for failed extraction. Input: {input_path}. Status: {status}.")

    prep_logger.info(f"Prepared {len(kwargs_list)} arguments for transform/load ({successful_extractions} successful extractions).")
    return kwargs_list

def _find_unprocessed_subfolders_logic(config_processed_tuple: Tuple[Dict[str, Any], Set[str]]) -> List[str]:
    task_logger = logging.getLogger(__name__)
    config, already_processed_subfolders = config_processed_tuple
    base_input_folder = config["base_input_folder"]
    unprocessed_subfolders_list = []
    task_logger.info(f"Scanning {base_input_folder} for ROS 2 subfolders (containing metadata.yaml)...")

    try:
        if not os.path.isdir(base_input_folder):
             task_logger.error(f"Base input directory not found or is not a directory: {base_input_folder}")
             raise FileNotFoundError(f"Base input directory not found or is not a directory: {base_input_folder}")

        all_items = os.listdir(base_input_folder)
        potential_subfolders = [
            os.path.join(base_input_folder, item) for item in all_items
            if os.path.isdir(os.path.join(base_input_folder, item))
        ]

        ros2_bag_folders = []
        for folder_path in potential_subfolders:
            if os.path.exists(os.path.join(folder_path, "metadata.yaml")):
                ros2_bag_folders.append(folder_path)
            else:
                 task_logger.debug(f"Skipping potential folder (no metadata.yaml): {folder_path}")

        all_folders_set = set(ros2_bag_folders)
        unprocessed_subfolders_set = all_folders_set - already_processed_subfolders
        unprocessed_subfolders_list = sorted(list(unprocessed_subfolders_set))

        task_logger.info(f"Found {len(all_folders_set)} total potential ROS 2 bag folders (with metadata.yaml).")
        task_logger.info(f"{len(already_processed_subfolders)} folders already marked as processed.")
        task_logger.info(f"Found {len(unprocessed_subfolders_list)} new/unprocessed ROS 2 folders to process.")
        if len(unprocessed_subfolders_list) < 10:
            task_logger.debug(f"Folders to process: {unprocessed_subfolders_list}")
        elif unprocessed_subfolders_list:
            task_logger.debug(f"Folders to process (first 5): {unprocessed_subfolders_list[:5]}...")

        if not unprocessed_subfolders_list:
            task_logger.info("No new ROS 2 subfolders found to process.")

    except FileNotFoundError:
        task_logger.error(f"Base input directory not found during scan: {base_input_folder}")
        return []
    except OSError as e:
        task_logger.error(f"Error listing or accessing directory {base_input_folder}: {e}", exc_info=True)
        raise

    return unprocessed_subfolders_list

def _extract_ros_data_logic(config: Dict[str, Any], subfolder_path: str) -> Optional[Dict[str, Any]]:
    import os
    import logging
    import time
    from pathlib import Path
    import numpy as np
    from rosbags.highlevel import AnyReader
    from rosbags.typesys import Stores, get_typestore, get_types_from_msg, TypesysError
    from typing import Dict, List, Optional, Any, Set 


   
    from preprocessing.ros_etl_utils import parse_external_msg_definitions, get_all_fields
   

    task_logger = logging.getLogger(__name__)
    task_logger.info(f"Starting ROS data extraction for subfolder: {subfolder_path}")
    output_folder = config['output_folder']
    ros_distro = config['ros_distro']
    custom_msg_definition_folders = config.get('custom_msg_definition_folders', [])

    temp_extraction_folder = os.path.join(output_folder, "_temp_extraction")
    try:
        os.makedirs(temp_extraction_folder, exist_ok=True)
        task_logger.info(f"Ensured temporary extraction directory exists: {temp_extraction_folder}")
    except OSError as e:
        task_logger.error(f"Failed to create temporary extraction directory {temp_extraction_folder}: {e}", exc_info=True)
        temp_extraction_folder = output_folder
        task_logger.warning(f"Falling back to using main output folder for temp file: {output_folder}")

    subfolder_name = os.path.basename(subfolder_path)
    safe_subfolder_name = "".join(c if c.isalnum() or c in ('_', '-') else '_' for c in subfolder_name)
    output_hdf5_filename = safe_subfolder_name + ".h5"
    output_hdf5_path = os.path.join(output_folder, output_hdf5_filename)
    temp_npz_filename = safe_subfolder_name + ".npz"
    temp_npz_path = os.path.join(temp_extraction_folder, temp_npz_filename)

    if not os.path.isdir(subfolder_path):
        task_logger.error(f"Input subfolder not found or not a directory: {subfolder_path}")
        return None

    try:
        typestore_enum = getattr(Stores, f"ROS2_{ros_distro.upper()}", None)
        if typestore_enum is None:
            task_logger.warning(f"Invalid ROS distro '{ros_distro}', falling back to ROS2_HUMBLE.")
            typestore_enum = Stores.ROS2_HUMBLE
        typestore = get_typestore(typestore_enum)
        task_logger.info(f"Using base typestore: {typestore_enum.name}")
        if custom_msg_definition_folders:
            external_types_to_register = parse_external_msg_definitions(custom_msg_definition_folders, task_logger)
            if external_types_to_register:
                task_logger.info(f"Registering {len(external_types_to_register)} external types...")
                try:
                    typestore.register(external_types_to_register)
                except Exception as reg_err:
                    task_logger.error(f"Failed during external types registration: {reg_err}", exc_info=True)
                    raise RuntimeError("Failed to register external message definitions.") from reg_err
    except Exception as e:
        task_logger.error(f"Error initializing typestore/loading external types: {e}", exc_info=True)
        raise

    all_topics_in_bag: Set[str] = set()
    msgtypes: Dict[str, str] = {}
    message_counts: Dict[str, int] = {}
    newly_registered_types_from_bag: Dict[str, Any] = {}
    all_fields_by_topic: Dict[str, List[str]] = {}
    start_time = time.time()

    try:
        path = Path(subfolder_path)
        with AnyReader([path], default_typestore=typestore) as reader:
            task_logger.info(f"Opened bag: {subfolder_path}. Connections: {len(reader.connections)}.")
            types_missing_def_from_bag = set()
            types_parse_failed_from_bag = set()
            for conn in reader.connections:
                topic = conn.topic; msgtype = conn.msgtype; msgcount = conn.msgcount
                all_topics_in_bag.add(topic)
                if topic not in msgtypes:
                    msgtypes[topic] = msgtype; message_counts[topic] = msgcount
                else:
                    if msgtypes[topic] != msgtype: task_logger.warning(f"Multiple types for topic '{topic}'. Using '{msgtypes[topic]}'.")
                    if conn.msgcount is not None:
                        message_counts[topic] = (message_counts.get(topic) or 0) + conn.msgcount

                if '/' in conn.msgtype and conn.msgtype not in typestore.types and conn.msgtype not in newly_registered_types_from_bag:
                    msgdef_to_parse = getattr(conn, 'msgdef', '')
                    if not msgdef_to_parse and hasattr(conn, 'ext') and hasattr(conn.ext, 'rosbag2') and hasattr(conn.ext.rosbag2, 'msgdef'):
                        msgdef_to_parse = conn.ext.rosbag2.msgdef
                    if msgdef_to_parse:
                        try:
                            type_dict = get_types_from_msg(msgdef_to_parse, conn.msgtype)
                            new_types = {k: v for k, v in type_dict.items() if k not in typestore.types and k not in newly_registered_types_from_bag}
                            if new_types: newly_registered_types_from_bag.update(new_types)
                        except TypesysError as e: types_parse_failed_from_bag.add(conn.msgtype)
                        except Exception as e: types_parse_failed_from_bag.add(conn.msgtype)
                    else: types_missing_def_from_bag.add(conn.msgtype)

            if types_parse_failed_from_bag: task_logger.error(f"Failed to parse defs from bag: {types_parse_failed_from_bag}")
            if newly_registered_types_from_bag:
                task_logger.info(f"Registering {len(newly_registered_types_from_bag)} types from bag...")
                try: typestore.register(newly_registered_types_from_bag)
                except Exception as e: task_logger.error(f"Failed registering types from bag: {e}", exc_info=True)

            for topic in sorted(list(all_topics_in_bag)):
                 msg_type_name = msgtypes.get(topic)
                 if msg_type_name and msg_type_name in typestore.types: all_fields_by_topic[topic] = get_all_fields(msg_type_name, typestore)
                 else: all_fields_by_topic[topic] = []

            extracted_data_by_topic: Dict[str, Dict[str, list]] = {}
            for topic, fields in all_fields_by_topic.items():
                 if fields: extracted_data_by_topic[topic] = {'timestamps': [], 'data': {field: [] for field in fields}}

            processed_count = 0
            total_messages_expected = sum(mc for mc in message_counts.values() if mc is not None)
            log_interval = max(1000, total_messages_expected // 20) if total_messages_expected > 0 else 1000
            valid_connections = [c for c in reader.connections if c.topic in all_fields_by_topic and all_fields_by_topic[c.topic]]
            task_logger.info(f"Processing messages from {len(valid_connections)} valid connections.")

            if valid_connections:
                def flatten_msg_data(msg_obj, prefix='', target_dict=None):
                    # (Same flatten_msg_data internal logic as before)
                    if target_dict is None: target_dict = {}
                    if msg_obj is None: return target_dict
                    if isinstance(msg_obj, (int, float, bool, str, np.ndarray)): return target_dict
                    fields_to_check = getattr(msg_obj, '__slots__', [])
                    if not fields_to_check:
                        fields_to_check = [attr for attr in dir(msg_obj) if not attr.startswith('_') and not callable(getattr(msg_obj, attr))]
                    for field_name in fields_to_check:
                        flat_field_name = f"{prefix}{field_name}"
                        try:
                            field_value = getattr(msg_obj, field_name)
                            if flat_field_name in extracted_data_by_topic[topic]['data']:
                                if isinstance(field_value, (int, float, bool, str, np.ndarray)):
                                    target_dict[flat_field_name] = field_value
                                elif type(field_value).__name__ in ('Time', 'Duration') and hasattr(field_value, 'sec') and hasattr(field_value, 'nanosec'):
                                    target_dict[flat_field_name] = field_value.sec + field_value.nanosec * 1e-9
                            is_complex_type = hasattr(field_value, '__slots__') or (isinstance(field_value, object) and not isinstance(field_value, (int, float, bool, str, np.ndarray)))
                            needs_recursion = any(f.startswith(flat_field_name + '_') for f in extracted_data_by_topic[topic]['data'])
                            if is_complex_type and needs_recursion:
                                 if not isinstance(field_value, (list, tuple)):
                                    flatten_msg_data(field_value, prefix=f"{flat_field_name}_", target_dict=target_dict)
                        except AttributeError: pass
                        except Exception: pass
                    return target_dict

                for conn, timestamp, rawdata in reader.messages(connections=valid_connections):
                    topic = conn.topic
                    if topic in extracted_data_by_topic:
                        try: msg = typestore.deserialize_cdr(rawdata, conn.msgtype)
                        except Exception: continue
                        extracted_data_by_topic[topic]['timestamps'].append(timestamp / 1e9)
                        current_msg_flat_data = flatten_msg_data(msg)
                        expected_fields = extracted_data_by_topic[topic]['data'].keys()
                        for field_key in expected_fields:
                            extracted_data_by_topic[topic]['data'][field_key].append(current_msg_flat_data.get(field_key, None))
                        processed_count += 1
                        if processed_count % log_interval == 0: task_logger.info(f"Processed {processed_count}/{total_messages_expected} messages...")
            task_logger.info(f"Finished iterating messages. Processed {processed_count} messages total.")

    except Exception as e:
        task_logger.error(f"Failed read/process bag {subfolder_path}: {e}", exc_info=True)
        return None

    final_extracted_data_np: Dict[str, Dict[str, np.ndarray]] = {}
    conversion_errors = 0; empty_topics = 0
    for topic, data_dict in extracted_data_by_topic.items():
        timestamps_list = data_dict.get('timestamps', [])
        if not timestamps_list: empty_topics += 1; continue
        ts_count = len(timestamps_list); final_topic_data_np = {}; field_errors = 0
        try: timestamps_np = np.array(timestamps_list, dtype=np.float64)
        except Exception: empty_topics +=1; continue
        for field, values_list in data_dict['data'].items():
            if len(values_list) != ts_count: values_list.extend([None] * (ts_count - len(values_list)))
            try: final_topic_data_np[field] = np.array(values_list, dtype=object)
            except Exception: field_errors += 1; continue
        if field_errors > 0: conversion_errors += field_errors
        if not final_topic_data_np: empty_topics += 1; continue
        final_extracted_data_np[topic] = {'timestamps': timestamps_np, 'data': final_topic_data_np}

    total_time = time.time() - start_time
    task_logger.info(f"Finished extraction/conversion for {subfolder_path} in {total_time:.2f}s.")
    if not final_extracted_data_np:
        task_logger.error(f"No data extracted/converted for {subfolder_path}.")
        return None

    task_logger.info(f"Saving extracted data to temporary file: {temp_npz_path}")
    save_start_time = time.time()
    try:
        data_to_save = {}
        for topic, topic_data in final_extracted_data_np.items():
            safe_topic_key = topic.replace('/', '_').strip('_') or 'root'
            data_to_save[f"{safe_topic_key}__timestamps"] = topic_data['timestamps']
            for field, array in topic_data['data'].items():
                data_to_save[f"{safe_topic_key}__data__{field}"] = array
        np.savez_compressed(temp_npz_path, **data_to_save)
        task_logger.info(f"Saved data to {temp_npz_path} in {time.time() - save_start_time:.2f}s")
    except Exception as save_err:
        task_logger.error(f"Failed save NPZ {temp_npz_path}: {save_err}", exc_info=True)
        if os.path.exists(temp_npz_path):
            try: os.remove(temp_npz_path)
            except OSError: pass
        return None

    return {'status': 'success', 'input_subfolder_path': subfolder_path, 'output_hdf5_path': output_hdf5_path, 'temp_npz_path': temp_npz_path, 'msgtypes': msgtypes}

def _transform_load_ros_data_logic(transform_input_info: Dict[str, Any], config: Dict[str, Any]) -> Optional[Dict[str, str]]:
    # Imports needed within the virtualenv process for this function
    import logging
    import os
    import time
    import numpy as np
    import tables
    from typing import Dict, Optional, Any # Explicit typing imports

    # Assuming these utils are importable within the virtualenv's python path
    try:
        from preprocessing.ros_etl_utils import save_ros_topics_to_pytables, sanitize_hdf5_identifier
    except ImportError:
        try:
            from ros_etl_utils import save_ros_topics_to_pytables, sanitize_hdf5_identifier
        except ImportError as e:
             logging.getLogger(__name__).critical(f"Failed to import ros_etl_utils writer/sanitizer: {e}", exc_info=True)
             raise

    task_logger = logging.getLogger(__name__)
    if transform_input_info is None: return None

    temp_npz_path = transform_input_info.get('temp_npz_path')
    output_hdf5_path = transform_input_info.get('output_hdf5_path')
    input_subfolder_path = transform_input_info.get('input_subfolder_path', 'unknown')

    if not temp_npz_path or not output_hdf5_path:
         task_logger.error(f"Missing path info for {input_subfolder_path}. Cannot proceed.")
         return {'input_subfolder_path': input_subfolder_path, 'status': 'failed_missing_path'}

    writer_func = save_ros_topics_to_pytables
    writer_func_name = writer_func.__name__

    task_logger.info(f"Loading extracted data from: {temp_npz_path}")
    extracted_data = {}
    try:
        if not os.path.exists(temp_npz_path): raise FileNotFoundError(f"NPZ file missing: {temp_npz_path}")
        load_start_time = time.time()
        with np.load(temp_npz_path, allow_pickle=False) as npz_file:
            reconstructed_data = {}
            for key in npz_file.keys():
                parts = key.split('__')
                if len(parts) < 2: continue
                topic_key = parts[0]; data_type = parts[1]
                if topic_key not in reconstructed_data: reconstructed_data[topic_key] = {'timestamps': None, 'data': {}}
                if data_type == 'timestamps': reconstructed_data[topic_key]['timestamps'] = npz_file[key]
                elif data_type == 'data' and len(parts) == 3: reconstructed_data[topic_key]['data'][parts[2]] = npz_file[key]
            extracted_data = reconstructed_data
            task_logger.info(f"Loaded data from {temp_npz_path} in {time.time() - load_start_time:.2f}s")
    except FileNotFoundError:
         task_logger.error(f"NPZ file not found: {temp_npz_path}")
         return {'input_subfolder_path': input_subfolder_path, 'status': 'failed_npz_not_found'}
    except Exception as load_err:
        task_logger.error(f"Failed load NPZ {temp_npz_path}: {load_err}", exc_info=True)
        return {'input_subfolder_path': input_subfolder_path, 'status': 'failed_npz_load'}

    if not extracted_data:
        task_logger.warning(f"No data loaded from NPZ for {input_subfolder_path}.")
        if os.path.exists(temp_npz_path):
             try: os.remove(temp_npz_path)
             except OSError: pass
        return None

    task_logger.info(f"Preparing data for HDF5: {output_hdf5_path}")
    data_to_write: Dict[str, Dict[str, Any]] = {}
    preparation_start_time = time.time()

    for topic_key, topic_data in extracted_data.items():
        timestamps = topic_data.get('timestamps'); data_fields = topic_data.get('data', {})
        if timestamps is None or not isinstance(timestamps, np.ndarray) or timestamps.size == 0: continue
        if not data_fields: continue; num_rows = len(timestamps)
        if num_rows == 0: continue
        dtype_list = [('timestamp_s', np.float64)]
        structured_array_data_input = {'timestamp_s': timestamps.astype(np.float64)}
        valid_fields_count = 0
        for col_name, data_array in data_fields.items():
            if not isinstance(data_array, np.ndarray): continue
            if len(data_array) != num_rows: continue
            sanitized_col_name = sanitize_hdf5_identifier(col_name)
            if sanitized_col_name in structured_array_data_input: continue
            target_np_dtype = None; current_shape = (); final_data_for_col = None
            try: # Simplified Type Handling Logic - Ensure it matches your needs
                if data_array.dtype == 'O':
                    first_elem = next((item for item in data_array if item is not None), None)
                    if isinstance(first_elem, (np.ndarray, list, tuple)): continue
                    if first_elem is None: target_np_dtype=np.float64; final_data_for_col=np.full(num_rows, np.nan, dtype=target_np_dtype)
                    elif isinstance(first_elem, str): max_len=max((len(s) for s in data_array if isinstance(s,str)),default=1); target_np_dtype=f'S{max_len}'; final_data_for_col=np.array([s.encode('utf-8','replace')[:max_len] if isinstance(s,str) else b'' for s in data_array],dtype=target_np_dtype)
                    elif isinstance(first_elem, bytes): max_len=max((len(b) for b in data_array if isinstance(b,bytes)),default=1); target_np_dtype=f'S{max_len}'; final_data_for_col=np.array([b[:max_len] if isinstance(b,bytes) else b'' for b in data_array],dtype=target_np_dtype)
                    elif isinstance(first_elem, bool): target_np_dtype=np.bool_; final_data_for_col=np.array([x if isinstance(x,bool) else False for x in data_array],dtype=target_np_dtype)
                    elif isinstance(first_elem, int): target_np_dtype=np.int64; final_data_for_col=np.array([x if isinstance(x,int) else 0 for x in data_array],dtype=target_np_dtype)
                    elif isinstance(first_elem, float): target_np_dtype=np.float64; final_data_for_col=np.array([x if isinstance(x,float) else np.nan for x in data_array],dtype=target_np_dtype)
                    else: continue
                else: target_np_dtype=data_array.dtype; final_data_for_col=data_array;
                if data_array.ndim>1: current_shape=data_array.shape[1:]
                if target_np_dtype is not None and final_data_for_col is not None:
                    dtype_spec=(target_np_dtype,current_shape) if current_shape else target_np_dtype
                    dtype_list.append((sanitized_col_name,dtype_spec)); structured_array_data_input[sanitized_col_name]=final_data_for_col; valid_fields_count+=1
                else: continue
            except Exception: continue
        if valid_fields_count == 0: continue
        try:
            final_dtype_list = [item for item in dtype_list if item[0] in structured_array_data_input]
            if len(final_dtype_list) <= 1: continue
            final_dtype_np = np.dtype(final_dtype_list)
            description_object, byteorder = tables.descr_from_dtype(final_dtype_np)
            structured_array = np.empty(num_rows, dtype=description_object._v_dtype)
            for col_name_sanitized in description_object._v_dtype.names: structured_array[col_name_sanitized] = structured_array_data_input[col_name_sanitized]
            path_parts = [sanitize_hdf5_identifier(part) for part in topic_key.split('_') if part]
            table_path = '/' + '/'.join(path_parts) if path_parts else '/unknown_topic'
            data_to_write[table_path] = {'description': description_object, 'data': structured_array}
        except Exception as e: task_logger.error(f"Final Prep Error: {topic_key}: {e}", exc_info=True); continue

    task_logger.info(f"Finished data preparation for {len(data_to_write)} tables in {time.time() - preparation_start_time:.2f}s.")
    if not data_to_write:
        task_logger.error(f"No topics prepared for writing for {input_subfolder_path}.")
        if os.path.exists(temp_npz_path):
             try: os.remove(temp_npz_path)
             except OSError: pass
        return None

    write_success = False; final_status = 'failed_writer_exception'
    try:
        write_success = writer_func(output_hdf5_path, data_to_write)
        if write_success:
            task_logger.info(f"HDF5 writer SUCCESS for {input_subfolder_path}")
            final_status = 'success'
            if os.path.exists(temp_npz_path):
                try: os.remove(temp_npz_path)
                except OSError: final_status = 'success_npz_cleanup_failed'
            return {'input_subfolder_path': input_subfolder_path, 'status': final_status}
        else:
            task_logger.error(f"HDF5 writer FAILURE for {input_subfolder_path}.")
            final_status = 'failed_write'
            return {'input_subfolder_path': input_subfolder_path, 'status': final_status}
    except Exception as writer_e:
        task_logger.critical(f"HDF5 writer EXCEPTION for {input_subfolder_path}: {writer_e}", exc_info=True)
        return {'input_subfolder_path': input_subfolder_path, 'status': 'failed_writer_exception'}

def _log_processed_subfolders_logic(
    processed_results: List[Optional[Dict[str, str]]],
    config: Dict[str, Any],
    previously_processed_subfolders: List[str]
) -> None:
    task_logger = logging.getLogger(__name__)
    task_logger.info("Logging processed subfolder state.")

    try:
        if not isinstance(previously_processed_subfolders, list):
            task_logger.warning(f"Received 'previously_processed_subfolders' as type {type(previously_processed_subfolders)}, expected list. Attempting conversion.")
        previously_processed_set = set(previously_processed_subfolders)
        task_logger.debug(f"Converted previously processed list (size {len(previously_processed_subfolders)}) back to set (size {len(previously_processed_set)}).")
    except TypeError as e:
        task_logger.error(f"Could not convert 'previously_processed_subfolders' list back to a set: {e}. Initializing with an empty set.", exc_info=True)
        previously_processed_set = set()

    successfully_processed_info_this_run = [
        item for item in processed_results
        if isinstance(item, dict) and 'input_subfolder_path' in item and item.get('status') == 'success'
    ]

    if not successfully_processed_info_this_run:
        task_logger.info("No new subfolders were successfully processed and loaded in this run. State file not updated.")
        return

    newly_processed_subfolder_paths_this_run = {info['input_subfolder_path'] for info in successfully_processed_info_this_run}
    task_logger.info(f"Identified {len(newly_processed_subfolder_paths_this_run)} newly processed subfolders in this run.")
    if len(newly_processed_subfolder_paths_this_run) < 10:
        task_logger.debug(f"Newly processed subfolders this run: {newly_processed_subfolder_paths_this_run}")

    updated_folders_set = previously_processed_set.union(newly_processed_subfolder_paths_this_run)

    state_file = os.path.join(config['output_folder'], "processed_ros2_subfolders.pkl")
    task_logger.info(f"Preparing to write updated state to {state_file}. Total processed count: {len(updated_folders_set)}")

    try:
        os.makedirs(config['output_folder'], exist_ok=True)
        with open(state_file, 'wb') as f:
            pickle.dump(updated_folders_set, f, protocol=pickle.HIGHEST_PROTOCOL)
        task_logger.info(f"Successfully updated processed subfolders state log at {state_file}.")
    except FileNotFoundError:
        task_logger.critical(f"CRITICAL: Output directory {config['output_folder']} not found while trying to write state file {state_file}.")
        raise IOError(f"Output directory lost, cannot save state file: {state_file}")
    except OSError as e:
        task_logger.critical(f"CRITICAL: OS error writing state file {state_file}: {e}", exc_info=True)
        raise IOError(f"OS error writing state file: {state_file}") from e
    except pickle.PicklingError as e:
        task_logger.critical(f"CRITICAL: Failed to serialize updated processed subfolders set to {state_file}: {e}", exc_info=True)
        raise IOError(f"Failed to pickle state to {state_file}") from e
    except Exception as e:
        task_logger.critical(f"CRITICAL: Unexpected error writing state file {state_file}: {e}", exc_info=True)
        raise IOError(f"Unexpected error writing state file: {state_file}") from e

def save_ros_topics_to_pytables(output_hdf5_path: str, data_by_topic: Dict[str, Dict[str, Any]]) -> bool:
    writer_logger = logging.getLogger(__name__)
    writer_logger.info(f"Opening HDF5 file '{output_hdf5_path}' for writing {len(data_by_topic)} topics/tables.")

    output_dir = os.path.dirname(output_hdf5_path)
    try:
         os.makedirs(output_dir, exist_ok=True)
    except OSError as e:
         writer_logger.error(f"Failed to ensure output directory exists {output_dir}: {e}", exc_info=True)
         return False

    topics_written = 0
    try:
        with tables.open_file(output_hdf5_path, mode="w", title="Processed ROS Bag Data") as h5file:
            filters = tables.Filters(complib='zlib', complevel=5)

            for table_path, table_content in data_by_topic.items():
                description = table_content.get('description')
                structured_data = table_content.get('data')

                if description is None or structured_data is None:
                    writer_logger.warning(f"Skipping table path '{table_path}' due to missing description or data.")
                    continue
                if not isinstance(description, tables.Description):
                    writer_logger.error(f"Invalid description type for table '{table_path}': {type(description)}. Expected tables.Description. Skipping.")
                    continue
                if not isinstance(structured_data, np.ndarray):
                     writer_logger.error(f"Invalid data type for table '{table_path}': {type(structured_data)}. Expected numpy.ndarray. Skipping.")
                     continue

                try:
                    if not table_path.startswith('/'): table_path = '/' + table_path
                    parent_path, original_table_name = os.path.split(table_path)

                    table_name = sanitize_hdf5_identifier(original_table_name)
                    if table_name != original_table_name:
                         writer_logger.debug(f"Table name '{original_table_name}' sanitized to '{table_name}' for path '{table_path}'")

                    parent_node = h5file.root
                    if parent_path and parent_path != '/':
                         components = parent_path.strip('/').split('/')
                         current_node = h5file.root
                         for component in components:
                              sanitized_component = sanitize_hdf5_identifier(component)
                              if not hasattr(current_node, sanitized_component):
                                   writer_logger.debug(f"Creating group '{sanitized_component}' under '{current_node._v_pathname}'")
                                   current_node = h5file.create_group(current_node, sanitized_component, title=f"Group {sanitized_component}")
                              else:
                                   current_node = getattr(current_node, sanitized_component)
                                   if not isinstance(current_node, tables.Group):
                                        raise IOError(f"Expected node '{current_node._v_pathname}' to be a Group, but found {type(current_node)}")
                         parent_node = current_node

                    if hasattr(parent_node, table_name):
                         writer_logger.error(f"Node '{table_name}' already exists in group '{parent_node._v_pathname}'. Cannot create table. Path: {table_path}")
                         continue

                    writer_logger.debug(f"Creating table '{table_name}' in group '{parent_node._v_pathname}' with {len(structured_data)} rows")
                    data_table = h5file.create_table(
                        where=parent_node,
                        name=table_name,
                        description=description,
                        title=f"Data for topic originally at {original_table_name}",
                        filters=filters,
                        expectedrows=len(structured_data) if len(structured_data) > 0 else 1000
                    )

                    if len(structured_data) > 0:
                         data_table.append(structured_data)
                         data_table.flush()

                    final_table_node = h5file.get_node(parent_node, table_name)
                    final_table_path = final_table_node._v_pathname
                    writer_logger.debug(f"Successfully wrote {len(structured_data)} rows to table '{final_table_path}'")
                    topics_written += 1

                except Exception as node_create_e:
                    writer_logger.error(f"Failed during group/table creation or writing for '{table_path}' (Table: '{table_name}'): {node_create_e}", exc_info=True)
                    continue

            writer_logger.info(f"Finished writing loop. Attempted to write {len(data_by_topic)} topics, successfully wrote {topics_written} tables to {output_hdf5_path}")
            
            return True 

    except tables.HDF5ExtError as hdf5_err:
        writer_logger.error(f"PyTables HDF5 Error accessing file {output_hdf5_path}: {hdf5_err}", exc_info=True)
    except OSError as os_err:
        writer_logger.error(f"OS Error during file operation for {output_hdf5_path}: {os_err}", exc_info=True)
    except Exception as e:
        writer_logger.error(f"Unexpected error during PyTables file write operation for {output_hdf5_path}: {e}", exc_info=True)

    if os.path.exists(output_hdf5_path):
        writer_logger.warning(f"Attempting to remove potentially incomplete file: {output_hdf5_path} due to error during writing.")
        try:
            os.remove(output_hdf5_path)
            writer_logger.info(f"Removed failed/incomplete file: {output_hdf5_path}")
        except OSError as rm_err:
            writer_logger.error(f"Failed to remove partially created/failed file {output_hdf5_path}: {rm_err}")

    return False
