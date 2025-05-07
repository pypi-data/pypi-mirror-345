from antennex_client.api import AntennexApi
from antennex_client.configuration import Configuration
from antennex_client.api_client import ApiClient
from antennex_client import models, MeasurementUnits
import numpy as np
import json
from typing import Union

def hostname_from_file(file):
    """Retrieves the hostname from a specified file.

    Attempts to read the hostname, searching for typical locations for the examples.
    If unsuccessful, it throws an exception.

    :param file: The filename of the file containing the hostname.
    :type file: string
    :return: The string representing the hostname read from the file. An exception
             is raised on error.
    """
    try:
        with open(file, 'r') as file:
            return file.read().rstrip()
    except:
        try:
            with open("../" + file, 'r') as file:
                return file.read().rstrip()
        except:
            with open("antennex_client/examples/" + file, 'r') as file:
                return file.read().rstrip()
    
def create_client(hostname):
    """Creates and configures an API client for interacting with the reverberation chamber.

    :param hostname: The IP address or hostname of the reverberation chamber.
    :type hostname: string
    :returns: AntennexApi: An instance of the API class configured to communicate with the specified hostname.
    """
    # Configuration
    configuration = Configuration(
        host=hostname, # Replace hostname with the IP or hostname of the reverberation chamber.
    )
    # Create an API client with the configured settings
    api_client = ApiClient(configuration)
    # Create an instance of the API class
    myReverb = AntennexApi(api_client)
    return myReverb

def plot_result(data: Union[models.Spectrum, models.Spectrogram], show: bool = True, label = "Line"):
    """Plots received data using matplotlib

    :param data: Data to use as input for the plot
    :type data: Union[models.Spectrum, models.Spectrogram]
    :param show: Call matplotlib show() function to display the plot. This is done by default.
    :type show: bool
    :param label: Set a label that will be displayed in the legend. By default it is "Line".
    :type label: str
    """
    if type(data) == models.Spectrogram:
        plot_spectrogram(data, show)
    elif type(data) == models.Spectrum:
        plot_spectrum(data, show, label)
    else:
        raise NotImplementedError("Support this this data type has not been implemented")

def plot_spectrum(data: models.Spectrum, show: bool = True, label="Line"):
    """Plots spectrum data using matplotlib

    :param data: Data to use as input for the plot
    :type data: Union[models.Spectrum, models.Spectrogram]
    :param show: Call matplotlib show() function to display the plot. This is done by default.
    :type show: bool
    :param label: Set a label that will be displayed in the legend. By default it is "Line".
    :type label: str
    """
    import matplotlib.pyplot as plt
    x_min = data.settings.frequency_start
    x_max = data.settings.frequency_end
    nx = data.settings.resolution
    x_axis = np.linspace(x_min, x_max, nx)/1e9
    y_axis = data.data
    plt.plot(x_axis, y_axis, label=label)
    plt.title("Spectrum")
    plt.xlabel("frequency [GHz]")
    plt.ylabel("Magnitude [dBm]")
    if show:
        plt.show()

def plot_spectrogram(data: models.Spectrogram, show: bool = True):
    """Plots spectrogram data using matplotlib

    :param data: Data to use as input for the plot
    :type data: models.Spectrogram
    :param show: Call matplotlib show() function to display the plot. This is done by default.
    :type show: bool
    """
    import matplotlib.pyplot as plt
    x_min = data.settings.time_start
    x_max = data.settings.time_end
    y_min = data.settings.frequency_start
    y_max = data.settings.frequency_end
    nx = data.settings.fmcw.output_resolution
    ny = data.settings.fmcw.output_resolution

    x_axis = np.linspace(x_min, x_max, nx)*1e6
    y_axis = np.linspace(y_min, y_max, ny)/1e9
    X, Y = np.meshgrid(x_axis, y_axis)

    cf = plt.contourf(X, Y, list(map(list, zip(*data.data))), 10)
    plt.colorbar(cf, label="PSD [dBm/MHz]")
    plt.title("Spectrogram")
    plt.xlabel(u"time [\u03bcs]")
    plt.ylabel("frequency [GHz]")

    if show:
        plt.show()

def save_as_csv(data: Union[models.Spectrum, models.Spectrogram], filename: str):
    # Create a header from information that is relevant.
    header = json.dumps(data.settings.to_dict(), sort_keys=True, indent=4)
    # ... Something else.. make this nicer .. allow spectrum... # ......TODO...
    np.savetxt(filename, data.data, delimiter=',', header = header)

def save_as_json(data: Union[models.Spectrum, models.Spectrogram], filename: str):
    serialized = data.to_json()
    with open(filename, 'w') as outfile:
        outfile.write(serialized)

def create_calibration_data(frequency: np.array, gain: np.array):
    settings = models.Settings(
        frequency_start=min(frequency),
        frequency_end=max(frequency),
        resolution=len(frequency)
    )
    calibration_model = models.Spectrum(
        data=gain,
        unit= MeasurementUnits.DB,
        settings=settings
    )
    return calibration_model