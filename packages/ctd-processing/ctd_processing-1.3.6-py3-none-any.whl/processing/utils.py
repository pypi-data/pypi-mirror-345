import sys
from pathlib import Path
import numpy as np
from seabirdfilehandler import CnvFile
from seabirdfilehandler.parameter import Parameter


def default_seabird_exe_path() -> Path:
    """Creates a platform-dependent default path to the Sea-Bird exes."""
    exe_path = "Program Files (x86)/Sea-Bird/SBEDataProcessing-Win32/"
    if sys.platform.startswith("win"):
        path_prefix = Path("C:")
    else:
        path_prefix = Path.home().joinpath(".wine/drive_c")
    return path_prefix.joinpath(exe_path)


def get_sample_rate(cnv: CnvFile) -> float:
    """Fetches the sample rate from a CnvFile."""
    interval_info = cnv.data_table_misc["interval"].split(":")
    if not interval_info[0] == "seconds":
        raise BinnedDataError(cnv.file_name, "get_sample_rate")

    return np.round(1 / float(interval_info[1]))


def is_directly_measured_value(parameter: Parameter) -> bool:
    """
    Returns whether a parameter has been measured via a sensor or is calculated.
    """
    value_list = [
        "Pressure",
        "Conductivity",
        "Temperature",
        "Oxygen",
        "PAR/Irradiance",
        "SPAR",
        "Fluorescence",
        "Turbidity",
    ]
    return parameter.metadata["name"] in value_list


class BinnedDataError(Exception):
    """A custom error to throw when binned data has been detected."""

    def __init__(self, file_name: str, step_name: str):
        super().__init__(f"{step_name} cannot be applied to binned data in {file_name}")
