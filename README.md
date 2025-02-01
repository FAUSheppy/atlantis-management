# Server Interface
## Setup up with Docker Compose
First setup the server component with a docker-compose file. The Server is configured via `yaml` files in the `/app/services`-directory, which you should map out as a volume.

    services:
      atlantis-relay-server:
        ports:
            - 5000:5000
        volumes:
            - /data/atlantis-relay-server/services:/app/services
        image: harbor-registry.atlantishq.de/atlantishq/atlantis-status:latest
        restart: always

If you want OIDC (which you should), append this to your `docker-compose.yaml` with your appropriate values:

    oauth2-proxy-atlantis-status:
        image: bitnami/oauth2-proxy:latest
        depends_on:
          - redis
        restart: always
        command:
          - --skip-auth-route
          - /endpoints
          - --skip-auth-route
          - /hook-passive
          - --http-address
          - 0.0.0.0:5026
        ports:
          - 5026:5026
        environment:
          OAUTH2_PROXY_SCOPE: openid email profile
          OAUTH2_PROXY_UPSTREAMS: http://CONTAINER_ADDRESS
          OAUTH2_PROXY_EMAIL_DOMAINS: '*' 
          OAUTH2_PROXY_PROVIDER: keycloak-oidc
          OAUTH2_PROXY_PROVIDER_DISPLAY_NAME: "AtlantisHQ Accounts"
          OAUTH2_PROXY_REDIRECT_URL: "https://actions.atlantishq.de/oauth2/callback"
          OAUTH2_PROXY_OIDC_ISSUER_URL: "https://keycloak.atlantishq.de/realms/master"
          OAUTH2_PROXY_CLIENT_ID: "atlantis-status"
          OAUTH2_PROXY_CLIENT_SECRET: ""

          OAUTH2_PROXY_OIDC_EMAIL_CLAIM: sub 
          OAUTH2_PROXY_SET_XAUTHREQUEST: "true"

          OAUTH2_PROXY_SESSION_STORE_TYPE: redis
          OAUTH2_PROXY_REDIS_CONNECTION_URL: redis://redis

          OAUTH2_PROXY_COOKIE_REFRESH: 17m 
          OAUTH2_PROXY_COOKIE_NAME: SESSION
          OAUTH2_PROXY_COOKIE_SECRET: ""

          OAUTH2_PROXY_REVERSE_PROXY: "true"
          OAUTH2_PROXY_SKIP_PROVIDER_BUTTON: "true"

          OAUTH2_PROXY_WHITELIST_DOMAIN: "keycloak.atlantishq.de

      redis:
        image: redis:latest
        restart: always
        
## Configuration
You can have two different types of `hook_operations`, **active** and **passive**:

- A passive operation, requires a service in *hook_operations* and a endpoint in *register_endpoint*. One the service has been clicked. The server will provide this information at the give endpoint.
- A active operation will call one or multiple URLs, if the endpoint requires the client itself to call it (e.g. because it needs the client IP, set `client: true`). If the endpoint is protected, and you do not want to leak a permanent secret to the client, you can use the `client_secret` field to generate a one-time-secret (if your application support this).

**Example:**

    name: Atlantis Array
    hook_operations:
        - start_service:
            passive: true
        - unlock_service:
            location:
                url:
                   - https://ipv4-vpn-activate.atlantishq.de:10443/activate
                   - https://ipv6-vpn-activate.atlantishq.de:10443/activate
                client_secret: https://ipv4-vpn-activate.atlantishq.de:10443/one-time-token
                client_secret_field: "secret"
                args:
                    secret: "BACKEND_SECRET_NOT_LEAKED_TO_CLIENT"
            status_url: https://vpn-activate.atlantishq.de:10443/am-i-unlocked
            client: true

    register_endpoints:
        - start_service:
            token: <YOUR_RELAY_SECRET>

    groups:
        - admin

You can configure groups for the entire section, in the above example, only the *admin*-group can use the services of the group *"Atlantis Array"*. A name is required for every file. You can have infinite files, but enpoints are not currently checked for duplications across files.

The `unlock_service` you see here is the [Atlantis IP Gate](https://github.com/FAUSheppy/atlantis-ip-gate).

# Setting up Relay
## Initial Setup
Clone the Repository to your local relay, which is in the same physical subnet as your offline server (i.e. a Pine64 or Raspi in your home), see the `client_scripts`-directory. The python scripts in this directory are configured by identically named `.yaml` files.

    # action_wake_on_lan.py.yaml 
    target: <MAC_OF_TARGET_INTERFACE (get this with ip a on target)>

    # status_http.py.yaml
    target: <IP_OF_TARGET>
    target_webservice: http://<URL_OF_WEBSERVICE>
    delay_on:
        - "Wake"
    delay_for: 20
    
Do not change the `delay_on` parameter for now, changing it is not implemented yet.

## Starting with SystemD
**Unit:**

    [Unit]
    Description=Run Actions and Status Script

    [Service]
    Type=oneshot
    WorkingDirectory=/PATH_TO/atlantis-status/client_scripts/
    ExecStart=/usr/bin/python passive_endpoint_client.py \
        --server https://ACTIONS_URL \
        --service atlantisarray \
        --operation start_service \
        --status-endpoint NONE \
        --token TOKEN \
        --action-script ./action_wake_on_lan.py \
        --status-script ./status_http.py

**Timer:**

    # /etc/systemd/system/atlantis-array-actions.timer
    [Unit]
    Description=Run Atlantis Status Script every 10 seconds

    [Timer]
    OnBootSec=60s
    OnUnitActiveSec=10s

    [Install]
    WantedBy=timers.target
