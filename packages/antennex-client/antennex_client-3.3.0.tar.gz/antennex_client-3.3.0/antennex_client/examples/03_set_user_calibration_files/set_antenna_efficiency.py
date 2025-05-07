from antennex_client import *
import numpy as np
import matplotlib.pyplot as plt

if __name__ == "__main__":

    # Create an instance of the API class
    hostname = hostname_from_file("hostname.txt")
    ReverbClient = create_client("http://" + hostname + ":8080")
    #Set the system to Spectrum mode
    ReverbClient.set_machine_mode(MachineMode(mode=AcquisitionMode.SPECTRUM))

    # For performing absolute measurements, the reverberation chamber must have
    # a calibration file that describes the gain of the efficiency of the
    # referenced antenna. The efficiency should be given in dB, as a
    # function of the RF-frequency. Consult the manual for more details.

    # Load your data here. We generate a simple line from -2dB gain at 40GHz to
    # -4dB gain at 80GHz with 1000 points as an example.

    frequency = np.linspace(40e9, 80e9, 1000)
    gain = (-frequency / 100.0e9).tolist()

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

    ReverbClient.set_data(DataTypes.ANTENNAEFFICIENCY, calibrationData)

    # Get the data back from the machine and plot it in order to show the
    # external calibration file was properly set.

    data = ReverbClient.get_data(DataTypes.ANTENNAEFFICIENCY)

    # Plot the data using the "plot" method of the Spectrum model.

    plot_spectrum(data)
