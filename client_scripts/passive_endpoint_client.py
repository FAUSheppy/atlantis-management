import requests
import sys
import os
import datetime
import argparse
import subprocess

# seperator for title & message in action-/status-script output #
SCRIPT_SEPERATOR = "$$"
QUERY_PATH_SERVER = "/hook-passive"
ENDPOINTS_PATH_SERVER = "/endpoints"

class Status:

    def __init__(self, server, service, operation, action_script, status_endpoint=None, status_script=None, token=None):

        self.server = server
        self.service = service
        self.operation = operation
        self.action_script = action_script
        self.status_endpoint = status_endpoint
        self.status_script = status_script
        self.token = token or ""

        # dynamic #
        self.last_status = ""
        self.timestamp_last_status = datetime.datetime.now()
        self.min_delta_to_last_action = datetime.timedelta(hours=1)
        self.timestamp_last_action = datetime.datetime.now() - self.min_delta_to_last_action

    def _get_params(self):
        '''Get URL Parameters for Server requests'''

        return { "service": self.service, "operation": self.operation, "token": self.token, "endpoint": self.operation }

    def _send_status(self, title, message):
        '''Send a status to the server'''

        payload = {"title": title, "message": message}
        r = requests.post(self.server + ENDPOINTS_PATH_SERVER, json=payload, params=self._get_params())
        r.raise_for_status()
        self.last_status = title + message
        self.timstamp_last_status = datetime.datetime.now()
        print(f"Sent status: {payload}")

    def check_status(self):
        '''Check current status and send it to server'''

        if not self.status_script:
            self._send_status("No Status script for this service", "(but relay is listening)")
            return

        # prepare command #
        cmd = [self.status_script, self.last_status, self.timestamp_last_status.isoformat()]
        if args.action_script.endswith(".py"):
            cmd = ["python"] + cmd

        # execute command #
        p = subprocess.run(cmd, capture_output=True, universal_newlines=True)

        if p.returncode != 0:
            self._send_status("Status script has failed", p.stderr)
        else:
            title, message = p.stdout.split(SCRIPT_SEPERATOR)
            self._send_status(title, message)

    def poll_passive_endpoint(self):
        '''Poll a passive endpoint for status'''

        r = requests.get(self.server +QUERY_PATH_SERVER, params=self._get_params())

        try:
            r.raise_for_status()
            result = r.json()

            if "auto" in result and result["auto"]:

                delta = datetime.datetime.now() - self.timestamp_last_action
                print(delta, self.min_delta_to_last_action)
                if delta >= self.min_delta_to_last_action:

                    # prepare command #
                    cmd = [args.action_script, self.last_status, self.timestamp_last_status.isoformat()]
                    if args.action_script.endswith(".py"):
                        cmd = ["python"] + cmd

                    # execute command #
                    p = subprocess.run(cmd, capture_output=True, universal_newlines=True)
                    if p.returncode != 0:
                        self._send_status("Action script has failed", p.stderr)
                    else:
                        title, message = p.stdout.split(SCRIPT_SEPERATOR)
                        self._send_status(title, message)

                else:

                    title = "Action refused (repeated to fast)"
                    msg = "Wait for {} minutes".format(int(delta.total_seconds()/60))
                    self._send_status(title, msg)
            
            else:
                self.check_status()

        except requests.exceptions.HTTPError as e:
            if r.status_code == 404:
                self.check_status()
                return
            else:
                print(e)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Atlantis Status Management - Mini-Client',
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--server", required=True, help="Status Server to target")
    parser.add_argument("--service", required=True, help="Service to handle with this script")
    parser.add_argument("--operation", required=True, help="Operation to handle with this script")
    parser.add_argument("--status-endpoint", help="Status endpoint to send information to")
    parser.add_argument("--token", help="Token to authenticate with upstream server")
    parser.add_argument("--status-script", help="Script to call for status")
    parser.add_argument("--action-script", required=True, help="Script to call as a action if passive webhook was triggered")
    
    args = parser.parse_args()
    status = Status(args.server, args.service, args.operation, args.action_script, 
                    args.status_endpoint, args.status_script, args.token)
    status.poll_passive_endpoint()
