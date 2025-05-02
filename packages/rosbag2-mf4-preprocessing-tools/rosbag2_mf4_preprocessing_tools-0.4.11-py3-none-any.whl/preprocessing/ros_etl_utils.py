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

def prepare_transform_arguments(
    config: Dict[str, Any],
    extracted_results: List[Optional[Dict[str, Any]]],
    
) -> List[Dict[str, Any]]: #
    """
    Prepares arguments for the transform_and_load_single task, filtering out failed extractions.
    NOTE: This version assumes the transform/load function no longer needs the writer function name passed dynamically.

    Args:
        config: The main configuration dictionary.
        extracted_results: A list of results from the mapped extract task (can contain None).

    Returns:
        List of dictionaries, each suitable for op_kwargs of the transform_and_load_single task.
    """
    prep_logger = logging.getLogger(__name__) 
    kwargs_list = [] 
    successful_extractions = 0 

    if extracted_results is None: 
        prep_logger.info("Received None as extraction result (upstream likely skipped all). No data to transform/load.") #
        return [] 

    if not isinstance(extracted_results, list): 
         prep_logger.warning(f"Received non-list extraction result: {type(extracted_results)}. Wrapping in list.") 
         extracted_results = [extracted_results] 


    for result in extracted_results: 
        if isinstance(result, dict) and "extracted_data" in result and result["extracted_data"]: 
            kwargs_list.append( 
                {
                    "extracted_info": result, 
                    "config": config,
                }
            )
            successful_extractions += 1 
        else: #
            input_path = "unknown" 
            if isinstance(result, dict): 
                input_path = result.get("input_subfolder_path", "unknown") 
            prep_logger.warning( 
                f"Skipping transform argument preparation for a None, empty, or invalid result from extraction. Input path (if known): {input_path}. Result: {result}" 
            )

    prep_logger.info( 
        f"Prepared {len(kwargs_list)} arguments for transform/load task " 
        f"(corresponding to {successful_extractions} successful extractions)." 
    )
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
    from rosbags.typesys import Stores, get_typestore, get_types_from_msg
    from preprocessing.ros_etl_utils import parse_external_msg_definitions, get_all_fields

    task_logger = logging.getLogger(__name__)
    task_logger.info(f"Starting ROS data extraction for subfolder: {subfolder_path}")
    output_folder = config['output_folder']
    ros_distro = config['ros_distro']
    custom_msg_definition_folders = config.get('custom_msg_definition_folders', [])

    subfolder_name = os.path.basename(subfolder_path)
    safe_subfolder_name = "".join(c if c.isalnum() or c in ('_', '-') else '_' for c in subfolder_name)
    output_hdf5_filename = safe_subfolder_name + ".h5"
    output_hdf5_path = os.path.join(output_folder, output_hdf5_filename)

    if not os.path.isdir(subfolder_path):
        task_logger.error(f"Input subfolder not found or not a directory: {subfolder_path}")
        return None

    try:
        typestore_enum = getattr(Stores, f"ROS2_{ros_distro.upper()}", None)
        if typestore_enum is None:
            task_logger.error(f"Invalid ROS distro '{ros_distro}' specified. Cannot find corresponding typestore.")
            task_logger.warning(f"Falling back to default ROS2_HUMBLE typestore.")
            typestore_enum = Stores.ROS2_HUMBLE

        typestore = get_typestore(typestore_enum)
        task_logger.info(f"Using base typestore: {typestore_enum.name}")

        if custom_msg_definition_folders:
            task_logger.info("Parsing external message definitions...")
            external_types_to_register = parse_external_msg_definitions(custom_msg_definition_folders, task_logger)

            if external_types_to_register:
                task_logger.info(f"Registering {len(external_types_to_register)} external types with the typestore...")
                try:
                    typestore.register(external_types_to_register)
                    task_logger.info("Registration of external types complete.")
                    problem_types_to_check = ['dae_msgs/msg/GNSS', 'marwis_msg/msg/Marwis'] # Example check
                    for ptype in problem_types_to_check:
                         if ptype in external_types_to_register:
                              task_logger.info(f"Post-external-registration check: Is '{ptype}' in typestore.types? {'YES' if ptype in typestore.types else 'NO - FAILED!'}")

                except Exception as reg_err:
                    task_logger.error(f"Failed during typestore.register call for external types: {reg_err}", exc_info=True)
                    raise RuntimeError("Failed to register required external message definitions.") from reg_err
            else:
                task_logger.info("No external types found or parsed from provided folders.")
        else:
            task_logger.info("No external message definition folders specified in config.")

    except AttributeError:
        task_logger.error(f"Failed to get typestore for ROS distro '{ros_distro}'. Check rosbags library support.")
        raise
    except Exception as e:
        task_logger.error(f"Unexpected error initializing typestore or loading external types: {e}", exc_info=True)
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
            task_logger.info(f"Opened bag: {subfolder_path}. Found {len(reader.connections)} connections.")

            types_missing_def_from_bag = set()
            types_parse_failed_from_bag = set()

            for conn in reader.connections:
                topic = conn.topic
                msgtype = conn.msgtype
                msgcount = conn.msgcount

                all_topics_in_bag.add(topic)

                if topic not in msgtypes:
                    msgtypes[topic] = msgtype
                    message_counts[topic] = msgcount
                    task_logger.debug(f"Topic '{topic}': Type='{msgtype}', Count={msgcount}")
                else:
                    if msgtypes[topic] != msgtype:
                         task_logger.warning(f"Topic '{topic}' has multiple message types: '{msgtypes[topic]}' and '{msgtype}'. Using first encountered ('{msgtypes[topic]}').")
                    message_counts[topic] += msgcount

                if '/' in conn.msgtype and conn.msgtype not in typestore.types and conn.msgtype not in newly_registered_types_from_bag:
                    msgdef_to_parse = getattr(conn, 'msgdef', '')
                    if not msgdef_to_parse and hasattr(conn, 'ext') and hasattr(conn.ext, 'rosbag2') and hasattr(conn.ext.rosbag2, 'msgdef'):
                         msgdef_to_parse = conn.ext.rosbag2.msgdef

                    if msgdef_to_parse:
                        task_logger.info(f"Found potential msgdef in bag for type '{conn.msgtype}' (Topic: '{conn.topic}'). Length: {len(msgdef_to_parse)}. Attempting parse.")
                        task_logger.debug(f"Msgdef preview for '{conn.msgtype}':\n{msgdef_to_parse[:500]}...")
                        try:
                            type_dict = get_types_from_msg(msgdef_to_parse, conn.msgtype)
                            new_types = {k: v for k, v in type_dict.items() if k not in typestore.types and k not in newly_registered_types_from_bag}
                            if new_types:
                                 task_logger.info(f"Parsed {len(new_types)} new type definitions from bag associated with '{conn.msgtype}': {list(new_types.keys())}")
                                 newly_registered_types_from_bag.update(new_types)
                            else:
                                 task_logger.debug(f"Types associated with '{conn.msgtype}' from bag seem already known.")
                        except SyntaxError as e:
                             task_logger.error(f"Syntax error parsing message definition from bag for type '{conn.msgtype}' (Topic: '{conn.topic}'): {e}")
                             types_parse_failed_from_bag.add(conn.msgtype)
                        except Exception as e:
                            task_logger.warning(f"Failed to parse/register message definition from bag for type '{conn.msgtype}' (Topic: '{conn.topic}'): {e}", exc_info=True)
                            types_parse_failed_from_bag.add(conn.msgtype)
                    else:
                        task_logger.warning(f"No msgdef found in bag connection info for potential custom type '{conn.msgtype}' (Topic: '{conn.topic}').")
                        types_missing_def_from_bag.add(conn.msgtype)

            task_logger.info(f"Found {len(newly_registered_types_from_bag)} unique new types definitions within the bag itself.")
            if types_missing_def_from_bag:
                 task_logger.warning(f"Could not find definitions in bag for types (may be expected if provided externally): {types_missing_def_from_bag}")
            if types_parse_failed_from_bag:
                 task_logger.error(f"Failed to parse definitions found within the bag for types: {types_parse_failed_from_bag}")

            if newly_registered_types_from_bag:
                task_logger.info(f"Registering {len(newly_registered_types_from_bag)} types found within the bag...")
                try:
                    typestore.register(newly_registered_types_from_bag)
                    task_logger.info("Registration of types from bag complete.")
                except Exception as e:
                    task_logger.error(f"Failed during typestore.register call for types from bag: {e}", exc_info=True)

            task_logger.info("Determining flattened fields for each topic...")
            for topic in sorted(list(all_topics_in_bag)):
                 msg_type_name = msgtypes.get(topic)
                 if msg_type_name:
                     if msg_type_name in typestore.types:
                         task_logger.debug(f"Getting fields for topic '{topic}' (type: {msg_type_name})")
                         all_fields_by_topic[topic] = get_all_fields(msg_type_name, typestore)
                         task_logger.debug(f"Found {len(all_fields_by_topic[topic])} fields for topic '{topic}': {all_fields_by_topic[topic][:10]}...")
                     else:
                         task_logger.warning(f"Message type '{msg_type_name}' for topic '{topic}' not found in the final typestore. Cannot determine fields or deserialize.")
                         all_fields_by_topic[topic] = []
                 else:
                     task_logger.warning(f"No message type found for topic '{topic}' in connection info.")
                     all_fields_by_topic[topic] = []

            extracted_data_by_topic: Dict[str, Dict[str, list]] = {}
            for topic, fields in all_fields_by_topic.items():
                 if fields:
                     extracted_data_by_topic[topic] = {'timestamps': [], 'data': {field: [] for field in fields}}
                 else:
                     task_logger.info(f"Skipping data structure initialization for topic '{topic}' as no fields were found/type was unknown.")

            task_logger.info("Starting message iteration and data extraction...")
            processed_count = 0
            total_messages_expected = sum(mc for mc in message_counts.values() if mc is not None) # Handle potential None counts
            log_interval = max(1000, total_messages_expected // 20) if total_messages_expected > 0 else 1000

            valid_connections = []
            task_logger.info("Filtering connections based on final typestore state...")
            connections_excluded_type = 0
            connections_excluded_fields = 0
            known_unknown_types = types_missing_def_from_bag.union(types_parse_failed_from_bag)
            for conn in reader.connections:
                 type_known = conn.msgtype in typestore.types
                 topic_processable = conn.topic in all_fields_by_topic and bool(all_fields_by_topic[conn.topic])

                 if type_known and topic_processable:
                      valid_connections.append(conn)
                 elif not type_known:
                     if conn.msgtype not in known_unknown_types:
                          task_logger.warning(f"Excluding connection for topic '{conn.topic}': Type '{conn.msgtype}' is NOT known to the final typestore (reason unclear).")
                          known_unknown_types.add(conn.msgtype)
                     connections_excluded_type += 1
                 elif not topic_processable:
                     task_logger.warning(f"Excluding connection for topic '{conn.topic}': Type '{conn.msgtype}' is known, but no processable fields were found/determined.")
                     connections_excluded_fields += 1

            task_logger.info(f"Processing messages from {len(valid_connections)} valid connections.")
            task_logger.info(f"Excluded {connections_excluded_type} connections due to unknown types.")
            task_logger.info(f"Excluded {connections_excluded_fields} connections due to missing fields/processability.")

            if not valid_connections:
                 task_logger.warning(f"No valid connections found for processing in bag {subfolder_path}. No data will be extracted.")

            for conn, timestamp, rawdata in reader.messages(connections=valid_connections):
                topic = conn.topic
                if topic in extracted_data_by_topic:
                    try:
                        msg = typestore.deserialize_cdr(rawdata, conn.msgtype)
                    except KeyError as deser_err:
                        task_logger.warning(f"Deserialization KeyError for {conn.msgtype} (Topic: {topic}) at ts {timestamp}. Error: {deser_err!r}", exc_info=False)
                        continue
                    except ValueError as deser_err:
                        task_logger.warning(f"Deserialization ValueError for {conn.msgtype} (Topic: {topic}) at ts {timestamp}. Error: {deser_err!r}", exc_info=False)
                        continue
                    except Exception as deser_err:
                        task_logger.warning(f"Generic Deserialization failed for {conn.msgtype} (Topic: {topic}) at ts {timestamp}: {deser_err!r}", exc_info=False) # Reduce noise
                        continue

                    extracted_data_by_topic[topic]['timestamps'].append(timestamp / 1e9)
                    current_msg_flat_data = {}

                    def flatten_msg_data(msg_obj, prefix='', target_dict=None):
                         if target_dict is None: target_dict = {}
                         if msg_obj is None: return target_dict
                         if isinstance(msg_obj, (int, float, bool, str)): return target_dict
                         if isinstance(msg_obj, np.ndarray): pass

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
                                      else: pass

                                  if isinstance(field_value, (list, tuple)) or (hasattr(field_value, '__slots__') or (isinstance(field_value, object) and not isinstance(field_value, (int, float, bool, str, np.ndarray)))):
                                       needs_recursion = any(f.startswith(flat_field_name + '_') for f in extracted_data_by_topic[topic]['data'])
                                       if needs_recursion:
                                            if isinstance(field_value, (list, tuple)):
                                                 # task_logger.debug(f"Field '{flat_field_name}' is an array/list of complex types. Skipping detailed content.")
                                                 pass # Skip recursion into lists/tuples of complex types for now
                                            else:
                                                 flatten_msg_data(field_value, prefix=f"{flat_field_name}_", target_dict=target_dict)
                              except AttributeError:
                                  task_logger.debug(f"AttributeError getting field '{field_name}' from message of type {type(msg_obj).__name__}")
                              except Exception as getattr_err:
                                  task_logger.debug(f"Could not getattr '{field_name}' for topic '{topic}': {getattr_err}")
                         return target_dict

                    current_msg_flat_data = flatten_msg_data(msg)

                    expected_fields = extracted_data_by_topic[topic]['data'].keys()
                    for field_key in expected_fields:
                         value_to_append = current_msg_flat_data.get(field_key, None)
                         extracted_data_by_topic[topic]['data'][field_key].append(value_to_append)

                    processed_count += 1
                    if processed_count % log_interval == 0:
                         elapsed_time = time.time() - start_time
                         task_logger.info(f"Processed {processed_count}/{total_messages_expected} messages... ({elapsed_time:.2f}s)")

            task_logger.info(f"Finished iterating messages. Processed {processed_count} messages total.")

    except FileNotFoundError as e:
        task_logger.error(f"Bag folder not found during reading: {subfolder_path}: {e}")
        return None
    except ImportError as e:
        task_logger.error(f"ImportError during bag reading, potentially missing dependency: {e}", exc_info=True)
        return None
    except Exception as e:
        task_logger.error(f"Failed to read or process bag folder {subfolder_path}: {e}", exc_info=True)
        return None

    task_logger.info("Converting extracted data to NumPy arrays...")
    final_extracted_data = {}
    conversion_errors = 0
    empty_topics = 0

    for topic, data_dict in extracted_data_by_topic.items():
        timestamps_list = data_dict.get('timestamps', [])
        if not timestamps_list:
            task_logger.warning(f"No timestamps (and likely no data) extracted for topic: {topic}. Skipping.")
            empty_topics += 1
            continue

        ts_count = len(timestamps_list)
        final_topic_data = {}
        field_errors = 0

        for field, values_list in data_dict['data'].items():
            if len(values_list) != ts_count:
                 task_logger.warning(f"Correcting length mismatch for field '{field}' topic '{topic}'. Expected {ts_count}, got {len(values_list)}. Padding with None.")
                 values_list.extend([None] * (ts_count - len(values_list)))

            try:
                 np_array = np.array(values_list, dtype=object)
                 final_topic_data[field] = np_array
            except Exception as np_err:
                 task_logger.error(f"Failed to create NumPy array for field '{field}' topic '{topic}'. Skipping field. Error: {np_err}")
                 field_errors += 1
                 continue

        if field_errors > 0:
            task_logger.warning(f"Encountered {field_errors} errors converting fields to NumPy arrays for topic '{topic}'.")
            conversion_errors += field_errors

        if not final_topic_data:
            task_logger.warning(f"No data fields could be converted to NumPy for topic: {topic}. Skipping topic.")
            empty_topics += 1
            continue

        try:
             final_extracted_data[topic] = {
                 'timestamps': np.array(timestamps_list, dtype=np.float64),
                 'data': final_topic_data
             }
        except Exception as ts_np_err:
            task_logger.error(f"Failed to create NumPy array for timestamps of topic '{topic}': {ts_np_err}. Skipping topic.")
            empty_topics +=1
            if topic in final_extracted_data: del final_extracted_data[topic]
            continue

    total_time = time.time() - start_time
    task_logger.info(f"Finished extraction and NumPy conversion for {subfolder_path} in {total_time:.2f}s.")
    if conversion_errors > 0:
        task_logger.warning(f"Total NumPy conversion errors across all topics: {conversion_errors}")
    if empty_topics > 0:
        task_logger.warning(f"Total topics skipped due to no data or conversion errors: {empty_topics}")

    if not final_extracted_data:
        task_logger.error(f"No data successfully extracted for any topic in {subfolder_path}.")
        return None

    return {
        'extracted_data': final_extracted_data,
        'input_subfolder_path': subfolder_path,
        'output_hdf5_path': output_hdf5_path,
        'msgtypes': msgtypes,
    }

def _transform_load_ros_data_logic(
    extracted_info: Optional[Dict[str, Any]],
    writer_func_module: str,
    writer_func_name: str
) -> Optional[Dict[str, str]]:
    import logging 
    import os 
    import time 
    import numpy as np 
    import tables 
    from pathlib import Path
    from preprocessing.ros_etl_utils import save_ros_topics_to_pytables 

    task_logger = logging.getLogger(__name__)

    if extracted_info is None:
        task_logger.warning("Received no extracted info (likely due to upstream skip/error), skipping transform/load.")
        return None

    try:
        module = importlib.import_module(writer_func_module)
        writer_func = getattr(module, writer_func_name)
        task_logger.info(f"Successfully imported writer function '{writer_func_name}' from module '{writer_func_module}'.")
    except (ImportError, AttributeError, ModuleNotFoundError) as e:
        task_logger.critical(f"Failed to import writer function {writer_func_name} from {writer_func_module}: {e}", exc_info=True)
        raise RuntimeError(f"Could not load HDF5 writer function: {writer_func_module}.{writer_func_name}") from e

    input_subfolder_path = extracted_info['input_subfolder_path']
    output_hdf5_path = extracted_info['output_hdf5_path']
    extracted_data = extracted_info.get('extracted_data', {})

    if not extracted_data:
        task_logger.warning(f"No data dictionary found in extracted info for subfolder {input_subfolder_path}. Skipping HDF5 writing.")
        return None

    task_logger.info(f"Preparing data for HDF5 writing: {output_hdf5_path} (from {input_subfolder_path})")
    data_to_write: Dict[str, Dict[str, Any]] = {}
    preparation_start_time = time.time()

    for topic, topic_data in extracted_data.items():
        topic_start_time = time.time()
        task_logger.debug(f"Preparing topic: {topic}")

        timestamps = topic_data.get('timestamps')
        data_fields = topic_data.get('data', {})

        if timestamps is None or not isinstance(timestamps, np.ndarray) or timestamps.size == 0:
            task_logger.warning(f"Skipping topic '{topic}' due to missing, invalid, or empty timestamps.")
            continue
        if not data_fields:
             task_logger.warning(f"Skipping topic '{topic}' due to empty data fields dictionary.")
             continue

        num_rows = len(timestamps)
        if num_rows == 0:
            task_logger.warning(f"Skipping topic '{topic}' due to zero rows (empty timestamps array).")
            continue

        dtype_list = [('timestamp_s', np.float64)]
        structured_array_data_input = {'timestamp_s': timestamps.astype(np.float64)}
        valid_fields_count = 0

        for col_name, data_array in data_fields.items():
            if not isinstance(data_array, np.ndarray):
                task_logger.warning(f"Data for field '{col_name}' in topic '{topic}' is not a NumPy array (type: {type(data_array)}). Skipping field.")
                continue
            if len(data_array) != num_rows:
                task_logger.error(f"Data array length mismatch for field '{col_name}' ({len(data_array)}) vs timestamps ({num_rows}) in topic '{topic}'. Skipping field.")
                continue

            sanitized_col_name = sanitize_hdf5_identifier(col_name)
            if sanitized_col_name != col_name:
                task_logger.warning(f"Field name '{col_name}' (Topic: {topic}) sanitized to '{sanitized_col_name}' for HDF5 table.")
            if sanitized_col_name in structured_array_data_input:
                task_logger.error(f"Sanitized column name collision for '{sanitized_col_name}' (from original '{col_name}') in topic '{topic}'. Skipping field.")
                continue

            target_np_dtype = None
            current_shape = ()

            if data_array.dtype == 'O':
                 first_elem = next((item for item in data_array if item is not None), None)
                 if isinstance(first_elem, np.ndarray) or isinstance(first_elem, (list, tuple)):
                      task_logger.warning(f"Field '{col_name}' (Topic: {topic}) contains array-like objects. Skipping field for direct table storage.")
                      continue

            try:
                if data_array.dtype == 'O':
                    first_val = next((x for x in data_array if x is not None), None)
                    if first_val is None:
                         target_np_dtype = np.float64
                         final_data_for_col = np.full(num_rows, np.nan, dtype=target_np_dtype)
                    elif isinstance(first_val, str):
                         max_len = max((len(s) for s in data_array if isinstance(s, str)), default=1)
                         target_np_dtype = f'S{int(max_len)}'
                         final_data_for_col = np.array([s.encode('utf-8','replace')[:int(max_len)] if isinstance(s, str) else b'' for s in data_array], dtype=target_np_dtype)
                    elif isinstance(first_val, bytes):
                         max_len = max((len(b) for b in data_array if isinstance(b, bytes)), default=1)
                         target_np_dtype = f'S{int(max_len)}'
                         final_data_for_col = np.array([b[:int(max_len)] if isinstance(b, bytes) else b'' for b in data_array], dtype=target_np_dtype)
                    elif isinstance(first_val, bool):
                         target_np_dtype = np.bool_
                         final_data_for_col = np.array([x if isinstance(x, bool) else False for x in data_array], dtype=target_np_dtype)
                    elif isinstance(first_val, int):
                         target_np_dtype = np.int64
                         final_data_for_col = np.array([x if isinstance(x, int) else 0 for x in data_array], dtype=target_np_dtype)
                    elif isinstance(first_val, float):
                         target_np_dtype = np.float64
                         final_data_for_col = np.array([x if isinstance(x, float) else np.nan for x in data_array], dtype=target_np_dtype)
                    else:
                         task_logger.warning(f"Field '{col_name}' has object dtype with unsupported element type '{type(first_val)}'. Skipping.")
                         continue
                else:
                    target_np_dtype = data_array.dtype
                    final_data_for_col = data_array
                    if data_array.ndim > 1:
                         current_shape = data_array.shape[1:]

                if target_np_dtype is not None and final_data_for_col is not None:
                    dtype_spec = (target_np_dtype, current_shape) if current_shape else target_np_dtype
                    dtype_list.append((sanitized_col_name, dtype_spec))
                    structured_array_data_input[sanitized_col_name] = final_data_for_col
                    valid_fields_count += 1
                else:
                     task_logger.warning(f"Could not determine target type or prepare data for field '{col_name}'. Skipping.")
                     continue

            except Exception as prep_err:
                 task_logger.error(f"Error preparing data for field '{col_name}' (Topic: {topic}): {prep_err}", exc_info=True)
                 continue

        if valid_fields_count == 0:
            task_logger.warning(f"No valid data fields could be prepared for topic '{topic}'. Skipping table creation.")
            continue

        try:
            final_dtype_list = [item for item in dtype_list if item[0] in structured_array_data_input]
            if len(final_dtype_list) <= 1:
                 task_logger.warning(f"Only timestamp field (or fewer) remains for topic '{topic}'. Skipping table creation.")
                 continue

            final_dtype_np = np.dtype(final_dtype_list)
            description_object, byteorder = tables.descr_from_dtype(final_dtype_np)
            task_logger.debug(f"Generated final PyTables description for topic '{topic}' with {len(final_dtype_np.names)} columns.")

            structured_array = np.empty(num_rows, dtype=description_object._v_dtype.descr)
            for col_name_sanitized in description_object._v_dtype.names:
                 structured_array[col_name_sanitized] = structured_array_data_input[col_name_sanitized]

            sanitized_topic_for_path = topic.strip('/').replace('/', '_')
            path_parts = [sanitize_hdf5_identifier(part) for part in sanitized_topic_for_path.split('_') if part]
            table_path = '/' + '/'.join(path_parts) if path_parts else '/unknown_topic'

            if table_path != '/' + sanitized_topic_for_path:
                task_logger.warning(f"Topic path '{topic}' sanitized to HDF5 path '{table_path}'.")

            data_to_write[table_path] = {
                'description': description_object,
                'data': structured_array
                }
            task_logger.info(f"Successfully prepared topic '{topic}' ({num_rows} rows, {len(final_dtype_np.names)} cols) as HDF5 path '{table_path}' in {time.time() - topic_start_time:.2f}s")

        except Warning as w:
             task_logger.warning(f"PyTables Warning during description/array creation for topic {topic}: {w}")
        except NotImplementedError as nie:
             task_logger.error(f"PyTables does not support the generated structure for topic '{topic}': {nie}", exc_info=True)
        except Exception as e:
            task_logger.error(f"Failed during final structured array or description creation for topic '{topic}': {e}", exc_info=True)
            continue

    preparation_time = time.time() - preparation_start_time
    task_logger.info(f"Finished data preparation for {len(data_to_write)} topics in {preparation_time:.2f}s.")

    if not data_to_write:
        task_logger.error(f"No topics could be successfully prepared for writing for subfolder {input_subfolder_path}.")
        return None

    task_logger.info(f"Calling HDF5 writer function '{writer_func_name}' for {len(data_to_write)} tables...")
    write_success = False
    writer_start_time = time.time()
    try:
        write_success = writer_func(output_hdf5_path, data_to_write)
        writer_time = time.time() - writer_start_time
        if write_success:
            task_logger.info(f"HDF5 writer reported SUCCESS for {input_subfolder_path} (took {writer_time:.2f}s)")
            return {'input_subfolder_path': input_subfolder_path, 'status': 'success'}
        else:
            task_logger.error(f"HDF5 writer function '{writer_func_name}' reported FAILURE for {input_subfolder_path} (took {writer_time:.2f}s). Check writer logs.")
            return {'input_subfolder_path': input_subfolder_path, 'status': 'failed_write'}
    except Exception as writer_e:
        writer_time = time.time() - writer_start_time
        task_logger.critical(f"HDF5 writer function '{writer_func_name}' raised an unhandled exception after {writer_time:.2f}s for {input_subfolder_path}: {writer_e}", exc_info=True)
        return {'input_subfolder_path': input_subfolder_path, 'status': 'failed_exception'}

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
