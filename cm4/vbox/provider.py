from cm4.abstractclass.CloudManagerABC import CloudManagerABC
from cloudmesh.common.Shell import Shell
import webbrowser
from cloudmesh.common.dotdict import dotdict
import os
import textwrap
from cm4.configuration.config import Config
from pprint import pprint

class VboxProvider (CloudManagerABC):

    #
    # if name is none, take last name from mongo, apply to last started vm
    #

    def start(self, name):
        """
        start a node

        :param name: the unique node name
        :return:  The dict representing the node
        """
        pass


    def stop(self, name=None):
        """
        stops the node with the given name

        :param name:
        :return: The dict representing the node including updated status
        """
        pass


    def info(self, name=None):
        """
        gets the information of a node with a given name

        :param name:
        :return: The dict representing the node including updated status
        """
        pass


    def suspend(self, name=None):
        """
        suspends the node with the given name

        :param name: the name of the node
        :return: The dict representing the node
        """
        # TODO: find last name if name is None
        result = Shell.execute("vagrant", ["suspend", name])
        return result

    def resume(self, name=None):
        """
        resume the named node

        :param name: the name of the node
        :return: the dict of the node
        """
        # TODO: find last name if name is None
        result = Shell.execute("vagrant", ["resume", name])
        return result



    def list(self, verbose=False):
        """
        list all nodes id

        :return: an array of dicts representing the nodes
        """

        def convert(line):
            entry = (' '.join(line.split())).split(' ')
            data = dotdict()
            data.id = entry[0]
            data.name = entry[1]
            data.provider = entry[2]
            data.state = entry[3]
            data.directory = entry[4]
            return data

        result = Shell.execute("vagrant", "global-status --prune")
        if verbose:
            print(result)
        if "There are no active" in result:
            return None

        lines = []
        for line in result.split("\n")[2:]:
            if line == " ":
                break
            else:
                lines.append(convert(line))
        return lines



    def destroy(self, name=None):
        """
        Destroys the node
        :param name: the name of the node
        :return: the dict of the node
        """
        pass

    @classmethod
    def delete(self, name=None):
        # TODO: check

        result = Shell.execute("vagrant",
                               ["destroy", "-f", name],
                               cwd=name)
        return result

    def vagrantfile(cls, **kwargs):

        arg = dotdict(kwargs)

        provision = kwargs.get("script", None)

        if provision is not None:
            arg.provision = 'config.vm.provision "shell", inline: <<-SHELL\n'
            for line in textwrap.dedent(provision).split("\n"):
                if line.strip() != "":
                    arg.provision += 12 * " " + "    " + line + "\n"
            arg.provision += 12 * " " + "  " + "SHELL\n"
        else:
            arg.provision = ""

        # not sure how I2 gets found TODO verify, comment bellow is not enough
        # the 12 is derived from the indentation of Vagrant in the script
        # TODO we may need not just port 80 to forward
        script = textwrap.dedent("""
               Vagrant.configure(2) do |config|

                 config.vm.define "{name}"
                 config.vm.hostname = "{name}"
                 config.vm.box = "{image}"
                 config.vm.box_check_update = true
                 config.vm.network "forwarded_port", guest: 80, host: {port}
                 config.vm.network "private_network", type: "dhcp"

                 # config.vm.network "public_network"
                 # config.vm.synced_folder "../data", "/vagrant_data"
                 config.vm.provider "virtualbox" do |vb|
                    # vb.gui = true
                    vb.memory = "{memory}"
                 end
                 {provision}
               end
           """.format(**arg))

        return script

    def create(self, name=None, image=None, size=None, timeout=360, port=80, **kwargs):
        """
        creates a named node

        :param name: the name of the node
        :param image: the image used
        :param size: the size of the image
        :param timeout: a timeout in seconds that is invoked in case the image does not boot.
               The default is set to 3 minutes.
        :param kwargs: additional arguments passed along at time of boot
        :return:
        """
        """
        create one node
        """
        arg = dotdict(kwargs)
        arg.port = port
        if name is not None:
            arg.name = name
        else:
            # TODO get new name
            pass

        if image is not None:
            arg.image = image
        else:
            # TODO get image from yaml file
            pass

        config = Config()

        """
        vagrant:
              credentials:
                local: True
                hostname: localhost
              cm:
                heading: Vagrant
                host: TBD
                label: TBD
                kind: TBD
                version: TBD
              default:
                path: ~/.cloudmesh/vagrant
                image: ubuntu/bionic/64
        """

        cloud = "vagrant" # must come through parameter or set cloud
        arg.path = config.data["cloudmesh"]["cloud"]["vagrant"]["default"]["path"]
        arg.directory = os.path.expanduser("{path}/{name}".format(**arg))
        arg.vagrantfile = "{directory}/Vagrantfile".format(**arg)

        if not os.path.exists(arg.directory):
            os.makedirs(arg.directory)

        pprint(arg)

        configuration = self.vagrantfile(**arg)

        with open(arg.vagrantfile, 'w') as f:
            f.write(configuration)

    def rename(self, name=None, destination=None):
        """
        rename a node

        :param name: the current name
        :param new_name: the new name
        :return: the dict with the new name
        """
        # if destination is None, increase the name counter and use the new name
        pass

    #
    # Additional methods
    #


    @classmethod
    def find_image(cls, keywords):
        """
        Finds an image on hashicorps web site

        :param keywords: The keywords to narrow down the search
        """
        d = {
            'key': '+'.join(keywords),
            'location': "https://app.vagrantup.com/boxes/search"
        }
        link = "{location}?utf8=%E2%9C%93&sort=downloads&provider=&q=\"{key}\"".format(**d)
        webbrowser.open(link, new=2, autoraise=True)

    @classmethod
    def add_image(cls, name=None):
        result = ""
        if name is None:
            pass
            return "ERROR: please specify an image name"
            # read name form config
        else:
            try:
                # result = Shell.execute("vagrant", ["box", "add", name])
                os.system("vagrant box add {name}".format(name=name))
            except Exception as e:
                print(e)

            return result

    @classmethod
    def delete_image(cls, name=None):
        result = ""
        if name is None:
            pass
            return "ERROR: please specify an image name"
            # read name form config
        else:
            try:
                # result = Shell.execute("vagrant", ["box", "remove", name])
                os.system("vagrant box remove {name}".format(name=name))
            except Exception as e:
                print(e)

            return result
    @classmethod
    def list_images(cls):
        def convert(line):
            line = line.replace("(", "")
            line = line.replace(")", "")
            line = line.replace(",", "")
            entry = line.split(" ")
            data = dotdict()
            data.name = entry[0]
            data.provider = entry[1]
            data.date = entry[2]
            return data

        result = Shell.execute("vagrant", ["box", "list"])

        if "There are no installed boxes" in result:
            return None
        else:
            result = result.split("\n")
        lines = []
        for line in result:
            lines.append(convert(line))

        return lines