import os
import pickle
import logging
from typing import Dict, List, Optional, Any, Set, Type

import numpy as np


# Configure basic logging for use within the virtualenv tasks
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

#can be used file and folder based
def get_config(**context) -> Dict[str, Any]:
    params = context['params']
    config = {
        'input_folder': params['input_folder'],
        'output_folder': params['output_folder'],
        'file_pattern': params['file_pattern'],
        'channel_mapper': params["channel_mapper"],
    }
    logger.info(f"Configuration: Input={config['input_folder']}, Output={config['output_folder']}, "
                     f"Pattern={config['file_pattern']}")
    return config

def create_directories(config: Dict[str, Any]) -> Dict[str, Any]:
    input_f = config['input_folder']
    output_f = config['output_folder']
    try:
        os.makedirs(input_f, exist_ok=True)
        os.makedirs(output_f, exist_ok=True)
    except OSError as e:
        logger.error(f"Failed to create directories: {e}", exc_info=True)
        raise
    return config

def load_already_transformed_files(config: Dict[str, Any]) -> Set[str]:
    pickle_path = os.path.join(config["input_folder"], "processed_files.pkl")
    already_transformed_files: Set[str] = set()
    if os.path.exists(pickle_path):
        try:
            with open(pickle_path, 'rb') as f:
                loaded_data = pickle.load(f)
                if isinstance(loaded_data, set):
                    already_transformed_files = loaded_data
                    logger.info(f"Loaded {len(already_transformed_files)} processed file names from {pickle_path}")
                else:
                    logger.warning(f"State file {pickle_path} did not contain a set. Ignoring.")
        except (pickle.UnpicklingError, EOFError, TypeError, Exception) as e:
            logger.warning(f"Error loading state file {pickle_path}: {e}. Assuming empty state.")
            try:
                os.remove(pickle_path)
                logger.info(f"Removed potentially corrupted state file: {pickle_path}")
            except OSError as rm_err:
                logger.error(f"Could not remove corrupted state file {pickle_path}: {rm_err}")
    else:
        logger.info(f"State file {pickle_path} not found. Assuming no files processed previously.")
    return already_transformed_files

def prepare_extract_arguments(config: Dict[str, Any], untransformed_files: List[str]) -> List[Dict[str, Any]]:
    """
    Prepares a list of op_kwargs dictionaries for extract task expansion.
    Called by a PythonOperator before the mapped extract task.
    """
    logger.info(f"Preparing extract arguments for {len(untransformed_files)} files.")
    kwargs_list = []
    for file_name in untransformed_files:
        kwargs_list.append({
            "config": config,
            "file_name": file_name
        })
    return kwargs_list

def prepare_transform_arguments(config: Dict[str, Any], extracted_results: List[Optional[Dict[str, Any]]], transform_load_func_name: str) -> List[Dict[str, Any]]:
    """
    Prepares a list of op_kwargs dictionaries for transform_and_load task expansion.
    Called by a PythonOperator after the mapped extract task.
    Filters out None results from failed extract tasks.
    """
    logger.info(f"Preparing transform arguments based on {len(extracted_results)} results from extraction.")
    kwargs_list = []
    successful_extractions = 0
    for result in extracted_results:
        if result is not None and isinstance(result, dict):
            kwargs_list.append({
                "transform_load_func_name": transform_load_func_name,
                "extracted_data": result,
                "config": config
            })
            successful_extractions += 1
        else:
            # Log that we are skipping this one
             logger.warning(f"Skipping transform argument preparation for a None or invalid result from extraction: {result}")
    logger.info(f"Prepared {len(kwargs_list)} arguments for transform task (corresponding to {successful_extractions} successful extractions).")
    return kwargs_list


def find_untransformed_files(config: Dict[str, Any], already_transformed_files: Set[str]) -> List[str]:
    input_folder = config["input_folder"]
    file_pattern = config['file_pattern']
    non_transformed_files_list = []
    logger.info(f"Scanning {input_folder} for new files matching '{file_pattern}'...")
    try:
        prefix = file_pattern.split('*')[0] if '*' in file_pattern else ''
        suffix = file_pattern.split('*')[-1] if '*' in file_pattern else ''
        is_exact_match = '*' not in file_pattern
        all_files_in_dir = [f for f in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder, f))]
        matched_files = []
        for f in all_files_in_dir:
            if is_exact_match:
                if f == file_pattern:
                    matched_files.append(f)
            else:
                if f.startswith(prefix) and f.endswith(suffix):
                    matched_files.append(f)
        all_files_set = set(matched_files)
        non_transformed_files_set = all_files_set - already_transformed_files
        non_transformed_files_list = sorted(list(non_transformed_files_set))
        logger.info(f"Found {len(all_files_set)} total files matching pattern.")
        logger.info(f"{len(already_transformed_files)} files already processed.")
    except FileNotFoundError:
        logger.error(f"Input directory not found: {input_folder}")
        return []
    except OSError as e:
        logger.error(f"Error listing directory {input_folder}: {e}", exc_info=True)
        raise
    count = len(non_transformed_files_list)
    if count > 0:
        logger.info(f"Found {count} new files to process.")
        display_limit = 10
        if count > display_limit:
            logger.debug(f"Files to process: {non_transformed_files_list[:display_limit//2]}...{non_transformed_files_list[-display_limit//2:]}")
        else:
            logger.debug(f"Files to process: {non_transformed_files_list}")
    else:
        logger.info("No new files found to process.")
    return non_transformed_files_list

def extract(config: Dict[str, Any], file_name: str) -> Optional[Dict[str, Any]]:
    import os
    import logging
    import numpy as np
    import pandas as pd
    from asammdf import MDF
    from preprocessing.read_mf4 import check_channel_completeness
    
    
    input_folder = config["input_folder"]
    output_folder = config["output_folder"]
    channel_mapper = config['channel_mapper']
    channels_to_extract = list(channel_mapper.keys())
    input_path = os.path.join(input_folder, file_name)
    output_name = os.path.splitext(file_name)[0] + ".h5"
    output_path = os.path.join(output_folder, output_name)
    file_ext = os.path.splitext(file_name)[1].lower()

    logger = logging.getLogger(f"{__name__}.extract_venv")
    logger.info(f"Attempting extraction: {input_path}")
    if not channels_to_extract:
        logger.warning(f"Channel mapper empty for {file_name}. Skipping.")
        return None

    try:
        if file_ext == '.mf4':
            with MDF(input_path, memory='low') as mdf_obj:
                logger.info(f"Checking channel completeness for {file_name}...")
                is_complete = check_channel_completeness(mdf_obj, channel_mapper)
                if not is_complete:
                    logger.warning(f"check_channel_completeness failed for {file_name}. Skipping.")
                    return None
                logger.info(f"Channel check passed for {file_name}.")

                filtered_mdf = mdf_obj.filter(channels_to_extract)
                if not filtered_mdf.channels_db:
                    logger.warning(f"No specified channels found after filtering {file_name}. Skipping.")
                    return None

                target_mdf_for_df = filtered_mdf

                df_intermediate = None
                try:
                    df_intermediate = target_mdf_for_df.to_dataframe(time_from_zero=False, time_as_date=False, empty_channels='skip')
                except Exception as df_err:
                    logger.error(f"to_dataframe failed for {file_name}: {df_err}", exc_info=True)
                    return None

                if df_intermediate is None or df_intermediate.empty:
                    logger.warning(f"DataFrame empty after extraction/filtering for {file_name}. Skipping.")
                    return None
                try:
                    timestamps_np = df_intermediate.index.to_numpy(dtype=np.float64)
                except Exception as ts_err:
                    logger.error(f"Timestamp conversion error for {file_name}: {ts_err}", exc_info=True)
                    return None

                numpy_data: Dict[str, np.ndarray] = {}
                successful_channels = 0
                for input_channel, output_channel in config['channel_mapper'].items():
                    if input_channel in df_intermediate.columns:
                        try:
                            col_data = pd.to_numeric(df_intermediate[input_channel], errors='coerce').to_numpy(dtype=np.float64)
                            numpy_data[output_channel] = col_data
                            successful_channels += 1
                            if np.isnan(col_data).any():
                                logger.warning(f"NaNs found in channel '{output_channel}' (from '{input_channel}') in file {file_name}")
                        except Exception as col_err:
                            logger.warning(f"NumPy conversion error for channel '{input_channel}' in {file_name}: {col_err}")
                    else:
                        logger.warning(f"Channel '{input_channel}' not found in DataFrame for {file_name} (might be empty).")

                if successful_channels == 0:
                    logger.error(f"No channels successfully extracted to NumPy for {file_name}. Skipping.")
                    return None

                logger.info(f"Extracted {successful_channels} channel(s) for {file_name}")
                return {
                    'timestamps': timestamps_np,
                    'data': numpy_data,
                    'output_path': output_path,
                    'input_filename': file_name,
                    'input_path': input_path
                }
        else:
            logger.warning(f"Unsupported file extension '{file_ext}' in {file_name}. Skipping.")
            return None
    except FileNotFoundError:
        logger.error(f"Input file not found during extraction: {input_path}")
        return None
    except ImportError as e:
        logger.error(f"Import Error during extraction (missing dependency?): {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Unexpected error during extraction for {file_name}: {e}", exc_info=True)
        return None


def transform_and_load_single(transform_load_func_name: str, extracted_data: Optional[Dict[str, Any]], config: Dict[str, Any]) -> Optional[Dict[str, str]]:
    import logging
    import importlib
    import numpy as np
    from asammdf import MDF
    
    from preprocessing.read_mf4 import create_table_description

    logger = logging.getLogger(f"{__name__}.transform_load_venv")
   

    if extracted_data is None:
        logger.info("Skipping transform/load: No data received from extraction task (likely skipped upstream).")
        return None

    try:
        module_name, func_name = transform_load_func_name.rsplit('.', 1)
        module = importlib.import_module(module_name)
        transform_load_func = getattr(module, func_name)
    except (ImportError, AttributeError, ValueError) as e:
        logger.error(f"Could not import transform_load_func '{transform_load_func_name}': {e}", exc_info=True)
        return None


    timestamps: Optional[np.ndarray] = extracted_data.get('timestamps')
    data: Optional[Dict[str, np.ndarray]] = extracted_data.get('data')
    output_hdf5_path: Optional[str] = extracted_data.get('output_path')
    input_filename: str = extracted_data.get('input_filename', 'Unknown Filename')
    input_mdf_path: Optional[str] = extracted_data.get('input_path')
    channel_mapper: Optional[Dict[str, str]] = config.get('channel_mapper')

    if timestamps is None or data is None or not output_hdf5_path or not input_mdf_path or not data or channel_mapper is None:
        logger.error(f"Missing required data/paths/mapper for processing {input_filename}. Cannot proceed.")
        return None

    logger.info(f"Orchestrating save for: {input_filename} -> {output_hdf5_path}")

    TableDescription = None
    structured_array = None
    success = False

    try:
        logger.debug(f"Re-opening original MDF {input_mdf_path} to get table description...")
        with MDF(input_mdf_path, memory='low') as mdf_obj_reopened:
            TableDescription, _ = create_table_description(mdf_obj_reopened, channel_mapper)

        if TableDescription is None:
            logger.error(f"create_table_description failed for {input_filename} using {input_mdf_path}. Cannot create HDF5 structure.")
            return None
        logger.info(f"Obtained table description class: {getattr(TableDescription, '__name__', repr(TableDescription))} for {input_filename}")

        num_rows = len(timestamps)

        if num_rows == 0:
            logger.warning(f"No data rows found for {input_filename}. Calling writer with empty structured array.")
            structured_array = np.empty(0, dtype=TableDescription._v_dtype.descr)
        else:
            structured_array = np.empty(num_rows, dtype=TableDescription._v_dtype.descr)

            timestamp_col_name = 'timestamp_s'
            if timestamp_col_name in TableDescription._v_dtype.names:
                try:
                    target_ts_dtype = TableDescription._v_dtype[timestamp_col_name]
                    structured_array[timestamp_col_name] = timestamps.astype(target_ts_dtype)
                except Exception as ts_assign_err:
                    logger.error(f"Failed to assign timestamps to '{timestamp_col_name}' for {input_filename}: {ts_assign_err}", exc_info=True)
                    return None
            else:
                logger.warning(f"Column '{timestamp_col_name}' not found in table description for {input_filename}. Timestamps will not be saved in this column.")

            for name, arr in data.items():
                if name in TableDescription._v_dtype.names:
                    if arr.shape[0] != num_rows:
                        logger.error(f"Row count mismatch for data column '{name}' ({arr.shape[0]}) vs timestamps ({num_rows}) in {input_filename}. Aborting.")
                        return None
                    try:
                        target_dtype = TableDescription._v_dtype[name]
                        if np.issubdtype(target_dtype, np.integer) and np.isnan(arr).any():
                            logger.warning(f"NaNs found in column '{name}' for {input_filename}; replacing with 0 before casting to integer.")
                            arr_filled = np.nan_to_num(arr, nan=0)
                            structured_array[name] = arr_filled.astype(target_dtype)
                        elif np.issubdtype(target_dtype, np.bool_) and np.isnan(arr).any():
                            logger.warning(f"NaNs found in column '{name}' for {input_filename}; treating as False before casting to boolean.")
                            arr_filled = np.nan_to_num(arr, nan=0)
                            structured_array[name] = arr_filled.astype(target_dtype)
                        else:
                            structured_array[name] = arr.astype(target_dtype)
                    except Exception as cast_err:
                        logger.error(f"Failed to cast data for column '{name}' to type {target_dtype} for {input_filename}: {cast_err}", exc_info=True)
                        return None
                else:
                    logger.warning(f"Data column '{name}' extracted but not found in the final table description for {input_filename}. It will not be saved.")

        logger.debug(f"Prepared structured array with {num_rows} rows for {input_filename}.")

        logger.info(f"Calling provided transform_load_func '{transform_load_func_name}' to write data for {input_filename}...")
        success = transform_load_func(
            output_hdf5_path,
            TableDescription,
            structured_array
        )

        if success:
            logger.info(f"transform_load_func reported SUCCESS for {input_filename}")
            return {'input_filename': input_filename, 'output_path': output_hdf5_path}
        else:
            logger.error(f"transform_load_func reported FAILURE for {input_filename}. Check the implementation of that function.")
            return None

    except FileNotFoundError:
        logger.error(f"Failed to re-open MDF file {input_mdf_path} for getting description.", exc_info=True)
        return None
    except ImportError as e:
        logger.error(f"Import error during transform/load orchestration (missing dependency?): {e}", exc_info=True)
        return None
    except AttributeError as e:
        logger.error(f"Attribute error during table description handling or array preparation for {input_filename} (check TableDescription structure): {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Unexpected error during transform/load orchestration for {input_filename}: {e}", exc_info=True)
        return None


def log_processed_files(config: Dict[str, Any], processed_results: List[Optional[Dict[str, str]]], previously_transformed_files: Set[str]) -> Set[str]:
    successfully_processed_info = [item for item in processed_results if item is not None and 'input_filename' in item]

    if not successfully_processed_info:
        logger.info("No new files were successfully processed and loaded in this run.")
        return previously_transformed_files

    pickle_path = os.path.join(config["output_folder"], "processed_files.pkl") # Corrected to use output_folder
    newly_processed_filenames = {info['input_filename'] for info in successfully_processed_info}

    logger.info(f"Logging {len(newly_processed_filenames)} newly processed files.")
    logger.debug(f"Newly processed files: {newly_processed_filenames}")

    updated_files_set = previously_transformed_files.union(newly_processed_filenames)

    try:
        with open(pickle_path, 'wb') as f:
            pickle.dump(updated_files_set, f)
        logger.info(f"Updated processed files state log at {pickle_path}. Total count: {len(updated_files_set)}")
    except Exception as e:
        logger.critical(f"CRITICAL: Failed to write state file {pickle_path}: {e}", exc_info=True)
        raise IOError(f"CRITICAL: Failed to write state to {pickle_path}") from e

    return updated_files_set


def save_pytables_data(
    output_hdf5_path: str,
    table_description,
    structured_data: np.ndarray
    ) -> bool:

    import tables
    writer_logger = logging.getLogger(f"{__name__}.save_pytables_data")
    writer_logger.debug(f"Attempting to write {len(structured_data)} rows to {output_hdf5_path}")

    output_dir = os.path.dirname(output_hdf5_path)
    try:
        os.makedirs(output_dir, exist_ok=True)
    except OSError as e:
        writer_logger.error(f"Failed to create output directory {output_dir}: {e}", exc_info=True)
        return False

    try:
        with tables.open_file(output_hdf5_path, mode="w", title="Processed MF4 Data") as h5file:
            group_path = "/data"
            table_name = "measurements"
            data_group = h5file.create_group(h5file.root, group_path.strip('/'), "Timeseries Data")
            filters = tables.Filters(complib='zlib', complevel=5)
            data_table = h5file.create_table(data_group, table_name,
                                             description=table_description,
                                             title="Measurement Data",
                                             filters=filters)
            if len(structured_data) > 0:
                data_table.append(structured_data)

            data_table.flush()
            writer_logger.info(f"Successfully wrote {len(structured_data)} rows to table '{group_path}/{table_name}' in {output_hdf5_path}")
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