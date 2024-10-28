import requests
import sys
import os
import datetime

# seperator for title & message in action-/status-script output #
SCRIPT_SEPERATOR = "$$"

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

        return { "service": self.service, "operation": self.operation, token=self.token }

    def _send_status(self, title, message):
        '''Send a status to the server'''

        payload = {"title": title, "message": message}
        r = requests.post(self.server, json=payload, params=self._get_params())
        r.raise_for_status()
        self.last_status = title + message
        self.timstamp_last_status = datetime.datetime.now()

    def check_status(self):
        '''Check current status and send it to server'''

        p = subprocess.Popen([self.action_script, self.last_status, self.timestamp_last_status.isoformat()], universal_newlines=True)

        if p.status_code != 0:
            self._send_status("Status script has failed", p.stderr)
        else:
            title, message = p.stdout.split(SCRIPT_SEPERATOR)
            self._send_status(title, message)

    def poll_passive_endpoint(self)
        '''Poll a passive endpoint for status'''

        r = requests.get(server, params=self._get_params())
        r.raise_for_status()
        result = r.json

        if "auto" in result and result["auto"]:
            
            delta = datetime.datetime.now() - self.timestamp_last_action
            if delta < self.min_delta_to_last_action:

                p = subproccess.Popen(args)
                if p.status_code != 0:
                    self._send_status("Action script has failed", p.stderr)
                else:
                    title, message = p.stdout.split(SCRIPT_SEPERATOR)
                    self._send_status(title, message)

            else:

                title = "Action refused (repeated to fast)"
                msg = "Wait for {} minutes".format(int(delta.total_seconds/60))
                self._send_status(title, msg)


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
