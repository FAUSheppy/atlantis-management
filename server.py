#!/usr/bin/python3

import os
import requests
import flask
import argparse
import sys
import json
import datetime
import yaml
import services

SERVICES_DIR = "services"

def _load_services():
    '''Load all service YAML files'''
   
    services = []
    for fname in os.path.listdir(SERVICES_DIR):

        with open(os.path.join(SERVICES_DIR, fname)) as f:

            try:
                loaded_yaml = yaml.load(f)
            except ValueError:
                raise e # TODO
    
            services.append(services.Service(loaded_yaml))
            
    return services
            

def webhook(target, payload, auth):
    pass

    r = requests.post(target, json=payload, auth=auth)
    try:
        r.raise_for_status()
    except ValueError:
        return { "error" : r.content }

    return { "msg" : r.content }

def register_service_location(location, payload, auth):
    pass
    # request service start #

@app.route("/hook-relay")
def service(path):

    service = flask.request.args.get("service")
    operation = flask.request.args.get("operation")
    groups = parse_xauth_groups(flask.request.headers.get("X-Forwarded-Groups"))

    for s in app.config["services"]:

        if s.name == service:

            for hook in s.hook_operations:

                if hook.name == operation:

                    return hook.location.query()

    return ("Operation: {} for service {} not found".format(operation, service))

@app.route("/")
def dashboard():

    user = flask.request.headers.get("X-Forwarded-Preferred-Username")
    groups = parse_xauth_groups(flask.request.headers.get("X-Forwarded-Groups"))
    ip = flask.request.headers.get("X-Forwarded-For")


    # TODO request status from services
    for s in app.config["services"]:

        # TODO request ip status      #
        # TODO request service status #
        # TODO offer service start    #
        # TODO offer ip unlock        #
        pass

    return flask.render_template("dashboard.html", tiles=tiles, categories=categories,
                user=user, groups=groups, flask=flask)

def create_app():

    app.config["Services"] = _load_services()

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
