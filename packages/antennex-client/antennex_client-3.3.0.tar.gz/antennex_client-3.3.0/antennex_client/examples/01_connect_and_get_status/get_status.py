from antennex_client import *

#
# This example returns basic information of The Wireless Connector
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

    # Run the getVersion method. All functions return the output value, an HTTP code, and the full HTTP response.
    response = ReverbClient.get_version()
    print("version = " + response)

    # Run the getChamberStatus method. Only specify one output value, ignore the http code and the full http response.
    response = ReverbClient.get_chamber_status()
    print("status = " + response.status.value)

    # The response contains a machineState object (models.MachineState).
    # We can convert this to a string using the status property.
    response = ReverbClient.get_chamber_status_with_http_info()
    print("HTTP status code: " + str(response.status_code))
