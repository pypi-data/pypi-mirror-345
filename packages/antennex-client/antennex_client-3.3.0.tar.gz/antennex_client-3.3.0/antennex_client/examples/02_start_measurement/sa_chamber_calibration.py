from antennex_client import *

#
# Calibrate the Chamber Loss using a Spectrum Analyzer.
#
# The measurement setup requires:
# - Calibration module is installed in The Wireless Connector
# - A spectrum analyzer is connected
#
# Calibration happens in two steps:
# 1. Empty chamber, with DUT and cables removed. A solid feedthrough panel should be installed.
#    With this we run SACHAMBERCALIBRATIONSTEP1
# 2. Install the DUT, cables and feedthrough panel.
#    With this we run SACHAMBERCALIBRATIONSTEP2
#
# At the end of the calibration, the chamber losses will be plotted.
#

if __name__ == "__main__":

    frequency_start = 60e9
    frequency_end = 70e9

    # Create an instance of the API class
    hostname = hostname_from_file("hostname.txt")
    ReverbClient = create_client("http://" + hostname + ":8080")

    #Set the system to Spectrum mode
    ReverbClient.set_machine_mode(AcquisitionMode.SPECTRUM)

    # Start a spectrum acquisition using the current settings of the
    # reverberation chamber. Create a new settings object. It is initialized
    # with empty values. Only the values that we fill in will be sent to the
    # machine. More details can be found in a different example.

    # Create a settings object and set the frequencyStart and frequencyEnd keys
    settings = Settings(frequencyStart=frequency_start, frequencyEnd=frequency_end)

    # The acquire function with the optional argument Wait set to true is
    # blocking and the script will continue after the acquisition is finished.
    # Wait is set to true by default.
    # Change the SA settings. Then press enter to continue the script...
    input("Empty the chamber for the first calibration step and then press enter to continue the script...")
    ReverbClient.acquire(
        acquisition_type=AcquisitionTypes.SACHAMBERCALIBRATIONSTEP1, wait=True, settings=settings
    )
    print("Measurement is finished.")

    # The acquire function with the optional argument Wait set to true is
    # blocking and the script will continue after the acquisition is finished.
    # Wait is set to true by default.
    input("Setup your DUT for the second calibration step and then press enter to continue the script...")
    ReverbClient.acquire(
        acquisition_type=AcquisitionTypes.SACHAMBERCALIBRATIONSTEP2, wait=True, settings=settings
    )
    print("Measurement is finished.")

    # Get the data from the chamber
    data = ReverbClient.get_data(DataTypes.CHAMBERCALIBRATION)

    # Plot the data using the "plot" method of the Spectrum model.
    plot_spectrum(data)

    # sava data as json, as retrieved from instrument
    save_as_json(data, "test.json")

    # Save data as CSV
    save_as_csv(data, "test.csv")
