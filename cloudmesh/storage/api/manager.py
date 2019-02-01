import cloudmesh.storage.provider.gdrive.Provider
import cloudmesh.storage.provider.box.Provider

class Manager(object):

    def __init__(self):
        print("init {name}".format(name=self.__class__.__name__))

    def list(self, parameter):
        print("list", parameter)

    def delete(self, filename):
        print ("delete filename")

    def get(self, service, filename):
        print("get", service, filename)
        if service == "gdrive":
            provider = cloudmesh.storage.provider.gdrive.Provider.Provider()
        elif service == "box":
            provider = cloudmesh.storage.provider.box.Provider.Provider()

        provider.get(filename)
