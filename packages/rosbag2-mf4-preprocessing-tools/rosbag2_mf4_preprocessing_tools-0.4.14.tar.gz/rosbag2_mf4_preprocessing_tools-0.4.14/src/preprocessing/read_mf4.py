import logging
from datetime import datetime
from pathlib import Path
import os

import numpy as np
import numpy.lib.recfunctions as rfn
import tables
import yaml
from asammdf import MDF


LOGGER = logging.getLogger()

INPUT_FILE = "/mnt/sambashare/ugglf/2025-04-16/rec1_001.mf4"
OUTPUT_DIR = "/mnt/sambashare/ugglf/2025-04-16_output/"
CONFIG_PATH = "/home/bora/measurement-data-processing/dags/configs/mf4_config.yaml"



def check_channel_completeness(mdf_obj: MDF, cfg: dict):
    mdf_channel_list = []
    for group in mdf_obj.groups:
        mdf_channel_list = mdf_channel_list + [channel.name for channel in group.channels]

    not_in_mdf = list(set(list(cfg.keys())) - set(mdf_channel_list))
    not_in_cfg = list(set(mdf_channel_list) - set(list(cfg.keys())))

    if (not_in_mdf == []) and (not_in_cfg == []):
        LOGGER.info("All elements in MDF file and config match")
        return True

    if not_in_mdf != []:
        LOGGER.warning("There are elements in config which are not in MDF file: \n%s" % "\n".join(not_in_mdf))
    if not_in_cfg != []:
        LOGGER.warning("There are elements in MDF file which are not in config: \n%s" % "\n".join(not_in_cfg))

    return False

def create_table_description(mdf_obj, cfg):
    #dtype_list = [("timestamp_s", np.dtype(np.float64))]
    dtype_list = []
    for key, value in cfg.items():
        samples = mdf_obj.get(key).samples

        if samples.dtype.fields is not None:
            samples = rfn.structured_to_unstructured(mdf_obj.get(key).samples)

        name = value
        
        if name == "measurement_wheel_angular_velocity_actual_rps":
            continue
        shape = samples.shape
        dtype = samples.dtype
        ndim = samples.ndim

        if ndim == 1:
            dtype_list.append((name, dtype))
        elif ndim > 1:
            dtype_list.append((name, (dtype, (shape[1],))))
        else:
            raise ValueError("Number of dimension of signal '%s' is empty of negative" % name)
    print(dtype_list)
    return tables.descr_from_dtype(np.dtype(dtype_list))


if __name__ == "__main__":
    try:
        with open(CONFIG_PATH, "r") as cfg_file:
            cfg = yaml.safe_load(cfg_file)
    except Exception as e:
        logging.error("Could not read file {}: {}".format(cfg_file, e))

    directory_name = Path(OUTPUT_DIR) / Path(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    directory_name.mkdir(parents=False, exist_ok=False)

    
    mdf_obj = MDF(INPUT_FILE)
    mdf_obj.configure(integer_interpolation=0, float_interpolation=0)
    mdf_obj = mdf_obj.resample("HostService")
    status = check_channel_completeness(mdf_obj, cfg)
    for group in mdf_obj.groups:
        for channel in group.channels:
            channel.name = cfg[channel.name]
    mdf_obj.save(os.path.join(directory_name, INPUT_FILE.split(sep="/")[-1].split(".")[0]))
    # if status is True:
    # mdf_obj = rename_channel_names(mdf_obj, cfg)
    print(create_table_description(mdf_obj, cfg))
    # for channel in cfg.keys():
    #    print(mdf_obj.get(channel).samples.shape, mdf_obj.get(channel).samples.dtype)
    # print(mdf_obj.get("HostService").timestamps, mdf_obj.get("HostService").samples)
    #df = flatten_mdf(mdf_obj)
    #print(df["measurement_wheel_forces_wishbones_actual_N"])
    #df.to_hdf("test1.h5", key="rfmu_mabx2", mode="w")