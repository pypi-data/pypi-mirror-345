from antennex_client import *
import time

# Connect to the chamber, verify the door is closed and move the stirrers.

if __name__ == "__main__":

    ## Set up the client

    hostname = hostname_from_file("hostname.txt")
    ReverbClient = create_client("http://" + hostname + ":8080")

    ## Verify the door is closed

    # Retrieve information of the hardware in the equipment. This provides:
    # * Door Status
    # * Motor driver
    # * Hardware ID
    #
    # Note: motor status info can be incorrect on ANTENNEX software version 3.0
    #       and earlier.
    hardware_status = ReverbClient.get_hardware_status()

    door_status = hardware_status.door_switch
    print("The door is: " + door_status, ".")
    assert door_status == "closed", "The door must be closed to operate the stirrers."

    ## Move the stirrers.

    # Move a stirrer by a 15 degree step. For this create a moveStirrer model
    # and pass it to the moveStirrer method.
    stirrer = models.MoveStirrer(
        motorNumber=0,
        mode="angle",
        angle=15,
    )
    code = ReverbClient.move_stirrer(stirrer)
    assert code is None, "Command not accepted."  # assert the command was accepted

    # Move the other stirrer continuously with 10rpm.
    stirrer = models.MoveStirrer(
        motorNumber=1,
        mode="continuous",
        rpm=10,
    )
    code = ReverbClient.move_stirrer(stirrer)
    assert code is None, "Command not accepted."  # assert the command was accepted

    # Show that one motor is rotating.
    hardware_status = ReverbClient.get_hardware_status()
    print("Status of motor 0 is: " + hardware_status.motor_driver.state_motor_0 + ".")
    print("Status of motor 1 is: " + hardware_status.motor_driver.state_motor_1 + ".")
    time.sleep(5)

    # Stop both stirrers.
    stirrer = models.MoveStirrer(motorNumber=0, mode="stop")
    ReverbClient.move_stirrer(stirrer)
    stirrer = models.MoveStirrer(motorNumber=1, mode="stop")
    ReverbClient.move_stirrer(stirrer)
