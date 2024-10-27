class Location:

    def __init__(obj, method="GET"):

        assert(len(obj.keys()) == 1)

        self.name = list(obj.keys())[0]
        self.url = obj[self.key]["url"]

        # set multi url indicator #
        self.multi_url = False
        if type(self.url) == list:
            self.multi_url = True

        self.user = obj[self.key]["user"]
        self.args = obj[self.key].get("args")
        self.password = obj[self.key]["pass"] or obj[self.key]["password"]
        self.groups = obj[self.key].get("groups")
        self.method = method

    def query(self, json=None):

        if self.method == "GET":
            r = requests.post(self.url, auth=(self.user, self.password), params=self.args)
            r.raise_for_status()
            return r.json()
        elif self.method == "POST":
            r = requests.post(self.url, auth=(self.user, self.password), json=json)
            r.raise_for_status()
            return r.json()
        else:
            raise NotImplementedError("Method not supported: {}".format(self.method))


class HookOperation:

    def __init__(self, obj):

        assert(len(obj.keys()) == 1)

        self.name = list(obj.keys())[0]
        self.groups = obj.get("groups")

        if "location" in obj:
            self.location = Location(obj["location"])
        else:
            self.location = None

        self.passive = obj.get("passive")

        # sanity check #
        assert(self.passive or self.location)

    def query(self):

        if self.location:
            return self.location.query()
        else:
            raise RuntimeError("Invalid operation 'query' for passive Hook")


class InfoOperation:

    def __init__(self, obj):

        self.groups = obj.get(groups)
        self.endpoints = [InfoEndpoint(e) for e in obj.get("endpoints") or []]
        self.targets = [Location(i) for i in obj.get("targets") or []]

    def get_info(self):

        return {
            "endpoints" : [],
            "targets" : [ t.query() for t in self.targets ]
        }


class Service:
    '''Class representing the loaded YAML-service'''
    
    def __init__(self, obj):

        for hook_op in obj.get("hook_operations"):
            self.hook_operations = HookOperation(hook_op)

        self.info_operations = InfoOperations(obj.get("info_operations"))
        self.endpoints = Endpoint(obj.get("register_endpoints"))
        self.name = obj.get("name")
