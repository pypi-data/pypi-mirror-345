from antennex_client import *
import numpy as np
import matplotlib.pyplot as plt

if __name__ == "__main__":

    # Create an instance of the API class
    hostname = hostname_from_file("hostname.txt")
    ReverbClient = create_client("http://" + hostname + ":8080")
    #Set the system to Spectrum mode
    ReverbClient.set_machine_mode(MachineMode(mode=AcquisitionMode.SPECTRUM))

    ## Show the calibration files.

    # For performing absolute measurements, the reverberation chamber must have
    # several calibration files present
    # 1) ReferenceCalibration: the gain of the empty chamber (in dB) as determined
    # during a calibration by ANTENNEX.
    # 2) AntennaEfficiency: the efficiency (in dB) of the antenna connected to
    # the receiving chain.
    # 3) ExternalCalibration: the (conversion) gain (in dB) of your external
    # equipment such as waveguides or mixers.
    # 4) ChamberGain: the gain (in dB) of the chamber when a DUT is present in
    # the chamber. It is computed as a function of the ReferenceCalibration and
    # the calibration steps carried out by the user.

    # Let's retrieve the currently set calibration files and plot them.

    lgd = []
    try:
        referenceCalibration = ReverbClient.get_data("ReferenceCalibration")
        plot_result(referenceCalibration, show=False, label="Reference Calibration")
        lgd.append("Reference Calibration")
    except Exception as e:
        print("Reference Calibration could not be loaded: " + repr(e))
        referenceCalibration = None

    try:
        antennaEfficiency = ReverbClient.get_data("AntennaEfficiency")
        plot_result(antennaEfficiency, show=False, label="Antenna Efficiency")
        lgd.append("Antenna Efficiency")
    except Exception as e:
        print("Antenna Efficiency could not be loaded: " + repr(e))
        antennaEfficiency = None

    try:
        externalCalibration = ReverbClient.get_data("ExternalCalibration")
        plot_result(externalCalibration, show=False, label="External Calibration")
        lgd.append("External Calibration")
    except Exception as e:
        print("External Calibration could not be loaded: " + repr(e))
        externalCalibration = None
    try:
        chamberCalibration = ReverbClient.get_data("ChamberCalibration")
        plot_result(chamberCalibration, show=False, label="Chamber Calibration")
        lgd.append("Chamber Calibration")
    except Exception as e:
        print("Chamber Calibration could not be loaded: " + repr(e))
        chamberCalibration = None

    # If all calibration files are present, calculate and show the total
    # calibration added to the measurements. The total calibration is the sum
    # of AntennaEfficiency, ExternalCalibration and ChamberCalibration.

    if (
        referenceCalibration is not None
            and antennaEfficiency is not None
            and externalCalibration is not None
            and chamberCalibration is not None
    ):
        f_min = max(
            [
                referenceCalibration.settings.frequency_start,
                antennaEfficiency.settings.frequency_start,
                externalCalibration.settings.frequency_start,
                chamberCalibration.settings.frequency_start,
            ]
        )
        f_max = min(
            [
                referenceCalibration.settings.frequency_end,
                antennaEfficiency.settings.frequency_end,
                externalCalibration.settings.frequency_end,
                chamberCalibration.settings.frequency_end,
            ]
        )

        if f_min < f_max:
            try:
                # Find the ranges of the calibration data
                ae_range = np.linspace(antennaEfficiency.settings.frequency_start,
                                      antennaEfficiency.settings.frequency_end,
                                      antennaEfficiency.settings.resolution)
                ec_range = np.linspace(externalCalibration.settings.frequency_start,
                                      externalCalibration.settings.frequency_end,
                                      externalCalibration.settings.resolution)
                cc_range = np.linspace(chamberCalibration.settings.frequency_start,
                                      chamberCalibration.settings.frequency_end,
                                      chamberCalibration.settings.resolution)

                # The range to interpolate the data to [fmin:fmax]
                f_interp = np.linspace(f_min, f_max, 1001)

                # Interpolate the data to the range between fmin and fmax
                antennaEfficiency.data = np.interp(f_interp, ae_range, antennaEfficiency.data)
                externalCalibration.data = np.interp(f_interp, ec_range, externalCalibration.data)
                chamberCalibration.data = np.interp(f_interp, cc_range, chamberCalibration.data)

                totalCalibration = (
                    np.asarray(antennaEfficiency.data)
                    + np.asarray(externalCalibration.data)
                    + np.asarray(chamberCalibration.data)
                )
                plt.plot(f_interp / 1e9, totalCalibration, label="Total Calibration")
                lgd.append("Total applied TRP/PSD calibration")

            except Exception as e:
                print("Could not perform interpolation. There may not be an overlapping frequency range.")
                print(e)

    # ================================

    plt.title("Chamber calibration files")
    plt.xlabel("frequency [GHz]")
    plt.ylabel("Gain [dB]")
    plt.xlim(18, 148)
    plt.grid(True)
    plt.legend(loc="best")
    plt.show()
