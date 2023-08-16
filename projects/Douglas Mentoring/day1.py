import getpass
import netmiko
# json was here bc as I'm using textfsm to pull data from cisco devices
# it comes in json i needed to show the output before deciding how to tread the date
import json
import csv

# Where i'm pulling the devices list / Soon I'll make this automated which will pull direct from NARF
file = open(r'/home/segattod/segattod-workspace/src/Segattod-package/myproject/Light_level_checks/list.txt',
            'r')
file = file.read().splitlines()

username = input('User Name:')
password = getpass.getpass()

# Variable for "append" the data later
formatted_data = []

# for now just to name the file / Soon to add for user to add input :)
whid = 'YEG1'


# Function to sorte the data
def light_level_check(connection):
    # Command to checks light level per interface
    transceiver_output = connection.send_command('show interface transceiver', read_timeout=90,
                                                 use_textfsm='~/ntc-templates/ntc_templates/templates/cisco_ios_show_interface_transceiver.textfsm')

    for x in transceiver_output:
        # added both variables below to do a check at that moment based on the "output" for that device interface the loop is going through
        # why? bc was the way i could think to append(look below) all data to export later in CSV
        # basically i use the "entry" information from "x" do all the checks and move to the next, and so on.
        sfpmodel = connection.send_command(f'sh idprom interface {x["iface"]} detail | i Vendor Name')
        sfpspeed = connection.send_command(
            f'sh idprom interface {x["iface"]} detail | i Administrative Speed')

        # Checking if that entry maches with 'cisco'
        if 'CISCO' in sfpmodel.upper():
            sfpM = 'Cisco'
        else:
            sfpM = 'Non-Cisco'
        # Checking if that entry has a match with 10000, then with 1000
        if '10000' in sfpspeed:
            sfpS = '10GB'
        elif '1000' in sfpspeed:
            sfpS = '1GB'
        else:
            sfpS = 'Unknown'
        # checking if the light level for fiber connections are acceptable
        # AND add all that compiled data to "formatted_data"
        ## I know I could have used "return" but when i did it it was not "appending"
        ## it was adding all for one device and erasing and add the new ones, should be simple mistake from my end but i could not figure lol
        if x['rx_pwr'] == 'N/A':
            formatted_data.append((host, x['iface'], x["rx_pwr"], 'No Connection', sfpM, sfpS))
        elif float(x['rx_pwr']) >= -10:
            formatted_data.append((host, x['iface'], x["rx_pwr"], 'Pass', sfpM, sfpS))
        else:
            formatted_data.append((host, x['iface'], x["rx_pwr"], 'Fail', sfpM, sfpS))


# where script "starts", i could have done a __MAIN__ here but didn't get much how it works yet, currently learning this ;P
print('Beginning Script')

# Loop to go over device list linked on the beginning
## I know I can add the connection to a funcion as well, i have it on another script just didn't get to do it as this looks cleaner for me(but i know should be updated)
for host in file:
    print(f'Connecting to {host}')
    try:
        connection = netmiko.ConnectHandler(host=host, device_type='cisco_ios', username=username,
                                            password=password, secret=password)
        connection.send_command('terminal length 0')
        connection.enable()
    except Exception as e:
        print(f'Failed connection {host}: {e}')
        continue
    # call the funcion (and only one lol)
    light_level_check(connection)

# Define CSV file name + WHID
csv_filename = (f"{whid}_output_data.csv")

# Export formatted data to CSV
with open(csv_filename, "w", newline="") as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(
        ["Host", "interface", "rx_pwr", "result", "SFP Model", "SFP Speed"])  # Write CSV header
    csv_writer.writerows(formatted_data)  # Write the data

print(f"Data exported to {csv_filename}")

## I know i could make a main function and invoke others but im still going through it in my learning path lol
## Also should use a more structured start for the script using main or other way.