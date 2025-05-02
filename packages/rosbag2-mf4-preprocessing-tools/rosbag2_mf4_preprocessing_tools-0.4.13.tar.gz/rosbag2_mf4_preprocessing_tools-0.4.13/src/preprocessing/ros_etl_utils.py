import os
import logging
import time
import pickle
import re
import keyword
import gc # Garbage Collector import
from datetime import datetime
from pathlib import Path
from collections import defaultdict

import numpy as np
import tables # PyTables

# Airflow imports
from airflow import DAG
from airflow.models.param import Param
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonVirtualenvOperator, PythonOperator

# Typing imports (for functions running in main Airflow env)
from typing import Dict, List, Optional, Any, Set, Tuple, Callable

# --- Constants ---
PYTHON_VENV_REQUIREMENTS = [
    "rosbag2-mf4-preprocessing-tools==0.4.12", # Or your specific version
    "rosbags",
    "numpy",
    "tables", # Ensure PyTables is included
    "pyyaml", # Dependency often needed
]

DEFAULT_BASE_INPUT_FOLDER = "/mnt/sambashare/ugglf/measurement_data/input/"
DEFAULT_OUTPUT_FOLDER = "/mnt/sambashare/ugglf/measurement_data/output/"
DEFAULT_ROS_DISTRO = 'humble'
DEFAULT_CUSTOM_MSG_DEFS = [
    "/opt/airflow/dags/custom_ros2_msgs/custom_msgs",
]
# Removed SAVE_PYTABLES constants

# --- Logging Setup ---
# Keep your existing logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# dag_logger = logging.getLogger(__name__) # Use __name__ within functions for task-specific logging

# =============================================================================
# Utility Functions (Should reside in ros_etl_utils.py or similar)
# =============================================================================

def sanitize_hdf5_identifier(name: str) -> str:
    # Keep your existing sanitize_hdf5_identifier function
    sanitized = re.sub(r'\W|^(?=\d)', '_', name)
    if keyword.iskeyword(sanitized):
        sanitized += '_'
    if not sanitized or sanitized == '_': # Ensure it's not empty or just '_'
         # Try to derive something from original name if possible
        base_name = re.sub(r'^[^a-zA-Z_]+', '', name) # Remove leading non-alpha chars
        base_name = re.sub(r'\W', '_', base_name)
        if base_name and not keyword.iskeyword(base_name):
             sanitized = base_name
        else:
             sanitized = 'field_' + hex(hash(name) & 0xffffffff)[2:] # Fallback to hash
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', sanitized): # Final check for validity
        sanitized = 'field_' + hex(hash(name) & 0xffffffff)[2:]
    return sanitized

def get_all_fields(typename: str, typestore: Any, current_prefix: str = '', visited: Optional[Set[str]] = None) -> List[str]:
    # Keep your existing get_all_fields function
    # Ensure 'rosbags.typesys.Stores' and Any are imported if needed at top level
    from rosbags.typesys import Stores # Example if needed here
    task_logger = logging.getLogger(__name__)
    if visited is None: visited = set()
    if typename in visited: return []
    visited.add(typename)
    fields_list = []
    try:
        if typename not in typestore.types:
            task_logger.warning(f"Type '{typename}' not found in typestore during field recursion.")
            return []
        type_definition = typestore.get_msgdef(typename)
        # Check if it's a primitive type disguised as a complex one sometimes
        if not hasattr(type_definition, 'fields'):
             # task_logger.debug(f"Type '{typename}' has no fields attribute, likely primitive or empty.")
            return []
        fields_definition = type_definition.fields
    except KeyError:
        task_logger.warning(f"Type '{typename}' not found in typestore during field recursion (KeyError).")
        return []
    except AttributeError:
         task_logger.warning(f"Type '{typename}' definition lacks 'fields' attribute.")
         return []
    except Exception as e:
        task_logger.error(f"Unexpected error getting fields for {typename}: {e}")
        return []

    for field_tuple in fields_definition:
        # field_tuple structure can vary slightly, robust access needed
        if not isinstance(field_tuple, (list, tuple)) or len(field_tuple) < 2:
             task_logger.warning(f"Unexpected field definition format in {typename}: {field_tuple}")
             continue

        field_name = field_tuple[0]
        field_type_info = field_tuple[1] # This contains type details

        # Extract the actual type name (can be nested)
        field_type_name = None
        is_array = False
        element_type_name = None

        if isinstance(field_type_info, (list, tuple)) and len(field_type_info) > 0:
            # Common structure: [kind, [type_name, length_if_array]] or similar
            kind = field_type_info[0] # e.g., 'primitive', 'nested', 'array'
            details = field_type_info[1] if len(field_type_info) > 1 else None

            if isinstance(details, (list, tuple)) and len(details) > 0:
                 potential_name = details[0]
                 if isinstance(potential_name, str):
                      field_type_name = potential_name
                      element_type_name = potential_name # Assume initially
                 elif hasattr(potential_name, 'name'): # Handle Type objects
                      field_type_name = potential_name.name
                      element_type_name = potential_name.name


                 if kind == 'array':
                      is_array = True
                      # If it's an array, the element type might be nested further
                      if hasattr(potential_name, 'basetype') and hasattr(potential_name.basetype, 'name'):
                           element_type_name = potential_name.basetype.name
                      elif isinstance(potential_name, str): # Array of primitives
                           element_type_name = potential_name
                      else: # Fallback if structure is unexpected
                           element_type_name = field_type_name


            elif isinstance(details, str): # Simple primitive case
                 field_type_name = details
                 element_type_name = details

        if not field_type_name:
             task_logger.warning(f"Could not determine type name for field '{field_name}' in {typename}")
             continue # Skip if we can't figure out the type

        flat_name = f"{current_prefix}{field_name}"

        # Check if the *element* type is a complex type we need to recurse into
        # We don't recurse into arrays themselves, but into their base element type if complex
        is_element_complex = False
        if element_type_name and element_type_name in typestore.types:
             try:
                 element_msgdef = typestore.get_msgdef(element_type_name)
                 if hasattr(element_msgdef, 'fields') and element_msgdef.fields:
                      is_element_complex = True
             except Exception: # Handle cases where get_msgdef might fail
                  pass

        if is_element_complex and not is_array: # Recurse only for non-array complex types
            nested_fields = get_all_fields(
                element_type_name,
                typestore,
                current_prefix=f"{flat_name}_",
                visited=visited.copy()
            )
            if nested_fields:
                fields_list.extend(nested_fields)
            else: # If recursion yields nothing, add the parent field itself? No, usually handled below.
                 pass # Avoid adding the container field if nested fields are expected but empty
        else:
            # Add primitive fields, array fields (as a whole), or complex fields that weren't recursed
            fields_list.append(flat_name)

    return fields_list

def parse_external_msg_definitions(definition_folders: List[str], logger: logging.Logger) -> Dict[str, Any]:
    # Keep your existing parse_external_msg_definitions function
    # Ensure 'rosbags.typesys.get_types_from_msg' is imported if needed
    from rosbags.typesys import get_types_from_msg
    all_external_types = {}
    files_processed = 0; parse_errors = 0
    if not definition_folders: return {}
    logger.info(f"Scanning for .msg files in: {definition_folders}")
    for folder_path_str in definition_folders:
        base_path = Path(folder_path_str)
        if not base_path.is_dir(): continue
        logger.info(f"Searching for .msg files recursively in {base_path}...")
        msg_files = list(base_path.rglob('*.msg'))
        logger.info(f"Found {len(msg_files)} .msg files in {base_path}.")
        for msg_file_path in msg_files:
            files_processed += 1
            try:
                relative_path = msg_file_path.relative_to(base_path)
                type_name_parts = list(relative_path.parts[:-1]); type_name_parts.append(relative_path.stem)
                # Basic validation of path structure for ROS types
                if len(type_name_parts) < 2: # Need at least package/MsgName
                     logger.warning(f"Skipping type name generation for unexpected path: {msg_file_path}")
                     continue
                # Construct type name (e.g., package_name/msg/MessageName -> package_name/MessageName)
                if len(type_name_parts) >= 3 and type_name_parts[-2] in ('msg', 'srv', 'action'):
                     ros_type_name = f"{type_name_parts[0]}/{type_name_parts[-1]}" # Assuming package/msg/Type -> package/Type
                elif len(type_name_parts) == 2: # package/MessageName.msg
                     ros_type_name = f"{type_name_parts[0]}/{type_name_parts[1]}"
                else:
                     # Fallback or stricter check needed? Assume last two parts for now.
                     ros_type_name = f"{'/'.join(type_name_parts)}" # Less reliable
                     logger.debug(f"Using fallback type name generation for {msg_file_path}: {ros_type_name}")

                content = msg_file_path.read_text()
                parsed_types = get_types_from_msg(content, ros_type_name)
                for name, definition in parsed_types.items():
                    if name in all_external_types: logger.warning(f"Duplicate definition for type '{name}' from {msg_file_path}.")
                    all_external_types[name] = definition
            except ValueError as e: logger.error(f"Error parsing {msg_file_path} (ValueError): {e}"); parse_errors += 1
            except OSError as e: logger.error(f"Error reading file {msg_file_path}: {e}"); parse_errors += 1
            except Exception as e: logger.error(f"Unexpected error processing {msg_file_path}: {e}"); parse_errors += 1
    logger.info(f"Finished scanning. Processed {files_processed} files. Collected {len(all_external_types)} types.")
    if parse_errors > 0: logger.error(f"Encountered {parse_errors} errors during parsing.")
    return all_external_types

# --- Functions below run in main Airflow Environment ---

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
    task_logger.info(f"Configuration: {config}")
    return config

def _create_output_directory_logic(config: Dict[str, Any]) -> Dict[str, Any]:
    task_logger = logging.getLogger(__name__)
    output_f = config['output_folder']
    task_logger.info(f"Ensuring output directory exists: {output_f}")
    try:
        os.makedirs(output_f, exist_ok=True)
        # Also ensure the temp extraction dir exists (or is created later)
        temp_extraction_folder = os.path.join(output_f, "_temp_extraction")
        os.makedirs(temp_extraction_folder, exist_ok=True)
    except OSError as e:
        task_logger.error(f"Failed to create output/temp directory {output_f}: {e}", exc_info=True)
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
                processed_subfolders = {item for item in loaded_data if isinstance(item, str) and item}
                task_logger.info(f"Loaded {len(processed_subfolders)} processed paths from {state_file}")
            else:
                 task_logger.warning(f"State file {state_file} invalid format. Re-initializing.")
        except Exception as e:
            task_logger.warning(f"Error loading state file {state_file}: {e}. Re-initializing.")
            try: os.remove(state_file)
            except OSError: pass
    else:
        task_logger.info(f"State file {state_file} not found. Starting fresh.")
    return config, processed_subfolders

def _find_unprocessed_subfolders_logic(config_processed_tuple: Tuple[Dict[str, Any], Set[str]]) -> List[str]:
    task_logger = logging.getLogger(__name__)
    config, already_processed_subfolders = config_processed_tuple
    base_input_folder = config["base_input_folder"]
    unprocessed_subfolders_list = []
    task_logger.info(f"Scanning {base_input_folder} for ROS 2 subfolders...")
    try:
        if not os.path.isdir(base_input_folder):
            raise FileNotFoundError(f"Base input directory not found: {base_input_folder}")
        all_items = os.listdir(base_input_folder)
        potential_subfolders = [os.path.join(base_input_folder, item) for item in all_items if os.path.isdir(os.path.join(base_input_folder, item))]
        ros2_bag_folders = [folder for folder in potential_subfolders if os.path.exists(os.path.join(folder, "metadata.yaml"))]
        all_folders_set = set(ros2_bag_folders)
        unprocessed_subfolders_set = all_folders_set - already_processed_subfolders
        unprocessed_subfolders_list = sorted(list(unprocessed_subfolders_set))
        task_logger.info(f"Found {len(all_folders_set)} total bags, {len(already_processed_subfolders)} processed, {len(unprocessed_subfolders_list)} new.")
    except Exception as e:
        task_logger.error(f"Error scanning for subfolders in {base_input_folder}: {e}", exc_info=True)
        raise
    return unprocessed_subfolders_list

def prepare_extract_arguments(config: Dict[str, Any], unprocessed_subfolders: List[str]) -> List[Dict[str, Any]]:
    prep_logger = logging.getLogger(__name__)
    if not unprocessed_subfolders: return []
    kwargs_list = [{"config": config, "subfolder_path": subfolder} for subfolder in unprocessed_subfolders]
    prep_logger.info(f"Prepared {len(kwargs_list)} arguments for extraction.")
    return kwargs_list

def _log_processed_subfolders_logic(
    processed_results: List[Optional[Dict[str, str]]], # Now expects results from extract_task
    config: Dict[str, Any],
    previously_processed_subfolders: List[str] # Received as list from XCom
) -> None:
    task_logger = logging.getLogger(__name__)
    task_logger.info("Logging processed subfolder state.")
    try:
        previously_processed_set = set(previously_processed_subfolders)
    except TypeError:
        task_logger.error("Could not convert previously_processed_subfolders to set. Starting fresh.")
        previously_processed_set = set()

    # Filter results based on the output format of the NEW _extract_ros_data_logic
    successfully_processed_info_this_run = [
        item for item in processed_results
        if isinstance(item, dict) and 'input_subfolder_path' in item and item.get('status') == 'success'
    ]

    if not successfully_processed_info_this_run:
        task_logger.info("No new subfolders successfully processed in this run. State file not updated.")
        return

    newly_processed_subfolder_paths = {info['input_subfolder_path'] for info in successfully_processed_info_this_run}
    task_logger.info(f"Identified {len(newly_processed_subfolder_paths)} newly processed subfolders.")

    updated_folders_set = previously_processed_set.union(newly_processed_subfolder_paths)
    state_file = os.path.join(config['output_folder'], "processed_ros2_subfolders.pkl")
    task_logger.info(f"Writing updated state to {state_file}. Total processed: {len(updated_folders_set)}")
    try:
        os.makedirs(config['output_folder'], exist_ok=True)
        with open(state_file, 'wb') as f:
            pickle.dump(updated_folders_set, f, protocol=pickle.HIGHEST_PROTOCOL)
        task_logger.info(f"Successfully updated state log: {state_file}")
    except Exception as e:
        task_logger.critical(f"CRITICAL: Failed to write state file {state_file}: {e}", exc_info=True)
        raise IOError(f"Failed to write state file: {state_file}") from e


def _extract_and_write_hdf5_chunked_logic(config: Dict[str, Any], subfolder_path: str) -> Dict[str, str]:
    import os
    import logging
    import time
    import gc
    from pathlib import Path
    from collections import defaultdict
    import numpy as np
    import tables # PyTables
    from rosbags.highlevel import AnyReader
    from rosbags.typesys import Stores, get_typestore, get_types_from_msg, TypesysError
    from typing import Dict, List, Optional, Any, Set, Tuple, Union
    from preprocessing.ros_etl_utils import parse_external_msg_definitions, get_all_fields, sanitize_hdf5_identifier


    task_logger = logging.getLogger(__name__)
    task_logger.info(f"Starting chunked HDF5 extraction for: {subfolder_path}")

    output_folder = config['output_folder']
    ros_distro = config['ros_distro']
    custom_msg_definition_folders = config.get('custom_msg_definition_folders', [])
    chunk_size = config.get('chunk_size', 1000)
    prescan_limit = config.get('prescan_limit', 50)
    task_logger.info(f"Using chunk size: {chunk_size}, prescan limit: {prescan_limit}")


    subfolder_name = os.path.basename(subfolder_path)
    safe_subfolder_name = "".join(c if c.isalnum() or c in ('_', '-') else '_' for c in subfolder_name)
    output_hdf5_filename = safe_subfolder_name + ".h5"
    output_hdf5_path = os.path.join(output_folder, output_hdf5_filename)

    if not os.path.isdir(subfolder_path):
        task_logger.error(f"Input subfolder not found: {subfolder_path}")
        return {'input_subfolder_path': subfolder_path, 'status': 'failed_input_not_found'}

    # --- Typestore Initialization & Custom Types ---
    typestore = None
    try:
        typestore_enum = getattr(Stores, f"ROS2_{ros_distro.upper()}", Stores.ROS2_HUMBLE)
        typestore = get_typestore(typestore_enum)
        if custom_msg_definition_folders:
            external_types = parse_external_msg_definitions(custom_msg_definition_folders, task_logger)
            if external_types: typestore.register(external_types)
    except Exception as e:
        task_logger.error(f"Typestore initialization failed: {e}", exc_info=True)
        return {'input_subfolder_path': subfolder_path, 'status': 'failed_typestore_init'}

    # --- Bag Reading and Initial Scan ---
    h5file = None # HDF5 file handle
    reader = None # Rosbag reader handle
    all_topics_in_bag: Set[str] = set()
    msgtypes: Dict[str, str] = {}
    topic_connections: Dict[str, Any] = {} # Store connection info per topic
    message_counts: Dict[str, int] = {} # Store message counts per topic
    all_fields_by_topic: Dict[str, List[str]] = {}
    pytables_description_by_topic: Dict[str, tables.Description] = {}
    hdf5_table_refs: Dict[str, tables.Table] = {} # Map topic to HDF5 table object
    processed_topics: Set[str] = set() # Topics successfully prepared

    try:
        path = Path(subfolder_path)
        reader = AnyReader([path], default_typestore=typestore)
        task_logger.info(f"Opened bag: {subfolder_path}. Connections: {len(reader.connections)}.")

        # --- Identify topics, types, message counts, and get flattened fields ---
        types_parse_failed_from_bag = set()
        for conn in reader.connections:
            topic = conn.topic; msgtype = conn.msgtype
            all_topics_in_bag.add(topic)
            if topic not in topic_connections: # Store first connection encountered for topic
                topic_connections[topic] = conn
                msgtypes[topic] = msgtype
                message_counts[topic] = conn.msgcount if conn.msgcount is not None else 0
            elif msgtypes[topic] != msgtype:
                 task_logger.warning(f"Multiple types for topic '{topic}'. Using first: '{msgtypes[topic]}'.")
                 # Add message counts even if types differ? Assuming yes for expectedrows.
                 if conn.msgcount is not None:
                      message_counts[topic] = (message_counts.get(topic, 0) or 0) + conn.msgcount


            # Attempt to register types found within the bag (best effort)
            if '/' in conn.msgtype and conn.msgtype not in typestore.types:
                 msgdef_to_parse = getattr(conn, 'msgdef', '') # Simplified fetch
                 if msgdef_to_parse:
                     try: typestore.register(get_types_from_msg(msgdef_to_parse, conn.msgtype))
                     except Exception: types_parse_failed_from_bag.add(conn.msgtype)

        if types_parse_failed_from_bag: task_logger.error(f"Failed parsing defs from bag: {types_parse_failed_from_bag}")

        for topic in sorted(list(all_topics_in_bag)):
            msg_type_name = msgtypes.get(topic)
            if msg_type_name and msg_type_name in typestore.types:
                 all_fields_by_topic[topic] = get_all_fields(msg_type_name, typestore)
            else:
                 all_fields_by_topic[topic] = []
                 task_logger.warning(f"Cannot process topic '{topic}': Type '{msg_type_name}' unknown or no fields found.")

        # --- Pre-scan for Type Inference & HDF5 Table Creation ---
        task_logger.info("Pre-scanning messages to infer types for HDF5 tables...")
        h5file = tables.open_file(output_hdf5_path, mode="w", title=f"ROS Bag Data: {safe_subfolder_name}")
        filters = tables.Filters(complib='zlib', complevel=5)

        for topic, fields in all_fields_by_topic.items():
            if not fields: continue # Skip topics we can't process

            conn = topic_connections.get(topic)
            if not conn: continue # Should have connection if fields were found

            task_logger.debug(f"Inferring types for topic: {topic}")
            sample_data = defaultdict(list)
            messages_scanned = 0
            try:
                # Limit connections to the current topic for pre-scan efficiency
                for _, timestamp, rawdata in reader.messages(connections=[conn]):
                    if messages_scanned >= prescan_limit: break
                    try:
                        msg = typestore.deserialize_cdr(rawdata, conn.msgtype)
                        # --- Flatten message data (using same logic as before) ---
                        flat_data = {}
                        # Define nested flatten function (or call utility if refactored)
                        def flatten_prescan(msg_obj, prefix='', target_dict=None):
                            if target_dict is None: target_dict = {}
                            if msg_obj is None: return target_dict
                            if isinstance(msg_obj, (int, float, bool, str, np.ndarray)): return target_dict
                            fields_to_check = getattr(msg_obj, '__slots__', [])
                            if not fields_to_check: fields_to_check = [a for a in dir(msg_obj) if not a.startswith('_') and not callable(getattr(msg_obj,a))]
                            for field_name in fields_to_check:
                                flat_field_name = f"{prefix}{field_name}"
                                if flat_field_name in fields: # Only process expected fields
                                    try:
                                        field_value = getattr(msg_obj, field_name)
                                        if isinstance(field_value, (int, float, bool, str, np.ndarray)): target_dict[flat_field_name] = field_value
                                        elif type(field_value).__name__ in ('Time', 'Duration'): target_dict[flat_field_name] = field_value.sec + field_value.nanosec * 1e-9
                                        else: # Complex type, potentially recurse
                                             is_complex = hasattr(field_value, '__slots__') or (isinstance(field_value, object) and not isinstance(field_value, (int,float,bool,str,np.ndarray)))
                                             needs_recurse = any(f.startswith(flat_field_name + '_') for f in fields)
                                             if is_complex and needs_recurse and not isinstance(field_value, (list, tuple)):
                                                  flatten_prescan(field_value, prefix=f"{flat_field_name}_", target_dict=target_dict)
                                    except AttributeError: pass
                                    except Exception: pass
                            return target_dict
                        flat_data = flatten_prescan(msg)

                        for field_key in fields:
                            sample_data[field_key].append(flat_data.get(field_key, None))
                        messages_scanned += 1
                    except Exception: continue # Ignore deserialization errors during scan
            except Exception as e:
                 task_logger.warning(f"Error during pre-scan for topic {topic}: {e}")
                 continue # Skip topic if pre-scan fails

            if not sample_data:
                 task_logger.warning(f"No valid sample data obtained for topic {topic}. Skipping.")
                 continue

            # --- Infer PyTables Description from Sample Data ---
            dtype_list = [('timestamp_s', tables.Float64Col())] # Timestamp always first
            valid_fields_count = 0
            max_str_lens = defaultdict(int)
            shapes = {}

            for field_key in fields:
                values = sample_data.get(field_key, [])
                sanitized_col_name = sanitize_hdf5_identifier(field_key)
                # Check for name collisions after sanitization
                if any(sanitized_col_name == existing_name for existing_name, _ in dtype_list):
                     task_logger.warning(f"Sanitized column name collision for '{field_key}' -> '{sanitized_col_name}' in topic {topic}. Skipping field.")
                     continue

                if not values: # No data for this field in sample
                     task_logger.warning(f"No sample data for field '{field_key}' (Topic: {topic}). Assuming Float64.")
                     dtype_list.append((sanitized_col_name, tables.Float64Col()))
                     valid_fields_count += 1
                     continue

                # Infer type from first non-None value
                first_val = next((v for v in values if v is not None), None)
                col_type = None
                shape = ()

                if first_val is None: col_type = tables.Float64Col() # Default if all None
                elif isinstance(first_val, bool): col_type = tables.BoolCol()
                elif isinstance(first_val, int): col_type = tables.Int64Col()
                elif isinstance(first_val, float): col_type = tables.Float64Col()
                elif isinstance(first_val, str):
                    max_len = max((len(s) for s in values if isinstance(s, str)), default=1)
                    col_type = tables.StringCol(itemsize=max_len, dflt=b'') # Use itemsize
                elif isinstance(first_val, bytes):
                     max_len = max((len(b) for b in values if isinstance(b, bytes)), default=1)
                     col_type = tables.StringCol(itemsize=max_len, dflt=b'') # Use StringCol for bytes too
                elif isinstance(first_val, np.ndarray):
                     # Handle array types - use shape and base dtype
                     try:
                         base_dtype = first_val.dtype
                         shape = first_val.shape
                         # Basic check for consistent shapes (more robust checks possible)
                         if any(getattr(v,'shape',None) != shape for v in values if v is not None):
                              task_logger.warning(f"Inconsistent array shapes for field '{field_key}' (Topic: {topic}). Skipping.")
                              continue
                         # Convert numpy dtype to PyTables Col
                         col_type = tables.Col.from_dtype(np.dtype((base_dtype, shape)))
                     except Exception as arr_e:
                          task_logger.warning(f"Cannot handle array field '{field_key}' (Topic: {topic}): {arr_e}. Skipping.")
                          continue # Skip complex/unsupported array types
                else:
                     task_logger.warning(f"Unsupported type '{type(first_val)}' for field '{field_key}' (Topic: {topic}). Skipping.")
                     continue # Skip unsupported types

                if col_type:
                     dtype_list.append((sanitized_col_name, col_type))
                     valid_fields_count += 1

            if valid_fields_count == 0:
                 task_logger.warning(f"No valid fields determined for topic {topic} after pre-scan. Skipping.")
                 continue

            # --- Create HDF5 Group and Table ---
            try:
                table_desc_dict = dict(dtype_list)
                # Final check for duplicate names (should be caught above, but safety)
                if len(table_desc_dict) != len(dtype_list):
                     task_logger.error(f"Duplicate sanitized column names detected for topic {topic} just before table creation. Skipping.")
                     continue

                Hdf5TableDescription = type('Hdf5TableDescription', (tables.IsDescription,), table_desc_dict)

                # Create groups based on topic path
                topic_path_parts = [sanitize_hdf5_identifier(part) for part in topic.strip('/').split('/') if part]
                parent_node = h5file.root
                for part in topic_path_parts[:-1]: # Create parent groups
                    group_path = f"{parent_node._v_pathname}/{part}" if parent_node._v_pathname != '/' else f"/{part}"
                    if not h5file.__contains__(group_path):
                         parent_node = h5file.create_group(parent_node, part, f"Group {part}")
                    else:
                         parent_node = h5file.get_node(group_path)
                         if not isinstance(parent_node, tables.Group): raise TypeError(f"Path conflict: {group_path} is not a Group.")


                table_name = topic_path_parts[-1] if topic_path_parts else sanitize_hdf5_identifier(topic) # Use last part as name
                if not table_name: table_name = "topic_data" # Fallback name

                table_pathname = f"{parent_node._v_pathname}/{table_name}" if parent_node._v_pathname != '/' else f"/{table_name}"
                if h5file.__contains__(table_pathname):
                     task_logger.error(f"Table '{table_name}' already exists in group '{parent_node._v_pathname}'. Skipping topic {topic}.")
                     continue

                data_table = h5file.create_table(parent_node, table_name, Hdf5TableDescription,
                                                 title=f"Data for topic {topic}", filters=filters,
                                                 expectedrows=(message_counts.get(topic, 0) or 10000)) # Use message count estimate

                hdf5_table_refs[topic] = data_table
                pytables_description_by_topic[topic] = Hdf5TableDescription # Store description class
                processed_topics.add(topic)
                task_logger.info(f"Created HDF5 table for topic {topic} at {data_table._v_pathname}")

            except Exception as table_create_e:
                 task_logger.error(f"Failed to create HDF5 table for topic {topic}: {table_create_e}", exc_info=True)
                 continue # Skip this topic

        # --- Main Message Processing Loop (Chunked) ---
        task_logger.info(f"Starting main chunked processing for {len(processed_topics)} topics...")
        batch_data_by_topic = defaultdict(lambda: defaultdict(list)) # topic -> field -> list_of_values
        messages_in_chunk = 0
        total_messages_processed = 0
        skipped_message_count = 0
        start_proc_time = time.time()

        # Get connections only for topics we successfully prepared
        valid_connections = [c for t, c in topic_connections.items() if t in processed_topics]

        for conn, timestamp, rawdata in reader.messages(connections=valid_connections):
            topic = conn.topic
            if topic not in processed_topics: continue # Should not happen with filtered connections, but safety check

            # *** ADDED try...except for individual message processing ***
            try:
                msg = typestore.deserialize_cdr(rawdata, conn.msgtype)
                # --- Flatten message data (using same logic as before) ---
                flat_data = {}
                # Define nested flatten function (or call utility)
                def flatten_chunk(msg_obj, prefix='', target_dict=None):
                    # (Same flatten_msg_data internal logic as before)
                    if target_dict is None: target_dict = {}
                    if msg_obj is None: return target_dict
                    if isinstance(msg_obj, (int, float, bool, str, np.ndarray)): return target_dict
                    fields_to_check = getattr(msg_obj, '__slots__', [])
                    if not fields_to_check: fields_to_check = [a for a in dir(msg_obj) if not a.startswith('_') and not callable(getattr(msg_obj,a))]
                    current_topic_fields = all_fields_by_topic[topic] # Access fields for current topic
                    for field_name in fields_to_check:
                        flat_field_name = f"{prefix}{field_name}"
                        if flat_field_name in current_topic_fields: # Only process expected fields
                            try:
                                field_value = getattr(msg_obj, field_name)
                                if isinstance(field_value, (int, float, bool, str, np.ndarray)): target_dict[flat_field_name] = field_value
                                elif type(field_value).__name__ in ('Time', 'Duration'): target_dict[flat_field_name] = field_value.sec + field_value.nanosec * 1e-9
                                else: # Complex type, potentially recurse
                                     is_complex = hasattr(field_value, '__slots__') or (isinstance(field_value, object) and not isinstance(field_value, (int,float,bool,str,np.ndarray)))
                                     needs_recurse = any(f.startswith(flat_field_name + '_') for f in current_topic_fields)
                                     if is_complex and needs_recurse and not isinstance(field_value, (list, tuple)):
                                          flatten_chunk(field_value, prefix=f"{flat_field_name}_", target_dict=target_dict)
                            except AttributeError: pass
                            except Exception: pass # Ignore errors getting specific fields during flatten
                    return target_dict
                flat_data = flatten_chunk(msg)

                # Append data to batch
                batch_data_by_topic[topic]['timestamp_s'].append(timestamp / 1e9)
                for field_key in all_fields_by_topic[topic]:
                    sanitized_col_name = sanitize_hdf5_identifier(field_key)
                    batch_data_by_topic[topic][sanitized_col_name].append(flat_data.get(field_key, None))

                messages_in_chunk += 1
                total_messages_processed += 1

            # *** ADDED except block for message processing ***
            except Exception as msg_proc_err:
                skipped_message_count += 1
                task_logger.warning(f"Skipping message for topic '{topic}' at timestamp {timestamp} due to processing error: {msg_proc_err}", exc_info=False) # Log error briefly
                # Continue to the next message
                continue

            # --- Write Chunk if Size Reached ---
            if messages_in_chunk >= chunk_size:
                # task_logger.debug(f"Writing chunk, {total_messages_processed} messages processed...") # Reduce noise
                write_start = time.time()
                for write_topic, topic_batch_data in batch_data_by_topic.items():
                    if not topic_batch_data.get('timestamp_s'): continue # Check specifically for timestamps

                    table_ref = hdf5_table_refs.get(write_topic)
                    table_desc = pytables_description_by_topic.get(write_topic)
                    if not table_ref or not table_desc: continue # Should not happen

                    num_rows_in_batch = len(topic_batch_data['timestamp_s'])
                    if num_rows_in_batch == 0: continue # Extra check

                    try:
                        # Create structured array for the batch
                        structured_array = np.empty(num_rows_in_batch, dtype=table_desc.columns)
                        for col_name in table_desc.columns.keys():
                            data_list = topic_batch_data.get(col_name, [])
                            # Ensure list length matches timestamp count, pad if necessary
                            if len(data_list) < num_rows_in_batch:
                                 pad_value = table_desc.columns[col_name].dflt if hasattr(table_desc.columns[col_name], 'dflt') else None
                                 data_list.extend([pad_value] * (num_rows_in_batch - len(data_list)))
                            elif len(data_list) > num_rows_in_batch:
                                 data_list = data_list[:num_rows_in_batch] # Truncate (shouldn't happen)

                            try:
                                 # Attempt direct assignment first
                                 structured_array[col_name] = data_list
                            except (ValueError, TypeError) as assign_err: # Catch specific common errors
                                 # task_logger.warning(f"Assign error col '{col_name}' (Topic: {write_topic}): {assign_err}. Trying conversion.") # Reduce noise
                                 # Fallback: Convert list to array with specific dtype first
                                 try:
                                      col_info = table_desc.columns[col_name]
                                      target_dtype = col_info.dtype
                                      target_shape = col_info.shape
                                      # Use np.dtype for combined shape/type if needed
                                      np_target_dtype = np.dtype((target_dtype, target_shape)) if target_shape != () else np.dtype(target_dtype)

                                      converted_array = np.array(data_list, dtype=object) # Start as object
                                      # Fill Nones based on target type
                                      if np.issubdtype(np_target_dtype, np.floating):
                                           converted_array[converted_array == None] = np.nan
                                      elif np.issubdtype(np_target_dtype, np.integer):
                                           converted_array[converted_array == None] = 0 # Or appropriate default
                                      elif np.issubdtype(np_target_dtype, np.bool_):
                                           converted_array[converted_array == None] = False
                                      # String/bytes handled by StringCol default usually

                                      # Handle potential shape mismatches for array columns
                                      if target_shape != ():
                                           # Ensure all elements can be reshaped or handle errors
                                           # This part can be complex depending on data variability
                                           try:
                                                # Attempt to stack if elements are arrays/lists
                                                if all(isinstance(x, (np.ndarray, list, tuple)) for x in converted_array if x is not None):
                                                     # Pad inner lists/arrays if needed before stacking
                                                     # For now, assume they match target_shape or fail
                                                     stacked_array = np.stack(converted_array)
                                                     if stacked_array.shape[1:] != target_shape:
                                                          raise ValueError(f"Shape mismatch: Expected {target_shape}, got {stacked_array.shape[1:]}")
                                                     structured_array[col_name] = stacked_array.astype(np_target_dtype.base) # Assign base type
                                                else: # Mix of types or non-array elements
                                                     raise ValueError("Cannot reliably stack non-array elements for array column")
                                           except Exception as stack_err:
                                                task_logger.error(f"Failed conversion for array column '{col_name}' (Topic: {write_topic}): {stack_err}. Filling default.", exc_info=False)
                                                structured_array[col_name] = col_info.dflt # Fill default on error
                                      else: # Scalar column
                                          structured_array[col_name] = converted_array.astype(np_target_dtype)

                                 except Exception as convert_err:
                                      task_logger.error(f"CRITICAL: Failed final conversion for column '{col_name}' (Topic: {write_topic}): {convert_err}. Filling default.", exc_info=False)
                                      structured_array[col_name] = table_desc.columns[col_name].dflt # Fill default

                        table_ref.append(structured_array)
                    except Exception as append_err:
                         task_logger.error(f"Failed to prepare/append chunk for topic {write_topic}: {append_err}", exc_info=True)
                         # Decide how to handle: skip chunk? fail task? For now, log and continue.

                # Clear batch data and reset counter
                batch_data_by_topic.clear() # Re-init defaultdict
                messages_in_chunk = 0
                h5file.flush() # Flush after writing chunk
                gc.collect() # Encourage memory cleanup
                # task_logger.debug(f"Chunk written in {time.time() - write_start:.2f}s") # Reduce noise


        # --- Process Final Partial Chunk ---
        task_logger.info(f"Processing final chunk ({messages_in_chunk} messages)...")
        if messages_in_chunk > 0:
            for write_topic, topic_batch_data in batch_data_by_topic.items():
                if not topic_batch_data.get('timestamp_s'): continue
                table_ref = hdf5_table_refs.get(write_topic)
                table_desc = pytables_description_by_topic.get(write_topic)
                if not table_ref or not table_desc: continue
                num_rows_in_batch = len(topic_batch_data['timestamp_s'])
                if num_rows_in_batch == 0: continue
                try:
                    structured_array = np.empty(num_rows_in_batch, dtype=table_desc.columns)
                    for col_name in table_desc.columns.keys():
                        data_list = topic_batch_data.get(col_name, [])
                        if len(data_list) < num_rows_in_batch:
                             pad_value = table_desc.columns[col_name].dflt if hasattr(table_desc.columns[col_name], 'dflt') else None
                             data_list.extend([pad_value] * (num_rows_in_batch - len(data_list)))
                        elif len(data_list) > num_rows_in_batch: data_list = data_list[:num_rows_in_batch]
                        try:
                             structured_array[col_name] = data_list
                        except (ValueError, TypeError): # Fallback conversion as above
                             try:
                                  col_info = table_desc.columns[col_name]
                                  target_dtype = col_info.dtype; target_shape = col_info.shape
                                  np_target_dtype = np.dtype((target_dtype, target_shape)) if target_shape != () else np.dtype(target_dtype)
                                  converted_array = np.array(data_list, dtype=object)
                                  if np.issubdtype(np_target_dtype, np.floating): converted_array[converted_array == None] = np.nan
                                  elif np.issubdtype(np_target_dtype, np.integer): converted_array[converted_array == None] = 0
                                  elif np.issubdtype(np_target_dtype, np.bool_): converted_array[converted_array == None] = False

                                  if target_shape != ():
                                       try:
                                            stacked_array = np.stack(converted_array)
                                            if stacked_array.shape[1:] != target_shape: raise ValueError("Shape mismatch")
                                            structured_array[col_name] = stacked_array.astype(np_target_dtype.base)
                                       except Exception as stack_err:
                                            task_logger.error(f"Failed conversion (final chunk) for array column '{col_name}' (Topic: {write_topic}): {stack_err}. Filling default.", exc_info=False)
                                            structured_array[col_name] = col_info.dflt
                                  else:
                                       structured_array[col_name] = converted_array.astype(np_target_dtype)
                             except Exception as convert_err:
                                  task_logger.error(f"CRITICAL: Failed final conversion (final chunk) for column '{col_name}' (Topic: {write_topic}): {convert_err}. Filling default.", exc_info=False)
                                  structured_array[col_name] = table_desc.columns[col_name].dflt

                    table_ref.append(structured_array)
                except Exception as append_err:
                     task_logger.error(f"Failed to prepare/append final chunk for topic {write_topic}: {append_err}", exc_info=True)
            h5file.flush()

        task_logger.info(f"Finished processing {total_messages_processed} messages ({skipped_message_count} skipped) in {time.time() - start_proc_time:.2f}s.")
        return {'input_subfolder_path': subfolder_path, 'status': 'success', 'output_hdf5_path': output_hdf5_path}

    except Exception as e:
        task_logger.error(f"Unhandled exception during extraction for {subfolder_path}: {e}", exc_info=True)
        # Attempt to remove potentially incomplete HDF5 file
        if h5file is not None and h5file.isopen: h5file.close() # Close if open
        if os.path.exists(output_hdf5_path):
             task_logger.warning(f"Attempting to remove incomplete HDF5 file: {output_hdf5_path}")
             try: os.remove(output_hdf5_path)
             except OSError as rm_err: task_logger.error(f"Failed to remove incomplete HDF5: {rm_err}")
        return {'input_subfolder_path': subfolder_path, 'status': 'failed_exception'}
    finally:
        # Ensure resources are closed
        if reader:
             try: reader.close()
             except Exception as close_err: task_logger.warning(f"Error closing bag reader: {close_err}")
        if h5file and h5file.isopen:
             try: h5file.close()
             except Exception as close_err: task_logger.warning(f"Error closing HDF5 file: {close_err}")
        gc.collect()


