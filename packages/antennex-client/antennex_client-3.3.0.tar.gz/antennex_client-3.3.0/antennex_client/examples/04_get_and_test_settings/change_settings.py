from antennex_client import *

#
# The Wireless Connector retrains settings for the measurements.
#
# The instrument maintains separate settings for calibration and measurement. The example illustrates how settings
# can be updated. Additionally, settings can be overridden on a per-acquisition basis.
#
# In this example we will illustrate how:
# 1. Get settings
# 2. Set specific settings
# 3. Save and restore settings
# 4. Override settings on a per-acquisition basis
# 5. Restore settings to defaults
#

if __name__ == "__main__":

    ## Set up the client

    hostname = hostname_from_file("hostname.txt")
    ReverbClient = create_client("http://" + hostname + ":8080")

    # Set the system to Spectrum mode
    ReverbClient.set_machine_mode(AcquisitionMode.SPECTRUM)

    #
    # EXAMPLE 1:
    #
    # Get settings
    #

    retrieve_settings = ReverbClient.get_settings("measurement")
    print(retrieve_settings)


    #
    # EXAMPLE 2:
    #
    # Set settings
    #

    #
    # To set specific settings, it is unnecessary to call get_settings. Rather, the settings object can be set with
    # desired values. Subsequently The Wireless Connector will correctly merge changed and existing values.
    #

    # Set frequency information
    set_settings_one = Settings(
        frequency_start = 50e9,  # change the start frequency to 50GHz
        frequency_end = 70e9,  # change the end frequency to 70GHz
    )
    ReverbClient.set_settings("measurement", set_settings_one)

    # Set stirrer steps
    set_settings_two = Settings()
    set_settings_two.stirrer_steps0 = 20  # change the number of stirrer position of stirrer 0 to 20
    set_settings_two.stirrer_steps1 = 5  # change the number of stirrer position of stirrer 1 to 5
    ReverbClient.set_settings("measurement", set_settings_two)

    # Set both settings in a single operation
    set_settings_one_shot = Settings(
        frequency_start = 50e9,  # change the start frequency to 50GHz
        frequency_end = 70e9,  # change the end frequency to 70GHz
        stirrer_steps0 = 20,  # change the number of stirrer position of stirrer 0 to 20
        stirrer_steps1 = 5,  # change the number of stirrer position of stirrer 1 to 5
    )
    ReverbClient.set_settings("measurement", set_settings_one_shot)

    # The API contains several convenience functions for several settings
    settings_frequency_start_end = Settings()
    settings_frequency_start_end.set_frequency(50e9, 70e9)

    settings_frequency_center_span = Settings()
    settings_frequency_center_span.set_frequency_center_span(60e9, 20e9)

    #
    # EXAMPLE 3:
    #
    # Save and restore settings
    #

    # Retrieve settings from chamber
    retrieve_settings = ReverbClient.get_settings("measurement")
    # Save settings to a file
    with open("settings.json", "w") as file:
        file.write(retrieve_settings.to_json())

    # Read the settings
    with open("settings.json", "r") as file:
        settings_to_restore = Settings.from_json(file.read())
    # Apply settings to restore
    ReverbClient.set_settings("measurement", settings_to_restore)


    #
    # EXAMPLE 4:
    #
    # Override settings on a per-acquisition basis
    #

    # The applied settings will be used in later acquisitions, however, the settings can be overridden for a specific
    # acquisition.
    #
    # This is useful when multiple acquisitions are performed where some settings are different for each acquisition. This
    # removes the slight delay in having to explicitly set these between acquisitions.

    # Create an empty status structure. For each value that you would like to
    # override during the acquisition, specify a value. Leave the other
    # settings empty, which will not be overridden.
    settings = Settings(
        frequency_start=60e9,
        frequency_end=70e9
    )
    # Start an acquisition where existing settings are merged with these settings.
    ReverbClient.acquire(
        acquisition_type=AcquisitionTypes.SPECTRUM, wait=False, settings=settings
    )

    # Note that overridden settings are not saved to the machine. Settings are
    # only saved when using the setSettings method.
    settings = ReverbClient.get_settings("measurement")
    print(settings)  # -> frequencyStart is still set to 50GHz.

    # Cancel this acquisition
    ReverbClient.cancel_acquisition()

    #
    # EXAMPLE 5:
    #
    # Save and restore settings
    #

    # Revert the settings to defaults
    ReverbClient.restore_settings_to_defaults("measurement")
