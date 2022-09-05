# pylint: disable=missing-docstring

#
#    Copyright (C) 2014  Cirrax GmbH  http://www.cirrax.com
#    Benedikt Trefzer <benedikt.trefzer@cirrax.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import argparse
import re
import sys
from argparse import SUPPRESS, ArgumentParser, Namespace, _ArgumentGroup
from email.policy import default
from pprint import pprint
from typing import Any, Dict, Type

import nagiosplugin
import openstack
import openstack.config.loader
import openstack.connection
from keystoneauth1.session import Session
from nagiosplugin import Check
from nagiosplugin import Resource as NagiosResource
from nagiosplugin import Summary as NagiosSummary
from openstack.config.cloud_region import CloudRegion

from openstacknagios.icinga import generate_command_definition


class Resource(NagiosResource):
    """
    OpenStack Check Resource
    """

    def __init__(self, check: Check, args: Namespace, region: CloudRegion) -> None:
        super().__init__()

        self.args = args
        self.region = region
        self.configure(check, args)

    @property
    def session(self) -> Session:
        connection = openstack.connection.Connection(config=self.region)
        connection.authorize()
        return connection.session

    def configure(self, check: Check, args: Namespace):
        """
        Subclasses shall override this method to extend the nagios check
        object, e.g. to add additional scalars or summary objects.

        Example:

            def prepare(self, check: Check, args: Namespace):
                check.add(
                    ScalarContext("active"),
                    ScalarContext("down", args.warn, args.critical),
                    ScalarContext("build", args.warn_build, args.critical_build),
                    osnag.Summary(show=["active", "down", "build"]),
                )
        """

    @classmethod
    def setup(cls, options: _ArgumentGroup, parser: ArgumentParser):
        """
        Subclasses can override this method to extend the argument
        parser before arguments are parsed.

        Example:

            @classmethod
            def setup(cls, options: _ArgumentGroup, parser: ArgumentParser):
                options.add_argument(
                    "-w",
                    "--warn",
                    metavar="RANGE",
                    default="0:",
                    help='Warning range for DOWN routers (default: "0:")',
                )
                options.add_argument(
                    "-c",
                    "--critical",
                    metavar="RANGE",
                    default=":10",
                    help='Critical range for DOWN routers (default: ":10")',
                )
        """


class Summary(NagiosSummary):
    """Create status line with info"""

    def __init__(self, show):
        super().__init__()
        self.show = show

    def ok(self, results):
        return "[" + " ".join(r + ":" + str(results[r].metric) for r in self.show) + "]"

    def problem(self, results):
        return (
            str(results.first_significant)
            + "["
            + " ".join(r + ":" + str(results[r].metric) for r in self.show)
            + "]"
        )


@nagiosplugin.guarded
def run_check(resource_class: Type[Resource]):
    parser = ArgumentParser(description=resource_class.__doc__)

    parser.add_argument(
        "--print-command-definition",
        action="store_true",
    )

    # Parse once to check if --print-command-definition has been
    # specified. We parse here, to avoid having required arguments added
    # later being required to print the command definition.
    args, _ = parser.parse_known_args()

    # Argument group for check arguments
    options = parser.add_argument_group("Check Options")

    options.add_argument(
        "--check-timeout",
        type=int,
        default=10,
        help="Timeout for total check execution in seconds (default: 10)",
    )

    options.add_argument(
        "--verbose",
        action="count",
        default=0,
        help="Increase output verbosity",
    )

    # Allow resources to add custom options to the argument parser.
    resource_class.setup(options, parser)

    # Set up OpenStack connection session and load config using
    # OpenStacks config framework.
    #
    # This supports configuration via:
    #
    # * Environment variables
    # * Command line arguments
    # * Cloud Profile
    #
    config = openstack.config.loader.OpenStackConfig(
        app_name="openstacknagios",
    )

    # Add OpenStack arguments to our parser
    config.register_argparse_arguments(parser, sys.argv)

    # If --print-command-definition has been parsed above, stop
    # processing and generate an icinga command definition based on all
    # added checks.
    if args.print_command_definition:
        print(generate_command_definition(resource_class, parser))
        sys.exit(0)

    # Finally parse all arguments
    args = parser.parse_args()

    # Load region configuration
    #
    # This region config is given to the check resource, to create a
    # connection/session when needed.
    region = config.get_one(argparse=args)

    check = Check()
    resource = resource_class(check, args, region)
    check.add(resource)
    check.main(verbose=args.verbose, timeout=args.check_timeout)
