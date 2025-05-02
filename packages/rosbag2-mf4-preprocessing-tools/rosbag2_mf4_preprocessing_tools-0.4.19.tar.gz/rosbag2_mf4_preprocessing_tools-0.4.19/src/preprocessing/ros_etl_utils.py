# -*- coding: utf-8 -*-
import os
import pickle
import logging
from typing import Dict, List, Optional, Any, Set, Type, Tuple, Union
import importlib
import traceback
import re
import keyword
import time
import sys
from pathlib import Path



logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def sanitize_hdf5_identifier(name: str) -> str:
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    if sanitized and sanitized[0].isdigit():
        sanitized = '_' + sanitized
    if keyword.iskeyword(sanitized):
        sanitized += '_'
    if not sanitized:
        return 'empty_name'
    return sanitized

def get_all_fields(typename: str, typestore: Any, current_prefix: str = '', visited: Optional[Set[str]] = None) -> List[Tuple[str, str, bool]]:
    """
    Recursively finds all flattened field paths within a given ROS message type.
    Handles potential errors when accessing type definitions. Uses venv_logger.
    Correctly parses rosbags field type info structure based on Nodetype.
    """
    from rosbags.typesys.types import Nodetype
    venv_logger = logging.getLogger(__name__)
    if visited is None: visited = set()
    if typename in visited: return []
    visited.add(typename)
    fields_list = []

    try:
        if typename not in typestore.types:
             known_types_sample = list(typestore.types.keys())[:20]
             venv_logger.warning(f"Type '{typename}' not found in typestore. Known types sample: {known_types_sample}...")
             return []
        msg_def = typestore.get_msgdef(typename)
        field_defs = msg_def.fields
    except AttributeError:
         venv_logger.warning(f"Type '{typename}' definition in typestore lacks 'fields' attribute or is not a complex type.")
         return []
    except KeyError:
        venv_logger.warning(f"Type '{typename}' definition not found in typestore during field recursion (KeyError).")
        return []
    except Exception as e:
         venv_logger.error(f"Unexpected error accessing definition for type '{typename}': {e}", exc_info=True)
         return []
    if isinstance(field_defs, dict):
        field_iterator = field_defs.items()
    elif isinstance(field_defs, (list, tuple)):
        field_iterator = field_defs
    else:
        venv_logger.error(f"Unexpected structure for field definitions of type '{typename}': {type(field_defs)}. Cannot iterate fields.")
        field_iterator = []
    for field_info in field_iterator:
        try:
            field_name, field_type_tuple = field_info # Expecting (name, (nodetype, details))
        except (TypeError, ValueError):
            venv_logger.warning(f"Unexpected element structure in field definitions for type '{typename}': {field_info}. Skipping element.")
            continue
        flat_name = f"{current_prefix}{field_name}"
        is_array = False
        element_type_name = None
        # <<< FIX: Parse field_type_tuple based on Nodetype >>>
        try:
            # Ensure it's a tuple with at least 2 elements before unpacking
            if not isinstance(field_type_tuple, tuple) or len(field_type_tuple) < 2:
                 venv_logger.warning(f"Unexpected field_type_info format for field '{flat_name}': {field_type_tuple}. Skipping.")
                 continue
            node_type_enum, type_details = field_type_tuple
            # Handle potential direct enum member or integer value
            if isinstance(node_type_enum, Nodetype):
                node_type = node_type_enum
            else:
                node_type = Nodetype(node_type_enum) # Convert int to enum member
            if node_type == Nodetype.BASE:
                # type_details is like ('float64', 0) or ('string', 10)
                if isinstance(type_details, (list, tuple)) and len(type_details) > 0:
                    element_type_name = type_details[0] # The primitive type name
                else:
                    venv_logger.warning(f"Unexpected type_details format for Nodetype.BASE: {type_details}. Field: '{flat_name}'. Skipping.")
                    continue
                is_array = False
            elif node_type == Nodetype.NAME:
                # type_details is like 'std_msgs/msg/Header'
                if isinstance(type_details, str):
                    element_type_name = type_details
                else:
                    venv_logger.warning(f"Unexpected type_details format for Nodetype.NAME: {type_details}. Field: '{flat_name}'. Skipping.")
                    continue
                is_array = False
            elif node_type == Nodetype.ARRAY or node_type == Nodetype.SEQUENCE:
                # type_details is like ((<Nodetype.BASE: 1>, ('float64', 0)), 9) for ARRAY
                # or ((<Nodetype.NAME: 2>, 'geometry_msgs/msg/Point'), 0) for SEQUENCE
                if not isinstance(type_details, (list, tuple)) or len(type_details) < 1:
                     venv_logger.warning(f"Unexpected type_details format for {node_type}: {type_details}. Field: '{flat_name}'. Skipping.")
                     continue
                element_type_tuple = type_details[0] # This is another (nodetype, details) tuple for the element
                if not isinstance(element_type_tuple, (list, tuple)) or len(element_type_tuple) < 2:
                     venv_logger.warning(f"Unexpected element_type_tuple format for {node_type}: {element_type_tuple}. Field: '{flat_name}'. Skipping.")
                     continue
                element_nodetype_enum, element_details = element_type_tuple
                if isinstance(element_nodetype_enum, Nodetype):
                    element_nodetype = element_nodetype_enum
                else:
                    element_nodetype = Nodetype(element_nodetype_enum)
                if element_nodetype == Nodetype.BASE:
                    if isinstance(element_details, (list, tuple)) and len(element_details) > 0:
                        element_type_name = element_details[0]
                    else:
                         venv_logger.warning(f"Unexpected element_details format for {node_type} -> BASE: {element_details}. Field: '{flat_name}'. Skipping.")
                         continue
                elif element_nodetype == Nodetype.NAME:
                    if isinstance(element_details, str):
                        element_type_name = element_details
                    else:
                         venv_logger.warning(f"Unexpected element_details format for {node_type} -> NAME: {element_details}. Field: '{flat_name}'. Skipping.")
                         continue
                else:
                     venv_logger.warning(f"Nested {node_type} of {element_nodetype} not fully handled for field '{flat_name}'. Skipping.")
                     continue
                is_array = True
            else:
                 venv_logger.warning(f"Unhandled Nodetype '{node_type}' for field '{flat_name}'. Skipping.")
                 continue
        except (IndexError, ValueError, TypeError) as parse_err:
            venv_logger.warning(f"Error parsing field type tuple for field '{flat_name}' (type: {typename}, info: {field_type_tuple}): {parse_err}. Skipping.")
            continue
        # <<< END FIX >>>
        if element_type_name is None:
             venv_logger.warning(f"Could not determine element type name for field '{field_name}' (type: {typename}, info: {field_type_tuple}). Skipping.")
             continue
        is_complex = False
        if element_type_name in typestore.types:
            try:
                element_msg_def = typestore.get_msgdef(element_type_name)
                if hasattr(element_msg_def, 'fields') and element_msg_def.fields:
                     is_complex = True
            except Exception:
                 pass
        if is_complex:
             nested_fields = get_all_fields(element_type_name, typestore, f"{flat_name}_", visited.copy())
             if nested_fields:
                 if is_array:
                      venv_logger.warning(f"Field '{flat_name}' is an array of complex type '{element_type_name}'. Skipping detailed fields.")
                 else:
                      fields_list.extend(nested_fields)
             elif not is_array:
                 fields_list.append((flat_name, element_type_name, is_array))
        else:
             fields_list.append((flat_name, element_type_name, is_array))
    return fields_list

def parse_external_msg_definitions(
    definition_folders: List[str],
    venv_logger: logging.Logger
) -> Dict[str, str]:
    all_external_defs: Dict[str, str] = {}
    files_processed = 0
    parse_errors = 0

    if not definition_folders:
        venv_logger.info("No external definition folders provided to parse.")
        return {}

    venv_logger.info(f"Scanning for .msg files in: {definition_folders}")

    for folder_path_str in definition_folders:
        base_path = Path(folder_path_str)
        if not base_path.is_dir():
            venv_logger.warning(f"Provided definition path is not a directory, skipping: {folder_path_str}")
            continue

        venv_logger.info(f"Searching for .msg files recursively in {base_path}...")
        try:
            msg_files = list(base_path.rglob('*.msg'))
            venv_logger.info(f"Found {len(msg_files)} .msg files in {base_path}.")
        except OSError as e:
            venv_logger.error(f"Error scanning directory {base_path}: {e}. Skipping this path.")
            continue

        for msg_file_path in msg_files:
            files_processed += 1
            try:
                relative_path = msg_file_path.relative_to(base_path)
                parts = relative_path.parts

                pkg_name = parts[0] if parts else None
                msg_dir_index = -1
                for i, part in enumerate(parts):
                    if part in ('msg', 'srv', 'action'):
                        msg_dir_index = i
                        break

                if pkg_name and msg_dir_index != -1 and msg_dir_index + 1 < len(parts):
                    type_stem = msg_file_path.stem
                    ros_type_name = f"{pkg_name}/{parts[msg_dir_index]}/{type_stem}"
                else:
                    venv_logger.warning(f"Could not determine ROS type name from path structure: {msg_file_path}. Relative path: {relative_path}. Skipping file.")
                    continue

                venv_logger.debug(f"Reading {msg_file_path} for type {ros_type_name}")
                content = msg_file_path.read_text(encoding='utf-8')

                if ros_type_name in all_external_defs:
                    venv_logger.warning(f"Duplicate definition found for type '{ros_type_name}' from file {msg_file_path}. Overwriting previous definition.")
                all_external_defs[ros_type_name] = content
                venv_logger.debug(f"Stored definition for {ros_type_name}")

            except OSError as e:
                venv_logger.error(f"Error reading file {msg_file_path}: {e}", exc_info=False)
                parse_errors += 1
            except Exception as e:
                venv_logger.error(f"Unexpected error processing {msg_file_path}: {e}", exc_info=False)
                parse_errors += 1

    venv_logger.info(f"Finished scanning external definition folders. Processed {files_processed} files.")
    if parse_errors > 0:
        venv_logger.error(f"Encountered {parse_errors} errors during external definition reading.")
    venv_logger.info(f"Collected {len(all_external_defs)} raw type definitions externally.")
    return all_external_defs


def get_config(**context) -> Dict[str, Any]:
    params = context['params']
    config = {
        'input_folder': params['input_folder'],
        'output_folder': params['output_folder'],
        'ros_distro': params.get('ros_distro', 'humble'),
        'custom_msg_definition_folders': params.get('custom_msg_definition_folders', []) or [],
        'timestamp_hdf5_name': params.get('timestamp_hdf5_name', 'timestamp_s'),
    }
    logger.info(f"Configuration: Input={config['input_folder']}, Output={config['output_folder']}, ROS Distro={config['ros_distro']}")
    if config['custom_msg_definition_folders']:
        logger.info(f"Custom .msg definition folders: {config['custom_msg_definition_folders']}")
    else:
        logger.info("No external custom .msg definition folders provided.")
    logger.info(f"Timestamp column name in HDF5: {config['timestamp_hdf5_name']}")
    return config

def create_directories(config: Dict[str, Any]) -> Dict[str, Any]:
    input_f = config['input_folder']
    output_f = config['output_folder']
    try:
        os.makedirs(input_f, exist_ok=True)
        os.makedirs(output_f, exist_ok=True)
        logger.info(f"Ensured directories exist: Input='{input_f}', Output='{output_f}'")
    except OSError as e:
        logger.error(f"Failed to create directories: {e}", exc_info=True)
        raise
    return config

def load_already_transformed_folders(config: Dict[str, Any]) -> Set[str]:
    pickle_path = os.path.join(config["output_folder"], "processed_rosbags_folders.pkl")
    already_transformed_folders: Set[str] = set()
    if os.path.exists(pickle_path):
        try:
            with open(pickle_path, 'rb') as f:
                loaded_data = pickle.load(f)
                if isinstance(loaded_data, set):
                    validated_data = {item for item in loaded_data if isinstance(item, str)}
                    if len(validated_data) != len(loaded_data):
                        logger.warning(f"State file {pickle_path} contained non-string items. Filtering them out.")
                    already_transformed_folders = validated_data
                    logger.info(f"Loaded {len(already_transformed_folders)} processed folder names from {pickle_path}")
                else:
                    logger.warning(f"State file {pickle_path} did not contain a set. Re-initializing state. File content type: {type(loaded_data)}")
        except (pickle.UnpicklingError, EOFError, TypeError, ValueError, Exception) as e:
            logger.warning(f"Error loading state file {pickle_path}: {e}. Assuming empty state and attempting to remove corrupt file.")
            try:
                os.remove(pickle_path)
                logger.info(f"Removed potentially corrupted state file: {pickle_path}")
            except OSError as rm_err:
                logger.error(f"Could not remove corrupted state file {pickle_path}: {rm_err}")
    else:
        logger.info(f"State file {pickle_path} not found. Assuming no folders processed previously.")
    return already_transformed_folders

def find_untransformed_folders(config: Dict[str, Any], already_transformed_folders: Set[str]) -> List[str]:
    input_folder = config["input_folder"]
    non_transformed_folders_list = []
    logger.info(f"Scanning {input_folder} for new rosbag folders (containing metadata.yaml)...")
    try:
        if not os.path.isdir(input_folder):
            logger.error(f"Input directory not found or is not a directory: {input_folder}")
            return []

        all_potential_folders = [os.path.join(input_folder, d) for d in os.listdir(input_folder)
                                 if os.path.isdir(os.path.join(input_folder, d))]

        rosbag_folders_paths = []
        for folder_path in all_potential_folders:
            metadata_path = os.path.join(folder_path, 'metadata.yaml')
            if os.path.isfile(metadata_path):
                rosbag_folders_paths.append(folder_path)
            else:
                logger.debug(f"Skipping '{os.path.basename(folder_path)}', does not contain metadata.yaml")

        all_found_folder_names = {os.path.basename(p) for p in rosbag_folders_paths}
        non_transformed_folder_names = sorted(list(all_found_folder_names - already_transformed_folders))

        non_transformed_folders_list = [os.path.join(input_folder, name) for name in non_transformed_folder_names]

        logger.info(f"Found {len(all_found_folder_names)} total potential rosbag folders.")
        logger.info(f"{len(already_transformed_folders)} folder names already processed.")
        logger.info(f"Found {len(non_transformed_folders_list)} new folders to process.")

    except FileNotFoundError:
        logger.error(f"Input directory not found during scan: {input_folder}")
        return []
    except OSError as e:
        logger.error(f"Error listing directory {input_folder}: {e}", exc_info=True)
        raise

    count = len(non_transformed_folders_list)
    if count > 0:
        display_limit = 5
        folder_names_to_display = [os.path.basename(p) for p in non_transformed_folders_list]
        if count > display_limit * 2:
            logger.info(f"Folders to process: {folder_names_to_display[:display_limit]}...{folder_names_to_display[-display_limit:]}")
        else:
            logger.info(f"Folders to process: {folder_names_to_display}")
    else:
        logger.info("No new folders found to process.")
    return non_transformed_folders_list


def prepare_extract_arguments(config: Dict[str, Any], untransformed_folder_paths: List[str]) -> List[Dict[str, Any]]:
    logger.info(f"Preparing extract arguments for {len(untransformed_folder_paths)} folders.")
    kwargs_list = []
    for folder_path in untransformed_folder_paths:
        kwargs_list.append({
            "config": config,
            "folder_path": folder_path
        })
    return kwargs_list

def prepare_transform_arguments(config: Dict[str, Any], extracted_results: List[Optional[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    logger.info(f"Preparing transform arguments based on {len(extracted_results)} results from extraction.")
    kwargs_list = []
    successful_extractions = 0
    for result in extracted_results:
        if result is not None and isinstance(result, dict) and result.get('extracted_data'):
            kwargs_list.append({
                "extracted_info": result,
                "config": config
            })
            successful_extractions += 1
        else:
            input_path = "unknown"
            if isinstance(result, dict):
                input_path = result.get("input_folder_path", "unknown")
            logger.warning(f"Skipping transform argument preparation for a None, empty, or invalid result from extraction. Input path (if known): {input_path}. Result: {result}")
    logger.info(f"Prepared {len(kwargs_list)} arguments for transform task (corresponding to {successful_extractions} successful extractions).")
    return kwargs_list


def extract(config: Dict[str, Any], folder_path: str) -> Optional[Dict[str, Any]]:
    import os
    import logging
    import numpy as np
    import sys
    import time
    from pathlib import Path

    import numpy as np

    from rosbags.highlevel import AnyReader
    from rosbags.typesys import Stores, get_typestore, get_types_from_msg
    from rosbags.serde import deserialize_cdr
    from rosbags.typesys.types import Nodetype


    from preprocessing.ros_etl_utils import sanitize_hdf5_identifier, parse_external_msg_definitions, get_all_fields
    

    venv_logger = logging.getLogger(f"{__name__}.extract_venv")

    venv_logger.info(f"Starting ROS data extraction using 'rosbags' for folder: {folder_path}")
    output_folder = config['output_folder']
    ros_distro = config.get('ros_distro', 'humble')
    custom_msg_definition_folders = config.get('custom_msg_definition_folders', [])

    folder_name = os.path.basename(folder_path)
    safe_folder_name = sanitize_hdf5_identifier(folder_name)
    output_hdf5_filename = f"{safe_folder_name}.h5"
    output_hdf5_path = os.path.join(output_folder, output_hdf5_filename)

    if not os.path.isdir(folder_path):
        venv_logger.error(f"Input folder not found or not a directory: {folder_path}")
        return None

    try:
        typestore_enum = getattr(Stores, f"ROS2_{ros_distro.upper()}", None)
        if typestore_enum is None:
            venv_logger.error(f"Invalid ROS distro '{ros_distro}' specified. Cannot find corresponding typestore in rosbags.Stores.")
            valid_distros = [s.name for s in Stores if s.name.startswith('ROS2_')]
            venv_logger.error(f"Available ROS 2 typestores in rosbags: {valid_distros}")
            venv_logger.warning(f"Falling back to default ROS2_HUMBLE typestore.")
            typestore_enum = Stores.ROS2_HUMBLE

        typestore = get_typestore(typestore_enum)
        venv_logger.info(f"Using base typestore: {typestore_enum.name}")

        if custom_msg_definition_folders:
            venv_logger.info("Parsing external message definitions...")
            external_type_defs = parse_external_msg_definitions(custom_msg_definition_folders, venv_logger)

            if external_type_defs:
                venv_logger.info(f"Registering {len(external_type_defs)} external types with the typestore...")
                types_to_register = {}
                registration_errors = 0
                for type_name, type_def_str in external_type_defs.items():
                    try:
                        parsed_types = get_types_from_msg(type_def_str, type_name)
                        types_to_register.update(parsed_types)
                    except SyntaxError as e:
                        venv_logger.error(f"Syntax error parsing definition for '{type_name}': {e}")
                        registration_errors += 1
                    except Exception as e:
                        venv_logger.error(f"Error processing definition for '{type_name}': {e}", exc_info=True)
                        registration_errors += 1

                if registration_errors > 0:
                    venv_logger.error(f"Encountered {registration_errors} errors during parsing of external definitions.")

                if types_to_register:
                    try:
                        typestore.register(types_to_register)
                        venv_logger.info(f"Registration of {len(types_to_register)} external types complete.")
                    except Exception as reg_err:
                        venv_logger.error(f"Failed during typestore.register call for external types: {reg_err}", exc_info=True)
                        raise RuntimeError("Failed to register required external message definitions.") from reg_err
                else:
                    venv_logger.warning("No valid types could be parsed from the provided external definition files.")
            else:
                venv_logger.info("No external types found or parsed from provided folders.")
        else:
            venv_logger.info("No external message definition folders specified in config.")

    except AttributeError as e:
        venv_logger.error(f"Failed to get typestore for ROS distro '{ros_distro}'. Check rosbags library support. Error: {e}", exc_info=True)
        raise
    except Exception as e:
        venv_logger.error(f"Unexpected error initializing typestore or loading external types: {e}", exc_info=True)
        raise

    extracted_data_by_topic: Dict[str, Dict[str, Any]] = {}
    msgtypes: Dict[str, str] = {}
    fields_by_topic: Dict[str, List[Tuple[str, str, bool]]] = {}
    unreadable_topics: Set[str] = set()

    start_time = time.time()
    try:
        bag_path = Path(folder_path)
        with AnyReader([bag_path], default_typestore=typestore) as reader:
            venv_logger.info(f"Opened bag: {folder_path}. Found {len(reader.connections)} connections.")
            total_messages_expected = reader.message_count
            venv_logger.info(f"Total messages in bag: {total_messages_expected}")

            for conn in reader.connections:
                topic = conn.topic
                msgtype = conn.msgtype

                if topic not in extracted_data_by_topic:
                    if msgtype not in typestore.types:
                        msgdef_in_bag = getattr(conn, 'msgdef', None)
                        if msgdef_in_bag:
                            venv_logger.info(f"Type '{msgtype}' for topic '{topic}' not in typestore. Trying to parse definition from bag.")
                            try:
                                parsed_types = get_types_from_msg(msgdef_in_bag, msgtype)
                                typestore.register(parsed_types)
                                venv_logger.info(f"Successfully registered type '{msgtype}' and dependencies from bag definition.")
                                if msgtype not in typestore.types:
                                    venv_logger.error(f"Registration of '{msgtype}' from bag definition failed unexpectedly.")
                                    unreadable_topics.add(topic)
                                    continue
                            except Exception as parse_reg_err:
                                venv_logger.error(f"Failed to parse/register definition for '{msgtype}' from bag: {parse_reg_err}", exc_info=True)
                                unreadable_topics.add(topic)
                                continue
                        else:
                            venv_logger.warning(f"Type '{msgtype}' for topic '{topic}' not found in typestore and no definition found in bag. Skipping topic.")
                            unreadable_topics.add(topic)
                            continue

                    if msgtype not in fields_by_topic:
                        venv_logger.debug(f"Determining fields for type '{msgtype}' (Topic: '{topic}')")
                        fields_by_topic[msgtype] = get_all_fields(msgtype, typestore)
                        if not fields_by_topic[msgtype]:
                            venv_logger.warning(f"Could not determine any fields for type '{msgtype}' (Topic: '{topic}'). Skipping topic.")
                            unreadable_topics.add(topic)
                            continue

                    topic_fields = fields_by_topic[msgtype]
                    extracted_data_by_topic[topic] = {
                        'timestamps': [],
                        'fields': topic_fields,
                        'data': {field[0]: [] for field in topic_fields}
                    }
                    msgtypes[topic] = msgtype
                    venv_logger.debug(f"Initialized data structure for topic '{topic}' (Type: {msgtype}, Fields: {[f[0] for f in topic_fields][:5]}...)")

                elif msgtypes.get(topic) != msgtype:
                    venv_logger.warning(f"Topic '{topic}' has inconsistent message types: '{msgtypes[topic]}' and '{msgtype}'. Sticking with the first type encountered.")
                    if msgtype not in typestore.types:
                        unreadable_topics.add(topic)

            venv_logger.info(f"Starting message iteration and data extraction for {len(extracted_data_by_topic)} processable topics...")
            processed_count = 0
            deserialization_errors = 0
            field_access_errors = 0
            log_interval = max(1000, total_messages_expected // 20) if total_messages_expected > 0 else 5000

            valid_connections = [c for c in reader.connections if c.topic in extracted_data_by_topic and c.topic not in unreadable_topics]
            if len(valid_connections) < len(reader.connections):
                venv_logger.warning(f"Processing messages from {len(valid_connections)} connections ({(len(reader.connections) - len(valid_connections))} excluded due to unknown types or errors).")

            for conn, timestamp_ns, rawdata in reader.messages(connections=valid_connections):
                topic = conn.topic
                msgtype = conn.msgtype

                try:
                    msg = deserialize_cdr(rawdata, msgtype)
                except Exception as deser_err:
                    venv_logger.debug(f"Deserialization failed for {msgtype} (Topic: {topic}) at ts {timestamp_ns}: {deser_err!r}")
                    deserialization_errors += 1
                    continue

                extracted_data_by_topic[topic]['timestamps'].append(timestamp_ns / 1e9)

                topic_fields = extracted_data_by_topic[topic]['fields']
                current_msg_data = {}

                def get_value_recursive(obj: Any, field_path_parts: List[str]):
                    value = obj
                    for i, part in enumerate(field_path_parts):
                        if value is None: return None
                        if isinstance(value, (list, tuple, np.ndarray)):
                            if i == len(field_path_parts) - 1:
                                return value
                            else:
                                venv_logger.debug(f"Cannot access attribute '{part}' on array/list at path {'_'.join(field_path_parts[:i])}")
                                return None
                        try:
                            value = getattr(value, part)
                        except AttributeError:
                            venv_logger.debug(f"Attribute '{part}' not found at path {'_'.join(field_path_parts[:i+1])}")
                            return None
                    if type(value).__name__ in ('Time', 'Duration') and hasattr(value, 'sec') and hasattr(value, 'nanosec'):
                        return value.sec + value.nanosec * 1e-9
                    return value

                for flat_field_name, _, _ in topic_fields:
                    try:
                        field_path_parts = flat_field_name.split('_')
                        value = get_value_recursive(msg, field_path_parts)
                        current_msg_data[flat_field_name] = value
                    except Exception as field_err:
                        venv_logger.debug(f"Error accessing field '{flat_field_name}' for topic '{topic}': {field_err}")
                        current_msg_data[flat_field_name] = None
                        field_access_errors += 1

                for flat_field_name, _, _ in topic_fields:
                    extracted_data_by_topic[topic]['data'][flat_field_name].append(current_msg_data.get(flat_field_name))

                processed_count += 1
                if processed_count % log_interval == 0:
                    elapsed_time = time.time() - start_time
                    venv_logger.info(f"Processed {processed_count}/{total_messages_expected} messages... ({elapsed_time:.2f}s)")

            venv_logger.info(f"Finished iterating messages. Processed {processed_count} messages total.")
            if deserialization_errors > 0:
                venv_logger.warning(f"Encountered {deserialization_errors} deserialization errors.")
            if field_access_errors > 0:
                venv_logger.warning(f"Encountered {field_access_errors} field access errors.")

    except FileNotFoundError as e:
        venv_logger.error(f"Bag folder not found or inaccessible during reading: {folder_path}: {e}")
        return None
    except ImportError as e:
        venv_logger.critical(f"ImportError during bag reading, required library (rosbags?) likely missing: {e}", exc_info=True)
        raise
    except Exception as e:
        venv_logger.error(f"Failed to read or process bag folder {folder_path}: {e}", exc_info=True)
        return None
    finally:
        pass

    final_data_to_return = {}
    for topic, data_dict in extracted_data_by_topic.items():
        if data_dict['timestamps']:
            data_dict['timestamps'] = np.array(data_dict['timestamps'], dtype=np.float64)
            final_data_to_return[topic] = data_dict
        else:
            venv_logger.warning(f"Topic '{topic}' had no messages successfully processed. Excluding from final output.")

    total_time = time.time() - start_time
    venv_logger.info(f"Finished extraction for {folder_path} in {total_time:.2f}s.")

    if not final_data_to_return:
        venv_logger.error(f"No data successfully extracted for any topic in {folder_path}.")
        return None

    return {
        'extracted_data': final_data_to_return,
        'input_folder_path': folder_path,
        'output_hdf5_path': output_hdf5_path,
        'msgtypes': msgtypes,
    }


def transform_and_load_single(extracted_info: Optional[Dict[str, Any]], config: Dict[str, Any]) -> Optional[Dict[str, str]]:
    import logging
    import numpy as np
    import sys
    import time
    import tables
    import os

    from preprocessing.ros_etl_utils import sanitize_hdf5_identifier, save_ros_topics_to_pytables

   
    venv_logger = logging.getLogger(f"{__name__}.transform_load_venv")

    if extracted_info is None:
        venv_logger.warning("Received no extracted info (likely due to upstream skip/error), skipping transform/load.")
        return None

    extracted_data_by_topic: Optional[Dict[str, Dict]] = extracted_info.get('extracted_data')
    output_hdf5_path: Optional[str] = extracted_info.get('output_hdf5_path')
    input_folder_path: Optional[str] = extracted_info.get('input_folder_path')
    timestamp_hdf5_name: str = config.get('timestamp_hdf5_name', 'timestamp_s')

    input_foldername = os.path.basename(input_folder_path) if input_folder_path else "Unknown Folder"

    if not extracted_data_by_topic or not output_hdf5_path or not input_folder_path:
        venv_logger.error(f"Missing required data or paths in extracted_info for {input_foldername}. Cannot proceed.")
        return {'input_foldername': input_foldername, 'output_path': output_hdf5_path, 'status': 'failed_input'}

    venv_logger.info(f"Preparing data for HDF5 writing: {output_hdf5_path} (from {input_foldername})")
    data_to_write: Dict[str, Dict[str, Any]] = {}
    preparation_start_time = time.time()
    topics_prepared = 0
    topics_failed_preparation = 0

    for topic_name, topic_data_dict in extracted_data_by_topic.items():
        topic_start_time = time.time()
        venv_logger.debug(f"Preparing topic: {topic_name}")

        timestamps: Optional[np.ndarray] = topic_data_dict.get('timestamps')
        field_definitions: Optional[List[Tuple[str, str, bool]]] = topic_data_dict.get('fields')
        data_by_field: Optional[Dict[str, List[Any]]] = topic_data_dict.get('data')

        if timestamps is None or field_definitions is None or data_by_field is None:
            venv_logger.warning(f"Skipping topic '{topic_name}' due to incomplete data structure (missing timestamps, fields, or data dict).")
            topics_failed_preparation += 1
            continue
        if not isinstance(timestamps, np.ndarray) or timestamps.ndim != 1:
            venv_logger.warning(f"Skipping topic '{topic_name}': Timestamps are not a 1D NumPy array (type: {type(timestamps)}).")
            topics_failed_preparation += 1
            continue
        if timestamps.size == 0:
            venv_logger.info(f"Skipping topic '{topic_name}': Contains zero messages.")
            continue

        num_rows = len(timestamps)
        venv_logger.debug(f"Topic '{topic_name}' has {num_rows} messages.")

        table_fields_pytables = {}
        structured_array_data_input = {}
        valid_fields_count = 0

        table_fields_pytables[timestamp_hdf5_name] = tables.Float64Col(pos=0)
        structured_array_data_input[timestamp_hdf5_name] = timestamps

        col_position = 1
        for flat_field_name, ros_type, is_array in field_definitions:
            col_name_hdf5 = sanitize_hdf5_identifier(flat_field_name)
            if col_name_hdf5 != flat_field_name:
                venv_logger.debug(f"Field name '{flat_field_name}' (Topic: {topic_name}) sanitized to '{col_name_hdf5}' for HDF5.")
            if col_name_hdf5 in table_fields_pytables:
                venv_logger.error(f"Sanitized column name collision for '{col_name_hdf5}' (from original '{flat_field_name}') in topic '{topic_name}'. Skipping field.")
                continue

            raw_data_list = data_by_field.get(flat_field_name)
            if raw_data_list is None:
                venv_logger.warning(f"Data missing for field '{flat_field_name}' in topic '{topic_name}', though it was defined. Skipping field.")
                continue
            if len(raw_data_list) != num_rows:
                venv_logger.error(f"Data list length mismatch for field '{flat_field_name}' ({len(raw_data_list)}) vs timestamps ({num_rows}) in topic '{topic_name}'. Skipping field.")
                continue

            col_type_pytables = None
            col_options = {'pos': col_position}
            final_data_for_col = None

            try:
                if is_array:
                    try:
                        object_array = np.array(raw_data_list, dtype=object)
                        first_elem = next((item for item in object_array.ravel() if item is not None), None)
                        if first_elem is None:
                            target_dtype = np.float64
                            shape = (1,)
                            final_data_for_col = np.full((num_rows,) + shape, np.nan, dtype=target_dtype)
                        elif isinstance(first_elem, (int, np.integer)): target_dtype = np.int64
                        elif isinstance(first_elem, (float, np.floating)): target_dtype = np.float64
                        elif isinstance(first_elem, (bool, np.bool_)): target_dtype = np.bool_
                        elif isinstance(first_elem, str): target_dtype = object
                        elif isinstance(first_elem, bytes): target_dtype = object
                        else:
                            venv_logger.warning(f"Field '{flat_field_name}' (Topic: {topic_name}) is an array of unsupported complex type '{type(first_elem)}'. Skipping field.")
                            continue

                        if target_dtype != object:
                            try:
                                converted_array = np.array([np.asarray(xi, dtype=target_dtype) if xi is not None else np.full(np.shape(first_elem), np.nan if target_dtype==np.float64 else 0) for xi in object_array])
                                if converted_array.ndim > 1:
                                    col_shape = converted_array.shape[1:]
                                    col_options['shape'] = col_shape
                                    final_data_for_col = converted_array
                                else:
                                    venv_logger.warning(f"Array field '{flat_field_name}' resulted in 1D array after conversion. Treating as scalar.")
                                    is_array = False
                                    final_data_for_col = converted_array
                            except Exception as array_conv_err:
                                venv_logger.warning(f"Could not consistently convert array field '{flat_field_name}' (Topic: {topic_name}) to type {target_dtype}. Skipping field. Error: {array_conv_err}")
                                continue
                        else:
                            max_len = 1
                            if isinstance(first_elem, str):
                                max_len = max((len(s) for row in object_array if row is not None for s in np.atleast_1d(row) if isinstance(s, str)), default=1)
                            elif isinstance(first_elem, bytes):
                                max_len = max((len(b) for row in object_array if row is not None for b in np.atleast_1d(row) if isinstance(b, bytes)), default=1)

                            col_type_pytables = tables.StringCol
                            col_options['itemsize'] = max_len
                            shape = np.shape(first_elem) if first_elem is not None else (1,)
                            col_options['shape'] = shape
                            encoded_array = np.empty((num_rows,) + shape, dtype=f'S{max_len}')
                            for i, row in enumerate(object_array):
                                if row is None:
                                    encoded_array[i] = np.full(shape, b'')
                                else:
                                    row_array = np.atleast_1d(row)
                                    encoded_row = np.array([str(s).encode('utf-8','replace')[:max_len] if isinstance(s, str) else s[:max_len] if isinstance(s, bytes) else b'' for s in row_array], dtype=f'S{max_len}')
                                    if encoded_row.shape == shape:
                                        encoded_array[i] = encoded_row
                                    else:
                                        venv_logger.warning(f"Shape mismatch in string/bytes array field '{flat_field_name}' at row {i}. Expected {shape}, got {encoded_row.shape}. Padding/truncating.")
                                        padded_encoded_row = np.full(shape, b'', dtype=f'S{max_len}')
                                        src_slice = tuple(slice(0, min(s1, s2)) for s1, s2 in zip(shape, encoded_row.shape))
                                        padded_encoded_row[src_slice] = encoded_row[src_slice]
                                        encoded_array[i] = padded_encoded_row
                            final_data_for_col = encoded_array
                    except Exception as array_prep_err:
                         venv_logger.warning(f"Error preparing array field '{flat_field_name}' (Topic: {topic_name}). Skipping. Error: {array_prep_err}")
                         continue


                if not is_array or final_data_for_col is not None:
                    if final_data_for_col is None:
                        try:
                            np_array = np.array(raw_data_list, dtype=object)
                            first_val = next((x for x in np_array if x is not None), None)

                            if first_val is None:
                                target_dtype = np.float64
                                final_data_for_col = np.full(num_rows, np.nan, dtype=target_dtype)
                            elif isinstance(first_val, str):
                                max_len = max((len(s) for s in np_array if isinstance(s, str)), default=1)
                                target_dtype = f'S{max_len}'
                                col_type_pytables = tables.StringCol
                                col_options['itemsize'] = max_len
                                final_data_for_col = np.array([s.encode('utf-8','replace')[:max_len] if isinstance(s, str) else b'' for s in np_array], dtype=target_dtype)
                            elif isinstance(first_val, bytes):
                                max_len = max((len(b) for b in np_array if isinstance(b, bytes)), default=1)
                                target_dtype = f'S{max_len}'
                                col_type_pytables = tables.StringCol
                                col_options['itemsize'] = max_len
                                final_data_for_col = np.array([b[:max_len] if isinstance(b, bytes) else b'' for b in np_array], dtype=target_dtype)
                            elif isinstance(first_val, bool):
                                target_dtype = np.bool_
                                final_data_for_col = np.array([x if isinstance(x, bool) else False for x in np_array], dtype=target_dtype)
                            elif isinstance(first_val, int):
                                target_dtype = np.int64
                                final_data_for_col = np.array([x if isinstance(x, int) else 0 for x in np_array], dtype=target_dtype)
                            elif isinstance(first_val, float):
                                target_dtype = np.float64
                                final_data_for_col = np.array([x if isinstance(x, (float, int)) else np.nan for x in np_array], dtype=target_dtype)
                            else:
                                venv_logger.warning(f"Field '{flat_field_name}' has object dtype with unsupported scalar element type '{type(first_val)}'. Skipping.")
                                continue
                        except Exception as scalar_conv_err:
                            venv_logger.error(f"Error converting scalar field '{flat_field_name}' (Topic: {topic_name}) to NumPy array: {scalar_conv_err}", exc_info=True)
                            continue

                    if col_type_pytables is None:
                        np_dtype_kind = final_data_for_col.dtype.kind
                        if np_dtype_kind == 'i': col_type_pytables = tables.Int64Col
                        elif np_dtype_kind == 'u': col_type_pytables = tables.UInt64Col
                        elif np_dtype_kind == 'f': col_type_pytables = tables.Float64Col
                        elif np_dtype_kind == 'b': col_type_pytables = tables.BoolCol
                        elif np_dtype_kind == 'S':
                            col_type_pytables = tables.StringCol
                            col_options['itemsize'] = final_data_for_col.dtype.itemsize
                        elif np_dtype_kind == 'O':
                            venv_logger.warning(f"Field '{flat_field_name}' remains object type. Attempting to save as StringCol.")
                            col_type_pytables = tables.StringCol
                            col_options['itemsize'] = 256
                            itemsize = col_options['itemsize']
                            final_data_for_col = np.array([str(s).encode('utf-8', 'replace')[:itemsize] if s is not None else b'' for s in final_data_for_col], dtype=f'S{itemsize}')


                if col_type_pytables and final_data_for_col is not None:
                    table_fields_pytables[col_name_hdf5] = col_type_pytables(**col_options)
                    structured_array_data_input[col_name_hdf5] = final_data_for_col
                    valid_fields_count += 1
                    col_position += 1
                elif final_data_for_col is None:
                    venv_logger.warning(f"Final data for field '{flat_field_name}' (Topic: {topic_name}) is None after processing. Skipping field.")
                else:
                    venv_logger.warning(f"Could not determine PyTables type for field '{flat_field_name}' (NumPy type: {final_data_for_col.dtype}). Skipping field.")

            except Exception as field_prep_err:
                venv_logger.error(f"Error preparing data or type for field '{flat_field_name}' (Topic: {topic_name}): {field_prep_err}", exc_info=True)
                continue

        if valid_fields_count == 0:
            venv_logger.warning(f"No valid data fields could be prepared for topic '{topic_name}'. Skipping table creation.")
            topics_failed_preparation += 1
            continue

        try:
            description_class_name = f"TopicDesc_{sanitize_hdf5_identifier(topic_name)}"
            TopicTableDescription = type(description_class_name, (tables.IsDescription,), table_fields_pytables)
            table_dtype = TopicTableDescription.columns

            structured_array = np.empty(num_rows, dtype=table_dtype)
            for col_name_hdf5 in table_dtype.names:
                if col_name_hdf5 in structured_array_data_input:
                    try:
                        structured_array[col_name_hdf5] = structured_array_data_input[col_name_hdf5]
                    except ValueError as assign_err:
                        venv_logger.error(f"ValueError assigning data for column '{col_name_hdf5}' (Topic: {topic_name}): {assign_err}. Check shapes and types.")
                        continue
                else:
                    venv_logger.warning(f"Column '{col_name_hdf5}' is in description but missing from prepared data for topic '{topic_name}'. Array will have default values.")

            hdf5_topic_path = '/' + '/'.join(sanitize_hdf5_identifier(part) for part in topic_name.strip('/').split('/') if part)
            if not hdf5_topic_path: hdf5_topic_path = '/untitled_topic'

            if hdf5_topic_path in data_to_write:
                venv_logger.error(f"HDF5 path collision for '{hdf5_topic_path}' (from Topic: '{topic_name}'). Skipping this topic.")
                topics_failed_preparation += 1
                continue

            data_to_write[hdf5_topic_path] = {
                'description': TopicTableDescription,
                'data': structured_array
                }
            topics_prepared += 1
            venv_logger.info(f"Successfully prepared topic '{topic_name}' ({num_rows} rows, {valid_fields_count + 1} cols) as HDF5 path '{hdf5_topic_path}' in {time.time() - topic_start_time:.2f}s")

        except tables.exceptions.HDF5ExtError as h5_err:
            venv_logger.error(f"PyTables error during description/array creation for topic {topic_name}: {h5_err}", exc_info=True)
            topics_failed_preparation += 1
        except Exception as e:
            venv_logger.error(f"Failed during final structured array or description creation for topic '{topic_name}': {e}", exc_info=True)
            topics_failed_preparation += 1
            continue

    preparation_time = time.time() - preparation_start_time
    venv_logger.info(f"Finished data preparation for {topics_prepared} topics in {preparation_time:.2f}s.")
    if topics_failed_preparation > 0:
        venv_logger.warning(f"Failed to prepare data for {topics_failed_preparation} topics.")

    if not data_to_write:
        venv_logger.error(f"No topics could be successfully prepared for writing for folder {input_foldername}.")
        return {'input_foldername': input_foldername, 'output_path': output_hdf5_path, 'status': 'failed_prepare'}

    venv_logger.info(f"Calling HDF5 writer function 'save_ros_topics_to_pytables' for {len(data_to_write)} tables...")
    write_success = False
    writer_start_time = time.time()
    try:
        write_success = save_ros_topics_to_pytables(output_hdf5_path, data_to_write)
        writer_time = time.time() - writer_start_time
        if write_success:
            venv_logger.info(f"HDF5 writer reported SUCCESS for {input_foldername} (took {writer_time:.2f}s)")
            return {'input_foldername': input_foldername, 'output_path': output_hdf5_path, 'status': 'success'}
        else:
            venv_logger.error(f"HDF5 writer function 'save_ros_topics_to_pytables' reported FAILURE for {input_foldername} (took {writer_time:.2f}s). Check writer logs.")
            return {'input_foldername': input_foldername, 'output_path': output_hdf5_path, 'status': 'failed_write'}
    except Exception as writer_e:
        writer_time = time.time() - writer_start_time
        venv_logger.critical(f"HDF5 writer function 'save_ros_topics_to_pytables' raised an unhandled exception after {writer_time:.2f}s for {input_foldername}: {writer_e}", exc_info=True)
        if os.path.exists(output_hdf5_path):
            try:
                os.remove(output_hdf5_path)
                venv_logger.info(f"Removed potentially corrupted HDF5 file due to writer exception: {output_hdf5_path}")
            except OSError as rm_err:
                venv_logger.error(f"Failed to remove corrupted HDF5 file {output_hdf5_path}: {rm_err}")
        return {'input_foldername': input_foldername, 'output_path': output_hdf5_path, 'status': 'failed_exception'}


def save_ros_topics_to_pytables(output_hdf5_path: str, data_by_hdf5_path: Dict[str, Dict[str, Any]]) -> bool:

    import tables
    import np

    writer_logger = logging.getLogger(f"{__name__}.save_pytables_data")
    writer_logger.info(f"Opening HDF5 file '{output_hdf5_path}' for writing {len(data_by_hdf5_path)} topics/tables.")

    output_dir = os.path.dirname(output_hdf5_path)
    try:
        os.makedirs(output_dir, exist_ok=True)
    except OSError as e:
        writer_logger.error(f"Failed to ensure output directory exists {output_dir}: {e}", exc_info=True)
        return False

    h5file = None
    topics_written = 0
    topics_failed = 0
    try:
        h5file = tables.open_file(output_hdf5_path, mode="w", title="Processed ROS Bag Data")
        filters = tables.Filters(complib='zlib', complevel=5)

        for hdf5_path, table_content in data_by_hdf5_path.items():
            description_class = table_content.get('description')
            structured_data = table_content.get('data')
            table_title = f"Data for {hdf5_path}"

            if description_class is None or structured_data is None:
                writer_logger.warning(f"Skipping HDF5 path '{hdf5_path}' due to missing description or data.")
                topics_failed += 1
                continue
            if not issubclass(description_class, tables.IsDescription):
                writer_logger.error(f"Invalid description type for HDF5 path '{hdf5_path}': {type(description_class)}. Expected subclass of tables.IsDescription. Skipping.")
                topics_failed += 1
                continue
            if not isinstance(structured_data, np.ndarray):
                writer_logger.error(f"Invalid data type for HDF5 path '{hdf5_path}': {type(structured_data)}. Expected numpy.ndarray. Skipping.")
                topics_failed += 1
                continue

            try:
                if not hdf5_path.startswith('/'): hdf5_path = '/' + hdf5_path

                parent_group_path, table_name = os.path.split(hdf5_path)
                if not table_name:
                    table_name = os.path.basename(parent_group_path)
                    parent_group_path = os.path.dirname(parent_group_path)

                if parent_group_path and parent_group_path != '/':
                    parent_node = h5file.create_group(h5file.root, parent_group_path, title=f"Group for {parent_group_path}", createparents=True)
                    writer_logger.debug(f"Ensured group exists: {parent_node._v_pathname}")
                else:
                    parent_node = h5file.root

                if hasattr(parent_node, table_name):
                    writer_logger.error(f"Node '{table_name}' already exists in group '{parent_node._v_pathname}'. Cannot create table for HDF5 path: {hdf5_path}. Skipping.")
                    topics_failed += 1
                    continue

                writer_logger.debug(f"Creating table '{table_name}' in group '{parent_node._v_pathname}' with {len(structured_data)} rows")
                data_table = h5file.create_table(
                    where=parent_node,
                    name=table_name,
                    description=description_class,
                    title=table_title,
                    filters=filters,
                    expectedrows=len(structured_data) if len(structured_data) > 0 else 1000
                )

                if len(structured_data) > 0:
                    data_table.append(structured_data)
                    data_table.flush()

                final_table_path = data_table._v_pathname
                writer_logger.debug(f"Successfully wrote {len(structured_data)} rows to table '{final_table_path}'")
                topics_written += 1

            except tables.exceptions.NodeError as ne:
                writer_logger.error(f"PyTables NodeError for HDF5 path '{hdf5_path}' (Table: '{table_name}'): {ne}. Check path validity and naming.", exc_info=True)
                topics_failed += 1
            except Exception as node_create_e:
                writer_logger.error(f"Failed during group/table creation or writing for HDF5 path '{hdf5_path}' (Table: '{table_name}'): {node_create_e}", exc_info=True)
                topics_failed += 1
                continue

        writer_logger.info(f"Finished writing loop. Attempted {len(data_by_hdf5_path)} tables, successfully wrote {topics_written}, failed {topics_failed} to {output_hdf5_path}")
        return topics_failed == 0

    except tables.exceptions.HDF5ExtError as hdf5_err:
        writer_logger.error(f"PyTables HDF5 Error accessing file {output_hdf5_path}: {hdf5_err}", exc_info=True)
    except OSError as os_err:
        writer_logger.error(f"OS Error during file operation for {output_hdf5_path}: {os_err}", exc_info=True)
    except Exception as e:
        writer_logger.error(f"Unexpected error during PyTables file write operation for {output_hdf5_path}: {e}", exc_info=True)

    if h5file is not None and h5file.isopen:
        h5file.close()
        h5file = None

    if os.path.exists(output_hdf5_path):
        writer_logger.warning(f"Attempting to remove potentially incomplete file: {output_hdf5_path} due to error during writing.")
        try:
            os.remove(output_hdf5_path)
            writer_logger.info(f"Removed failed/incomplete file: {output_hdf5_path}")
        except OSError as rm_err:
            writer_logger.error(f"Failed to remove partially created/failed file {output_hdf5_path}: {rm_err}")

    return False

def log_processed_folders(config: Dict[str, Any], processed_results: List[Optional[Dict[str, str]]], previously_transformed_folders: Set[str]) -> Set[str]:
    logger.info("Logging processed folder state...")
    successfully_processed_info = [
        item for item in processed_results
        if item is not None and isinstance(item, dict)
        and 'input_foldername' in item and item.get('status') == 'success'
    ]

    if not successfully_processed_info:
        logger.info("No new folders were successfully processed and loaded in this run.")
        return previously_transformed_folders

    pickle_path = os.path.join(config["output_folder"], "processed_rosbags_folders.pkl")
    newly_processed_foldernames = {info['input_foldername'] for info in successfully_processed_info}

    logger.info(f"Logging {len(newly_processed_foldernames)} newly processed folders.")
    logger.debug(f"Newly processed folders: {newly_processed_foldernames}")

    updated_folders_set = previously_transformed_folders.union(newly_processed_foldernames)

    try:
        os.makedirs(config["output_folder"], exist_ok=True)
        with open(pickle_path, 'wb') as f:
            pickle.dump(updated_folders_set, f)
        logger.info(f"Updated processed folders state log at {pickle_path}. Total count: {len(updated_folders_set)}")
    except Exception as e:
        logger.critical(f"CRITICAL: Failed to write state file {pickle_path}: {e}", exc_info=True)
        raise IOError(f"CRITICAL: Failed to write state to {pickle_path}") from e

    return updated_folders_set