from antennex_client import *

#
# Calibrate the Chamber Loss using a Vector Network Analyzer.
#
# The measurement setup requires:
# - A vector network analyzer is connected
#
# A calibration is performed and subsequently the chamber gain is plotted.
#
# At the end of the calibration, the chamber losses will be plotted.
#

if __name__ == "__main__":

    ## Set up the client

    hostname = hostname_from_file("hostname.txt")
    ReverbClient = create_client("http://" + hostname + ":8080")

    # Set the system to Spectrum mode
    ReverbClient.set_machine_mode(AcquisitionMode.SPECTRUM)

    ## Start an acquisition

    # Start a VNA acquisition between 55 and 90 GHz using a sufficient number of points.

    ReverbClient.restore_settings_to_defaults(SettingsTypes.MEASUREMENT)
    settings = models.Settings(
        frequencyStart=55e9,  # GHz
        frequencyEnd=90e9,  # GHz
        resolution=100001,
        stirrer_steps0=10,
        stirrer_steps1=10,
        step_angle_stirrer_0=10,
        step_angle_stirrer_1=10,
        continuous_stirring=False,
    )

    # The acquire function with the optional argument Wait set to true is
    # blocking and the script will continue after the acquisition is finished.
    # Wait is set to true by default.

    print("Measurement started...")
    ReverbClient.acquire(
        acquisition_type=AcquisitionTypes.VNACHAMBERCALIBRATION,
        settings=settings,
        wait=True,
    )
    print("Measurement is finished.")

    ##Get the data from the machine

    # Get data from the chamber. We performed a chamber calibration.
    calibrationData = ReverbClient.get_data(DataTypes.CHAMBERCALIBRATION)
    # Plot the data using the "plot" method of the Spectrum model.
    plot_spectrum(calibrationData)
    # save data
    saveData = calibrationData.data
    file = open("referenceCalibrationApi.txt", "w")
    file.write(saveData.__str__())
