from antennex_client import *

# Connect to the chamber and change the spectrum analyser preset

if __name__ == "__main__":

    ## Set up the client

    hostname = hostname_from_file("hostname.txt")
    ReverbClient = create_client("http://" + hostname + ":8080")
    # Set the system to Spectrum mode
    ReverbClient.set_machine_mode(MachineMode(mode=AcquisitionMode.SPECTRUM))

    ## Device presets

    # The general approach to changing the settings of devices such as as
    # a spectrum analyser (SA), is to change the settings on the SA directly
    # and then save the preset in a folder known by the machine. Then, when an
    # acquisition is started, the machine loads the correct preset and applies
    # it. This makes it possible to use any SA configuration as long as it
    # produces a trace that can be read by the machine.

    # Change the SA settings. Then press enter to continue the script...
    input("Change the SA settings and then press enter to continue the script...")

    # Save the preset with a supplied name.
    preset_name = "example_preset"
    preset = models.Preset(preset_name=preset_name)
    ReverbClient.save_as_preset("SA", preset)
    # This preset is now saved on the SA and can be used.

    # Show a list of all presets stored on the SA:
    presetList = ReverbClient.get_preset_list("SA")
    print(presetList)

    # the machine should be using the example_preset. Verify this:
    preset = ReverbClient.get_preset("SA")
    print("The currently used preset is: " + preset)

    # Reload the default preset. Subsequent measurements will be performed using default settings.
    ReverbClient.set_default_preset("SA")

    # To load a preset you have saved before, use setPreset:
    preset_name = "example_preset"
    preset = models.Preset(preset_name=preset_name)
    ReverbClient.set_preset("SA", preset)