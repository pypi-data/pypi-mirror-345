from antennex_client import *

#
# Perform a zero-span measurment using a Spectrum Analyzer.
#
# The measurement setup requires:
# - Calibration has been performed
# - A spectrum analyzer is connected
#
# This example illustrates the concept of zero-span measurement.
# For generic example about performing measurements and using settings, see the spectrum_measurement.py file.
#

if __name__ == "__main__":

    ## Set up the client

    hostname = hostname_from_file("hostname.txt")

    ReverbClient = create_client("http://" + hostname + ":8080")
    # Set the system to Spectrum mode
    ReverbClient.set_machine_mode(AcquisitionMode.SPECTRUM)

    ## Start an acquisition

    #In order to perform a fast measurement for a single frequency point, it is
    # possible to perform a zero-span measurement. This measurement strategy
    # rotates the stirrers continuously, and records the signal for a fixed
    # amount of time. The time trace is averaged to arrive at the result. When
    # the RMS average detector is used, the number of points does not have an
    # influence on the measurement result. For a small number of points, the
    # averaging occurs largely on the SA. For a large number of points, the
    # averaging occurs largely on the RC.

    # The following conditions are recommended in order to
    # achieve a low uncertainty in a short amount of time:
    # - The stirrers should rotate continuously, one at 19 RPM and one at 20 RPM
    # - The number of stirrer "positions" is set to 1 for both stirrers.
    # - An SA preset should be configured with the following settings:
    # --- RMS detector
    # --- Sweep time between 1s (~0.5dB uncertainty) and 5s (~0.1dB uncertainty)
    # --- some number of points between 101 and 1001. The exact number does
    #     not matter, when RMS detector is used, 1001 points is the recommendation.
    # --- The RBW can be set as high as possible, as long as the signal
    #     dominates the noise floor.

    settings = ReverbClient.get_settings("measurement")
    settings.trp_calibration_type = "none"
    settings.continuous_stirring = True
    settings.frequency_start = 21.5e9
    settings.frequency_end = 21.5e9
    settings.stirrer_steps0 = 1
    settings.stirrer_steps1 = 1
    settings.stirrer_speed0 = 20
    settings.stirrer_speed1 = 19

    print("Measurement is starting...")
    ReverbClient.acquire("Spectrum", settings, wait = True)
    print("Measurement is finished.")

    ## Get the data from the machine and save the data

    # Get data from the chamber.
    data = ReverbClient.get_data(DataTypes.SPECTRUM)

    # Plot the data using the "plot" method of the Spectrum model.
    plot_result(data)

    # Display metrics about the measurement. Note the uncertainty calculation
    # can be inaccurate for zero-span measurements. For the recommended
    # settings, the uncertainty should be about 0.1dB with 5s sweep time.
    print("Peak power = " + "{:.2f}".format(data.metrics.spectrum.peak_power) + " dBm")
    print("Uncertainty = " + "{:.1f}".format(data.metrics.spectrum.uncertainty) + " dB")
    print("RBW = " + "{:.0f}".format(data.metrics.spectrum.rbw/1e6) + " MHz")
