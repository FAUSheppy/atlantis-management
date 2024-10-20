class Location:

    def __init__(obj, method="GET"):

        assert(len(obj.keys()) == 1)

        self.name = list(obj.keys())[0]
        self.url = obj[self.key]["url"]
        self.user = obj[self.key]["user"]
        self.password = obj[self.key]["pass"] or obj[self.key]["password"]
        self.groups = obj[self.key].get("groups")
        self.method = method

    def query(self):

        if self.method == "GET":
            r = requests.post(self.url, auth=(self.user, self.password))
            r.raise_for_status()
            return r.json()
        elif self.method == "POST":
            r = requests.post(self.url, auth=(self.user, self.password))
            r.raise_for_status()
            return r.json()
        else:
            raise NotImplementedError("Method not supported: {}".format(self.method))




class HookOperation:

    def __init__(obj):

        self.name =
        self.groups = obj.get(groups)
        self.locations = [Location(loc_obj) for loc_obj in obj["locations"]]


class InfoOperation:

    def __init__(self, obj):

        self.groups = obj.get(groups)
        self.endpoints = [InfoEndpoint(e) for e in obj.get("endpoints") or []]
        self.targets = [Location(i) for i in obj.get("targets") or []]

    def get_info(self):

        return {
            "endpoints" : []
            "targets" : [ t.query() for t in self.targets ]
        }
                                                                                                    
class Service:
    '''Class representing the loaded YAML-service'''
    
    def __init__(obj):

        self.hook_operations = HookOperation(obj.get("hook_operations"))
        self.info_operations = InfoOperations(obj.get("info_operations"))
        self.endpoints = Endpoint(obj.get("register_endpoints"))
        self.name = obj.get("name")

