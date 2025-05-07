from antennex_client import *

#
# The Wireless Connector keeps data (traces) for acquisitions and calibrations.
# This example retrieves a list of the data that is currently present on the machine.
#

if __name__ == "__main__":

    # Connect to the chamber using an ip address or a hostname. This must be
    # given in the format: "http://{hostname}:8080"
    # Examples:
    # 10.0.2.3:8080
    # localhost:8080
    # For executing the examples, you can edit ../hostname.txt such that all
    # examples use the same address.

    hostname = hostname_from_file("hostname.txt")

    # Create an instance of the API class
    ReverbClient = create_client("http://" + hostname + ":8080")

    # Retrieve overview of all stored measurement data on the RC23
    overview = ReverbClient.get_data_available()

    # Iterate through the various items in the overview. It will print out generic information about
    # this item. Typically, only items that are present are provided.
    # The last (duplicate) .items() is due to how python dict objects work.
    for key, value in overview.items.items():
        if value.available:
            print(f"Data with name '{key}' is available with timestamp {value.timestamp}")
        else:
            print(f"Data with key '{key}' is not present")

    # For how to use the elements, please see the measurement and calibration examples.
