from antennex_client import *
import time

#
# Perform measurment using a Spectrum Analyzer.
#
# The measurement setup requires:
# - Calibration has been performed
# - A spectrum analyzer is connected
#
# This example illustrates the concept of how settings work and how measurement can be started:
# 1. Explicitly configure machine settings and perform acquisition.
#    It uses frequency range from frequency_start to frequency_end.
# 2. Override specific settings for this measurement only.
#    It uses frequency range from single_measurement_frequency_start to single_measurement_frequency_end.
# 3. Perform a measurement in a non-blocking way.
#    This uses the original frequency_start to frequency_end again.
# 4. Retrieve spectrum information and plot the data.
#

if __name__ == "__main__":

    frequency_start = 60e9
    frequency_end = 70e9

    single_measurement_frequency_start = 62e9
    single_measurement_frequency_end = 65e9

    # Create an instance of the API class
    hostname = hostname_from_file("hostname.txt")
    ReverbClient = create_client("http://" + hostname + ":8080")

    #Set the system to Spectrum mode
    ReverbClient.set_machine_mode(AcquisitionMode.SPECTRUM)

    #
    # EXAMPLE 1:
    #
    # Explicitly configure machine settings and perform acquisition.
    #

    print("Measurement start with explicitly setting machine settings...")

    # Start a spectrum acquisition using the current settings of the
    # reverberation chamber. Create a new settings object. It is initialized
    # with empty values. Only the values that we fill in will be applied on the
    # machine. Any other (empty) settings will remain as they are currently
    # configured.
    # More details can be found in a different example.
    settings = Settings(frequencyStart=frequency_start, frequencyEnd=frequency_end)
    ReverbClient.set_settings(SettingsTypes.MEASUREMENT, settings)

    # The acquire function with the optional argument Wait set to True is
    # blocking and the script will continue after the acquisition is finished.
    # Wait is set to True by default.
    ReverbClient.acquire(AcquisitionTypes.SPECTRUM, wait=True)

    print("Measurement is finished.")


    #
    # EXAMPLE 2:
    #
    # Override specific settings for this measurement only.
    #

    # Start a spectrum acquisition overriding specific settings.
    # A new settings object is created which overrides specific settings for this
    # measurement only.
    # The new settings are not stored on the machine. The get_settings(SettingsTypes.MEASUREMENT) function will return
    # the same settings before and after the call to acquire().
    measurement_settings = Settings(
        frequencyStart=single_measurement_frequency_start,
        frequencyEnd=single_measurement_frequency_end
    )
    ReverbClient.acquire(
        AcquisitionTypes.SPECTRUM,
        settings=measurement_settings,
        wait=True
    )


    #
    # EXAMPLE 3:
    #
    # Perform a measurement in a non-blocking way.
    #
    # Note: we expect example 1 has been run before and set the frequency range. This example doesn't call set_settings.
    #


    # It is also possible to start an acquisition in a non-blocking way,
    # allowing you to do other tasks in the meantime - such as checking the
    # progress of the chamber or monitoring the temperature of your antenna
    # under test.
    ReverbClient.acquire(
        AcquisitionTypes.SPECTRUM,
        wait=False
    )

    # We can do something useful background operation here.

    while True:
        chamber_status = ReverbClient.get_chamber_status()
        if chamber_status.status != "measuring":
            print("Done measuring.")
            break

        # We can do something useful background operation here.

        time.sleep(3)
        progress = ReverbClient.get_acquisition_progress()
        print("progress = " + "{:.1f}".format(progress.progress_percent))
        print("acquisition status = ", progress.acquisition_status)
        print("..................................")


    #
    # EXAMPLE 4:
    #
    # Retrieve spectrum information and plot the data
    #

    ## Get the data from the machine and save the data

    # Get the data from the chamber
    data = ReverbClient.get_data("Spectrum")

    # Plot the data using the supplied plot_result function
    plot_result(data)

    # Display metrics about the measurement
    print("Peak power = " + "{:.2f}".format(data.metrics.spectrum.peak_power))
    print("Uncertainty = " + "{:.1f}".format(data.metrics.spectrum.uncertainty))

    # sava data as json, as retrieved from instrument
    save_as_json(data, "test.json")

    # sava data as csv
    save_as_csv(data, "test.csv")

    ## Uncalibrated measurements

    # To perform uncalibrated measurements, change the trp_calibration_type setting to "none"
    settings = Settings(frequencyStart=60e9, frequencyEnd=70e9, trpCalibrationType="none")
    ReverbClient.acquire(
        acquisition_type=AcquisitionTypes.SPECTRUM, wait=False, settings=settings
    )

    ## Cancelling measurements

    # To cancel any running acquisitions, use the cancelAcquisition method
    ReverbClient.cancel_acquisition()
