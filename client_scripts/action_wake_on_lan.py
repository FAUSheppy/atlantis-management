import argparse
import subprocess
import yaml
import os
import wakeonlan
import sys

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Atlantis Status Management - Wake on Lan-Action',
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("LAST_STATUS", required=True, help="Last Status Submitted")
    parser.add_argument("LAST_STATUS_ISO_TIMESTAMP", required=True, help="ISO-Timestamp of last submitted status")

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
    if not target:
        print(f"Missing required filed 'target' in '{config_file}'", file=sys.stderr)
        sys.exit(1)

    # execute action #
    wakeonlan.send_magic_packet(target)
    print("Wake signal sent$$Waiting for status information")