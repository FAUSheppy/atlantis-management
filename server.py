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

app = flask.Flask("Atlantis Management")

def parse_xauth_groups():
    '''Parse X-Auth Headers'''
    groups = flask.request.headers.get("X-Forwarded-Groups") or []
    return groups

def _load_services():
    '''Load all service YAML files'''
   
    services_dict = {}
    for fname in os.listdir(SERVICES_DIR):

        with open(os.path.join(SERVICES_DIR, fname)) as f:

            try:
                loaded_yaml = yaml.safe_load(f)
            except ValueError:
                raise e # TODO
    
            try:

                s = services.Service(loaded_yaml)
                s_key = s.clean_name()

                # check valid key #
                if not s_key:
                    raise services.ServiceLoadError(f"Name: {s.name} is not valid ({fname})")
                elif s_key in services_dict:
                    raise services.ServiceLoadError(f"{s_key} already exists ({fname})")

                services_dict.update({ s_key: s })

            except services.ServiceLoadError as e:
                print(e)
                sys.exit(1)
            
    return services_dict
            

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

@app.route("/hook-relay", methods=["POST"])
def hook_relay():
    '''Register passive hooks and relay hooks to endpoints without revealing URLs and passwords'''

    service = flask.request.args.get("service")
    operation = flask.request.args.get("operation")
    groups = parse_xauth_groups()

    print([str(x) for x in app.config["services"]])

    # handle active & passive incoming hooks #
    if services.Service.clean_name(service) in app.config["services"]:
        s = app.config["services"][services.Service.clean_name(service)]
        for hook in s.hook_operations:
            if hook.name == operation:
                if hook.passive:
                    payload = flask.request.json
                    print(payload, bool(payload))
                    if not payload:
                        payload = { "auto": True }
                    app.config["PASSIVE_HOOKS"].update({ s.clean_name() + hook.name : payload })
                    return ("", 204)
                else:
                    return hook.location.query(flask.request.json)

    return ("Operation: {} for service {} not found".format(operation, service), 404)


@app.route("/endpoints", methods=["GET", "POST"])
def info_status_endpoint():

    service = flask.request.args.get("service")
    endpoint = flask.request.args.get("endpoint")
    token = flask.request.args.get("token")

    print([endpoint, service, (token or flask.request.method=="GET")])
    if not all([endpoint, service, (token or flask.request.method=="GET")]):
        return ("Missing endpoint, service or token argument", 400)

    serivce_obj = app.config["services"].get(services.Service.clean_name(service))
    if serivce_obj:
        endpoint_obj = serivce_obj.endpoints.get(endpoint)
        if endpoint_obj:
            if not endpoint_obj.token or (token and endpoint_obj.token == token):
                if flask.request.method == "GET":
                    return endpoint_obj.payload
                elif flask.request.method == "POST":
                    endpoint_obj.payload = flask.request.json                
                    return ("Endpoint Updatet", 200)
                else:
                    return ("Unsupported method", 405)
            else:
                return (f"Service {service} and {endpoint} found, but token invalid or missing", 405)
        else:
            return (f"Service {service} found, but not endpoint {endpoint}", 405)  
    else:
        return (f"Service {service} not found", 405)


@app.route("/hook-passive")
def passive_hook_endpoint():
    '''Endpoint which must not be part of OIDC so it can be accessed by checker scripts'''

    operation = flask.request.args.get("operation")
    service = flask.request.args.get("service")

    if not all([operation, service]):
        return ("Missing operation or service argument", 400)

    # handle incoming checks for passive hooks #
    hook_fullname = service + operation
    print(app.config["PASSIVE_HOOKS"])
    if hook_fullname in app.config["PASSIVE_HOOKS"]:
        payload = app.config["PASSIVE_HOOKS"][hook_fullname]
        app.config["PASSIVE_HOOKS"][hook_fullname] = {}
        return (payload, 200)
    else:
        return (f"No Hook for Service '{service}' and operation '{operation}'", 404)

@app.route("/")
def dashboard():

    user = flask.request.headers.get("X-Forwarded-Preferred-Username")
    groups = parse_xauth_groups()
    ip = flask.request.headers.get("X-Forwarded-For")


    # TODO request status from services
    for s in app.config["services"]:

        # TODO request ip status      #
        # TODO request service status #
        # TODO offer service start    #
        # TODO offer ip unlock        #
        print(s)
        pass

    return flask.render_template("dashboard.html", services=app.config["services"])

def create_app():

    app.config["services"] = _load_services()
    app.config["PASSIVE_HOOKS"] = dict()

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
