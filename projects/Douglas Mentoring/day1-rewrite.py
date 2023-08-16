# Python 3.10 has some nice features, but I only have 3.8 installed.
# Importing __future__ lets us use the features that won't break anything.
# It isn't as good as updating and getting ALL the features, but it's nice to have some.
from __future__ import annotations

import csv
from getpass import getpass
from typing import Any, Dict, List, Tuple

from netmiko import BaseConnection, ConnectHandler, ReadTimeout

DEFAULT_DEVICE_TYPE: str = 'cisco_ios'
DEFAULT_WHID: str = "YEG1"
IF_DETAIL_CMD: str = "sh idprom interface {iface} detail"
HOSTS_FILE = "/home/segattod/segattod-workspace/src/Segattod-package/myproject/Light_level_checks/list.txt"
MIN_LIGHT_LEVEL: float = -10
MODEL_LINE_PREFIX: str = "Vendor Name"
SPEED_LINE_PREFIX: str = "Administrative Speed"

SFP_SPEEDS: Dict[int, str] = {10000: "10G", 1000: "1G"}


def _login() -> Tuple[str, str]:
    # A tuple lets us return two different values at once!  Making this a method means
    # it is easier to change later on if we ever decide to change how we log in.  Maybe
    # we can use SSO or something one day?  That would be cool.
    return input('User Name:'), getpass()


def _get_whid() -> str:
    # You said you wanted to replace that hardcoded string with a user input or something
    # later, now you can just change this here and not mess with your `main` code.  This
    # is called the Interface Design Principle. You can write a dozen different ways to get
    # a WHID and add code here that says "if on the VPN then use SSO; if there is no keyboard
    # then default to "YEG1" otherwise ask the user for input and each of those options can
    # be in their own methods... Once you have this interface class, main doesn't care HOW
    # you get the WHID, as long as this method returns a string.
    return DEFAULT_WHID


def _create_connection(
        _host: str,
        _username: str,
        _password: str,
        # If the user doesn't provide a secret then we will default to using the password below.
        _secret: str | None = None,
        # If the user doesn't provide a device type then use the default.
        _device_type: str = DEFAULT_DEVICE_TYPE,
) -> BaseConnection | None:
    try:
        _connection: BaseConnection = ConnectHandler(
            host=_host,
            device_type=_device_type,
            username=_username,
            password=_password,
            secret=_secret or _password  # If _secret is None then use _password here instead
        )
        _connection.send_command('terminal length 0')
        _connection.enable()
        return _connection

    except ReadTimeout as raised:
        print(f'Failed connection {host}: {raised}')
        return None
    except ValueError as raised:
        print(f'ValueError raised connecting to {host}: {raised}: ')
        return None


def _parse_response_data(conn: BaseConnection, iface: str) -> Tuple[str, str]:
    """I have no way of testing if this will actually work, it's just here as an example."""
    response: str = conn.send_command(IF_DETAIL_CMD.format(iface=iface))

    # Initialize these to blank strings to stat with.
    # Python treats a blank string as False in an if statement.
    model: str = ""
    speed: str = ""
    # For each line in the response:
    for line in response.splitlines():
        # Split at the colon, save the right side, and strip any extra blank spaces.
        line_data: str = line.split(":")[1].rstrip()
        # If the left side startswith something we want, save it.
        if line.startswith(MODEL_LINE_PREFIX):
            model = line_data
        elif line.startswith(SPEED_LINE_PREFIX):
            speed = line_data

        # If we have both values then return them. There is no reason to look at the rest of the lines.
        if model and speed:
            return model, speed

    # If we finished looking at every line and have not found both values, we have a problem.
    raise ValueError(
        f"Provided data did not include model and speed information in the expected format. {response}"
    )


def _get_response_data(conn: BaseConnection, iface: str) -> Tuple[str, str]:
    """
    TECHNICALLY I think it is best practice to call just the base command and
    pull out the data you need from the full response. That is preferred because
    this is making two network calls instead of one. In our case it's trivial,
    but if you were connecting to a service that charged per connection or had
    a max number of connections per hour or something, getting it in one call
    then parsing it would save time and heartache.  It's a good habit to be in.

    See _parse_response_data() above for a suggestion.
    """

    # Take the command from up above and replace the {iface} placeholder:
    base_cmd: str = IF_DETAIL_CMD.format(iface=iface)
    # Then use that to build your two commands.
    model_data: str = conn.send_command(f'{base_cmd} | i Vendor Name')
    speed_data: str = conn.send_command(f'{base_cmd} | i Administrative Speed')

    return model_data, speed_data


def _light_level_check(conn: BaseConnection) -> None:
    transceiver_output: Dict[str, Any] = conn.send_command(
        'show interface transceiver',
        read_timeout=90,
        # I can't actually run this script, so you may need to tinker a little.
        # I suspect you can drop the following line
        use_textfsm=True
    )

    for transceiver in transceiver_output:
        interface: str = transceiver['iface']
        model_data, speed_data = _get_response_data(connection, interface)
        model: str = 'Cisco' if 'CISCO' in model_data.upper() else 'Non-Cisco'
        try:
            speed_as_str: str = speed_data.split(":")[1]
            speed = SFP_SPEEDS[int(speed_as_str)]
        except (ValueError, IndexError):
            # Return "Unknown" if we get an integer we don't recognize or a non-integer value.
            speed = "Unknown"

        pwr: str = transceiver['rx_pwr']
        try:
            state = 'Pass' if float(pwr) >= MIN_LIGHT_LEVEL else 'Fail'
        except ValueError:  # Could not convert to a float
            state = 'No Connection'

        formatted_data.append((host, interface, pwr, state, model, speed))


if __name__ == '__main__':
    username, password = _login()
    formatted_data: List = []
    whid: str = _get_whid()
    output_filename = f"{whid}_output_data.csv"

    print('Beginning Script')
    with open(HOSTS_FILE, 'r') as file:
        for host in file.readlines():
            print(f"Connecting to {host}")
            connection = _create_connection(host, username, password)
            _light_level_check(connection)

    with open(output_filename, "w", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        # Write CSV header.
        csv_writer.writerow(["Host", "interface", "rx_pwr", "result", "SFP Model", "SFP Speed"])
        # Write the data.
        csv_writer.writerows(formatted_data)

    print(f"Data exported to {output_filename}")
