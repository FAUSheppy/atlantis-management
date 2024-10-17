#!/usr/bin/python3

import os
import requests
import flask
import argparse
import sys
import json
import datetime
import yaml

class Service:
    '''Class representing the loaded YAML-service'''

    def __init__(path):

        self.

def _ip_unlock(ipv4, ipv6):
    pass
    # unlock ipv4 & ipv6 #
    # detect VPN & local ips #

def _service_start(endpoint, auth):
    pass
    # request service start #

@app.route("/")
def dashboard():

    user = flask.request.headers.get("X-Forwarded-Preferred-Username")
    groups = parse_xauth_groups(flask.request.headers.get("X-Forwarded-Groups"))

    # TODO load services #
    services = []

    # TODO request status from services
    for s in services:
        # TODO request ip status      #
        # TODO request service status #
        # TODO offer service start    #
        # TODO offer ip unlock        #
        pass

    return flask.render_template("dashboard.html", tiles=tiles, categories=categories,
                user=user, groups=groups, flask=flask)

def create_app():
    pass

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='AtlantisStatus Server',
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # general parameters #
    parser.add_argument("-i", "--interface", default="127.0.0.1", help="Interface to listen on")
    parser.add_argument("-p", "--port",      default="5000",      help="Port to listen on")
    args = parser.parse_args()

    # startup #
    with app.app_context():
        create_app()

    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host=args.interface, port=args.port, debug=True)
