import requests

class Location:

    def __init__(self, tupel, method="GET"):

        key, target = tupel

        self.name = key
        self.url = target["url"]

        # set multi url indicator #
        self.multi_url = False
        if type(self.url) == list:
            self.multi_url = True

        self.user = target.get("user")
        self.args = target.get("args")
        self.password = target.get("pass") or target.get("password")
        self.groups = target.get("groups")
        self.method = method

    def query(self, json=None):

        if self.multi_url:
            urls = self.url
        else:
            urls = [self.url]

        for url in urls:
            print(self.method)
            if self.method == "GET":
                r = requests.get(url, auth=(self.user, self.password), params=self.args)
                r.raise_for_status()
                try:
                    return r.json()
                except requests.exceptions.JSONDecodeError:
                    return { "error" : "Request returned no JSON"}
            elif self.method == "POST":
                r = requests.post(url, auth=(self.user, self.password), json=json)
                r.raise_for_status()
                try:
                    return r.json()
                except requests.exceptions.JSONDecodeError:
                    return { "error" : "Request returned no JSON"}
            else:
                raise NotImplementedError("Method not supported: {}".format(self.method))


class HookOperation:

    def __init__(self, obj, parent):

        self.name = list(obj.keys())[0]
        self.groups = obj[self.name].get("groups")

        self.location_unparsed = obj[self.name].get("location")
        if self.location_unparsed:
            self.location = Location((self.name, self.location_unparsed))
        else:
            self.location = None

        self.passive = obj[self.name].get("passive")
        self.client = obj[self.name].get("client")

        # sanity check #
        if not self.passive and not self.location:
            msg = f"Hook Operation '{self.name}' in '{parent.name}' is not 'passive' but is missing 'location'"
            raise ServiceLoadError(msg)

    def query(self):

        if self.location:
            return self.location.query()
        else:
            raise RuntimeError("Invalid operation 'query' for passive Hook")

    def __str__(self):

        return self.name

class InfoOperations:

    def __init__(self, obj):

        self.groups = obj.get("groups")
        self.endpoints = [InfoEndpoint(e) for e in obj.get("endpoints") or []]
        self.targets = [Location(i) for i in obj.get("targets").items() or []]

    def get_info(self):

        return {
            "endpoints" : [],
            "targets" : [], # TODO [ t.query() for t in self.targets ]
        }


class Service:
    '''Class representing the loaded YAML-service'''
    
    def __init__(self, obj):

        self.info_operations = InfoOperations(obj.get("info_operations"))
        #self.endpoints = Endpoint(obj.get("register_endpoints"))
        self.name = obj.get("name")

        self.hook_operations = []
        for hook_op in obj.get("hook_operations"):
            self.hook_operations.append(HookOperation(hook_op, self))
        print("Hook Operations:", [str(h) for h in self.hook_operations])

    def clean_name(self):
        
        if type(self) == str:
            return self.lower().replace(" ", "")
        return self.name.lower().replace(" ", "")

    def __str__(self):

        return self.name + str(self.hook_operations)

class ServiceLoadError(RuntimeError):

    def __init__(self, message):

        super().__init__(message)