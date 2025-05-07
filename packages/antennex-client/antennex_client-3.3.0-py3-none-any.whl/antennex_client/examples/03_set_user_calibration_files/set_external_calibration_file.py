from antennex_client import *
import numpy as np
import matplotlib.pyplot as plt

if __name__ == "__main__":

    ## Set up the client

    # Create an instance of the API class
    hostname = hostname_from_file("hostname.txt")
    ReverbClient = create_client("http://" + hostname + ":8080")
    #Set the system to Spectrum mode
    ReverbClient.set_machine_mode(AcquisitionMode.SPECTRUM)

    ## Set a calibration file.

    # For performing absolute measurements, the reverberation chamber must have
    # a calibration file that describes the gain of the externally connected
    # equipment. This equipment can be anything such as waveguides, mixer
    # converters, or coaxial cables. The gain should be given in dB, as a
    # function of the RF-frequency. If you are using a downconverter, specify
    # the RF frequency range at the high frequency side connected to the
    # chamber. Consult the manual for more details.

    # Load your data here. We generate a simple line from -2dB gain at 40GHz to
    # -4dB gain at 80GHz with 1000 points as an example.

    frequency = np.linspace(40e9, 80e9, 1000)
    gain = (-frequency / 20.0e9).tolist()

    plt.plot(frequency / 1e9, gain)
    plt.title("")
    plt.xlabel("frequency [GHz]")
    plt.ylabel("Gain [dB]")
    plt.grid(True)
    plt.show()

    # Create a Spectrum model which can be communicated to the machine. For
    # this, use the provided "createCalibrationData" helper function.

    calibrationData = create_calibration_data(frequency, gain)

    # Send the data to the machine.

    ReverbClient.set_data(DataTypes.EXTERNALCALIBRATION, calibrationData)

    ## Get the data from the machine

    # Get the data back from the machine and plot it in order to show the
    # external calibration file was properly set.

    data = ReverbClient.get_data(DataTypes.EXTERNALCALIBRATION)

    # Plot the data using the "plot" method of the Spectrum model.

    plot_spectrum(data)
