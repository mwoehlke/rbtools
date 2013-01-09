from rbtools.api.errors import APIError
from rbtools.commands import Command, Option
from rbtools.utils.process import die

import inspect

INFO = "info"
USER = "users"
ROOT = "self"
REPOSITORY = "repositories"
SESSION = "session"
GROUP = ("groups",)
REVIEW_REQUEST = ("review_requests",)

resource_type = None


def set_resource_type(option, opt_str, value, parser, *args):
    global resource_type
    if resource_type is not None:
        die("Only one resource may be queried at a time")
    resource_type = args[0]
    setattr(parser.values, option.dest, value)


class Info(Command):
    """Read resource attributes from the server."""
    name = "info"
    author = "The Review Board Project"
    args = "<resource-id> [<attribute>]"
    option_list = [
        Option("-r", "--request",
               dest="resource_id", type="string",
               action="callback",
               callback=set_resource_type, callback_args=REVIEW_REQUEST,
               help="retrieve information about the specified review request"),
        Option("--server",
               dest="server",
               metavar="SERVER",
               config_key="REVIEWBOARD_URL",
               default=None,
               help="specify a different Review Board server to use"),
        Option("-d", "--debug",
               action="store_true",
               dest="debug",
               config_key="DEBUG",
               default=False,
               help="display debug output"),
        Option("--username",
               dest="username",
               metavar="USERNAME",
               config_key="USERNAME",
               default=None,
               help="user name to be supplied to the Review Board server"),
        Option("--password",
               dest="password",
               metavar="PASSWORD",
               config_key="PASSWORD",
               default=None,
               help="password to be supplied to the Review Board server"),
    ]

    def main(self, *args):
        """Run the command."""
        resource_id = self.options.resource_id

        global resource_type

        self.repository_info, self.tool = self.initialize_scm_tool()
        server_url = self.get_server_url(self.repository_info, self.tool)
        self.root_resource = self.get_root(server_url)

        try:
            action = "get_%s" % resource_type
            resource_list = getattr(self.root_resource, action)()
            resource = resource_list.get_item(resource_id)
        except APIError, e:
            die("Error getting resource: %s" % (e))

        if len(args) > 0:
            try:
                print getattr(resource, args[0])

            except:
                die("%s resource %s has no such attribute %s." %
                    (resource_type, resource_id, args[0]))

        else:
            print resource  # TODO print available attributes (how?)
