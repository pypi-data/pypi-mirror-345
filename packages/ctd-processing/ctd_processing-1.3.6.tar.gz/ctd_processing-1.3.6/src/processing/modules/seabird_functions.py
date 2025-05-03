from pathlib import Path
import pandas as pd
import numpy as np
from scipy.signal import butter, filtfilt, correlate
import logging
from seabirdfilehandler.parameter import Parameter
from seabirdfilehandler.datatablefiles import CnvFile
from processing.module import ArrayModule, MissingParameterError

logger = logging.getLogger(__name__)


class AlignCTD(ArrayModule):
    """
    Align the given parameter columns.

    Given a measurement parameter in parameters, the column will be shifted
    by either, a float amount that is given as value, or, by a calculated
    amount, using cross-correlation between the high-frequency components of
    the temperature and the target parameters.
    The returned numpy array will thus feature the complete CnvFile data,
    with the columns shifted to their correct positions.
    """

    def __call__(
        self,
        input: Path | str | CnvFile | pd.DataFrame | np.ndarray,
        parameters: dict = {},
        name: str = "alignctd",
        output: str = "cnvobject",
        output_name: str | None = None,
        flag_value=-9.99e-29,
    ) -> None | CnvFile | pd.DataFrame | np.ndarray:
        self.flag_value = flag_value
        return super().__call__(input, parameters, name, output, output_name)

    def transformation(self) -> np.ndarray:
        """
        Performs the base logic of distinguishing whether to use given values
        or compute a delay.

        Returns
        -------
        A numpy array, representing the cnv data after the alignment.

        """
        assert len(self.parameters) > 0
        for key, value in self.parameters.items():
            if key not in self.cnv.parameters:
                raise ValueError(
                    f"Column {key} not in CnvFile {self.cnv.path_to_file}."
                )
            # if no shift value given, estimate it
            if not value:
                value = self.estimate_sensor_delay(
                    delayed_parameter=self.cnv.parameters[key],
                )
                self.parameters[key] = value
            index = [
                index for index, param in enumerate(self.cnv.parameters) if param == key
            ][0]

            sample_times = np.arange(
                0,
                len(self.array[:, index]) * self.sample_interval,
                self.sample_interval,
            )
            interp_res = np.interp(
                sample_times + float(value),
                sample_times,
                self.array[:, index],
                self.flag_value,
                self.flag_value,
            )

            self.array[:, index] = interp_res.round(decimals=4)

            # add s to output of parameters to indicate the shifting in
            # seconds
            self.parameters[key] = str(self.parameters[key]) + "s"
        return self.array

    def estimate_sensor_delay(
        self,
        delayed_parameter: Parameter,
        margin: int = 240,
        shift_seconds: int = 3600,
    ) -> float:
        """
        Estimate delay between a delayed parameter and temperature signals via
        cross-correlation of high-frequency components.

        Parameters
        ----------
        delayed_parameter: Parameter :
            The parameter whose delay shall be computed.

        margin: int :
            A number of data points that are cutoff from both ends.
             (Default value = 240)

        shift_seconds: int :
             Maximum time window to search for lag (default: 1 hour).

        Returns
        -------
        A float value, representing the parameter delay in seconds.

        """
        temperature = self.find_corresponding_temperature(delayed_parameter).data
        delayed_values = delayed_parameter.data
        assert len(temperature) == len(delayed_values)
        # conductivity is correlated, while oxygen is anticorrelated
        # remove edge effects (copying Gerds MATLAB software)
        while len(temperature) <= 2 * margin:
            margin = margin // 2

        t_shortened = np.array(temperature[margin:-margin])
        v_shortened = np.array(delayed_values[margin:-margin])

        if np.all(np.isnan(v_shortened)):
            return np.nan

        # design Butterworth filter
        nyq = 0.5 * self.sample_interval
        cutoff = 0.003 * nyq
        b, a = butter(3, cutoff / nyq)

        # smooth signals
        t_smoothed = filtfilt(b, a, t_shortened)
        v_smoothed = filtfilt(b, a, v_shortened)

        # high-frequency components
        t_high_freq = t_shortened - t_smoothed
        v_high_freq = v_shortened - v_smoothed

        # cross-correlation
        max_lag = int(shift_seconds * self.sample_interval)
        sign = self.get_correlation(delayed_parameter)
        corr = correlate(v_high_freq, t_high_freq * sign, mode="full")
        lags = np.arange(-len(t_high_freq) + 1, len(t_high_freq))
        lag_indices = np.where(np.abs(lags) <= max_lag)[0]

        corr_segment = corr[lag_indices]
        lags_segment = lags[lag_indices]
        lag_times_sec = lags_segment / self.sample_interval

        # find lag with highest correlation
        best_index = np.argmax(corr_segment)
        best_delay_sec = lag_times_sec[best_index]

        return float("{:.2f}".format(best_delay_sec))

    def find_corresponding_temperature(self, parameter: Parameter) -> Parameter:
        """
        Find the temperature values of the sensor that shared the same water
        mass as the input parameter.

        Parameters
        ----------
        parameter: Parameter :
            The parameter of interest.


        Returns
        -------
        The temperature parameter object.

        """
        if "0" in parameter.name:
            return self.cnv.parameters["t090C"]
        elif "1" in parameter.name:
            return self.cnv.parameters["t190C"]
        else:
            raise MissingParameterError("AlignCTD", "Temperature")

    def get_correlation(self, parameter: Parameter) -> float:
        """
        Gives a number indicating the cross correlation type regarding the
        input parameter and the temperature.

        Basically distinguishes between positive correlation, 1, and anti-
        correlation, -1. This value is then used to alter the temperature
        values accordingly.

        Parameters
        ----------
        parameter: Parameter :
            The parameter to cross correlate with temperature.

        Returns
        -------
        A float value representing positive or negative correlation.

        """
        if parameter.metadata["name"].lower() in ["oxygen", "oxygen 2"]:
            return -1
        else:
            return 1
