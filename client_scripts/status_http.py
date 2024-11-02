import argparse
import subprocess
import yaml
import os
import wakeonlan
import sys
import socket
import struct
import requests
import time

def is_icmp_reachable(host):
    '''Check if host reachable (ICMP)'''

    if " " in host:
        raise AssertionError("hostname must not contain spaces")

    if os.sys.platform.lower()=='win32':
        param = '-n'
        cmd = f"ping {param} 1 {host}"
    else:
        param = '-c'
        cmd = f"ping {param} 1 {host}".split()

    hostname = host
    response = subprocess.run(cmd, capture_output=True)

    return True if response.returncode == 0 else False

def is_up(url):
    '''Check if webservice is reachable'''

    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        return True
    except requests.exceptions.HTTPError:
        return False
    except requests.exceptions.ConnectionError:
        return False

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Atlantis Status Management - Wake on Lan-Action',
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("LAST_STATUS", help="Last Status Submitted")
    parser.add_argument("LAST_STATUS_ISO_TIMESTAMP", help="ISO-Timestamp of last submitted status")

    args = parser.parse_args()

    # determine config file #
    config_file = os.path.basename(__file__) + ".yaml"

    # check file exists
    if not os.path.isfile(config_file):
        print(f"Required config file '{config_file}' does not exist", file=sys.stderr)
        sys.exit(1)

    # load config file #
    config = {}
    try:
        with open(config_file) as f:
            config = yaml.safe_load(f)
    except yaml.scanner.ScannerError as e:
        print(f"Failed to parse '{config_file}': '{str(e)}'", file=sys.stderr)
        sys.exit(1)

    # get parameter #
    target = config.get("target")
    target_webservice = config.get("target_webservice")
    if not target or not target_webservice:
        print(f"Missing required filed 'target' or 'target_webservice' in '{config_file}'", file=sys.stderr)
        sys.exit(1)

    # delay status when neccesary #
    delay_on = config.get("delay_on")
    delay_for = config.get("delay_for") or 15
    if delay_on:
        if any([ x in args.LAST_STATUS for x in delay_on]):
            time.sleep(delay_for)

    # execute action #
    # options:
    #   ping -> server unreachable
    #   http -> server reachable but webservice unavailable
    #   both works -> server reachable/ok
    if not is_icmp_reachable(target):
        print("Server Unreachable$$Ping Failed")
    elif not is_up(target_webservice):
        print("Webservice Down$$Server is up but webservice is not")
    else:
        print("Up$$Started successfully")
