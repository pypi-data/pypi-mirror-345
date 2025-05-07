from antennex_client import *

#
# Perform FMCW Radar measurement with The Wireless Connector.
#
# The measurement setup requires:
# - FMCW application license is present on The Wireless Connector
# - FMCW Radar module running generating a chirp between 60 and 64 GHz
#   This is configurable with radar_frequency_start and radar_frequency_end
# - Mixer with LO at 59.4 GHz. This should down
#   The mixer frequency is configurable with lo_frequency.
# - Oscilloscope with first input connected to output of the Mixer.
# - Chamber loss calibration performed
#
# This examples will acquire a spectrogram and provide a plot and metrics.
#

if __name__ == "__main__":

    radar_frequency_start = 60e9
    radar_frequency_end = 64e9
    lo_frequency = 59.4e9

    # Create an instance of the API class
    hostname = hostname_from_file("hostname.txt")
    ReverbClient = create_client("http://" + hostname + ":8080")

    if not ReverbClient.is_version_greater_than("3.3"):
        print("This example requires The Wireless Connector software version 3.3 or higher.")
        exit()

    #Running this example required a license for the FMCW application to be installed on the chamber.
    licenses_installed = ReverbClient.get_license_info()
    assert "FMCW" in licenses_installed.licenses, "FMCW application is not licensed."

    #Set the system to FMCW mode
    ReverbClient.set_machine_mode(AcquisitionMode.FMCW)

    # Start an FMCW acquisition between 60 and 64 GHz.
    ReverbClient.restore_settings_to_defaults("measurement")
    settings = Settings()
    settings.frequency_start = radar_frequency_start
    settings.frequency_end = radar_frequency_end
    settings.time_start = 0.0e-6
    settings.time_end = 50.0e-6
    settings.stirrer_steps0 = 2
    settings.stirrer_steps1 = 2
    settings.fmcw = FmcwSettings()
    settings.fmcw.output_resolution = 256
    settings.fmcw.sft_overlap_factor = 0.75
    settings.fmcw.spectrogram_nfft = 1024
    settings.fmcw.lo_frequency = lo_frequency
    settings.fmcw.sideband = Sideband.UPPERSIDEBAND

    # The acquire function with the optional argument Wait set to true is
    # blocking and the script will continue after the acquisition is finished.
    # Wait is set to True by default.
    print("Measurement is starting...")
    ReverbClient.acquire(
        acquisition_type=AcquisitionTypes.FMCWSPECTROGRAM, wait=True, settings=settings
    )
    print("Measurement is finished.")

    # Get the data from the chamber
    data = ReverbClient.get_spectrogram()

    # Plot the data using the supplied plot_result function
    plot_result(data)

    # Display metrics about the measurement
    print("On-power = " + "{:.2f}".format(data.metrics.fmcw.pon) + "dBm")
    print("Rate = " + "{:.1f}".format(data.metrics.fmcw.rate/1e12) + "MHz/us")
    print("Linearity error = " + "{:.1f}".format(data.metrics.fmcw.rf/1e6) + "MHz")

    # sava data as json, as retrieved from instrument
    save_as_json(data, "test.json")

    # sava data as csv
    save_as_csv(data, "test.csv")