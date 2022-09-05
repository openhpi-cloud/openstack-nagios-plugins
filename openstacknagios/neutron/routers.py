# pylint: disable=missing-docstring

#
#    Copyright (C) 2016  Jordan Tardif  http://github.com/jordant
#    Jordan Tardif <jordan@dreamhost.com>
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
"""
Nagios plugin to check router status

Router status is an extended feature provided to neutron via astara
(https://github.com/openstack/astara). This plugin will _NOT_ work for
neutron servers without astara extensions.

This corresponds to the output of 'neutron router-list -c id -c status'.
"""

from argparse import ArgumentParser, Namespace, _ArgumentGroup

from nagiosplugin.check import Check
from nagiosplugin.context import ScalarContext
from nagiosplugin.metric import Metric
from neutronclient.neutron import client

import openstacknagios.openstacknagios as osnag


class NeutronRouters(osnag.Resource):
    """
    Nagios plugin to check router status:

    Checks and reports the number of down/build/active routers.
    """

    def configure(self, check: Check, args: Namespace):
        check.add(
            ScalarContext("active"),
            ScalarContext("down", args.warn, args.critical),
            ScalarContext("build", args.warn_build, args.critical_build),
            osnag.Summary(show=["active", "down", "build"]),
        )

    def probe(self):
        neutron = client.Client("2.0", session=self.session)
        result = neutron.list_routers()

        active = 0
        down = 0
        build = 0

        for router in result["routers"]:
            if router["status"] == "ACTIVE":
                active += 1
            if router["status"] == "DOWN":
                down += 1
            if router["status"] == "BUILD":
                build += 1

        return [
            Metric("active", active, min=0),
            Metric("down", down, min=0),
            Metric("build", build, min=0),
        ]

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

        options.add_argument(
            "--warn-build",
            metavar="RANGE",
            default="0:",
            help='Warning range for BUILD routers (default: "0:")',
        )

        options.add_argument(
            "--critical-build",
            metavar="RANGE",
            default=":10",
            help='Critical range for BUILD routers (default: ":10")',
        )


if __name__ == "__main__":
    osnag.run_check(NeutronRouters)
