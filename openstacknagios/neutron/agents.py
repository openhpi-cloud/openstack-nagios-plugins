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

"""
Nagios/Icinga plugin to check running neutron agents

This corresponds to the output of 'neutron agent-list'.
"""

from argparse import ArgumentParser, Namespace, _ArgumentGroup

from nagiosplugin.check import Check
from nagiosplugin.context import ScalarContext
from nagiosplugin.metric import Metric
from neutronclient.neutron import client
from openstack.config.cloud_region import CloudRegion

import openstacknagios.openstacknagios as osnag


class NeutronAgents(osnag.Resource):
    """
    Determines the status of the neutron agents.
    """

    def __init__(self, check: Check, args: Namespace, region: CloudRegion) -> None:
        super().__init__(check, args, region)
        self.binary = args.binary
        self.host = args.host

    def configure(self, check: Check, args: Namespace):
        super().configure(check, args)

        check.add(
            ScalarContext("up", args.warn, args.critical),
            ScalarContext("disabled", args.warn_disabled, args.critical_disabled),
            ScalarContext("down", args.warn_down, args.critical_down),
            ScalarContext("total", "0:", "@0"),
            osnag.Summary(show=["up", "disabled", "down"]),
        )

    def probe(self):
        neutron = client.Client("2.0", session=self.session)

        if self.host and self.binary:
            result = neutron.list_agents(host=self.host, binary=self.binary)
        elif self.binary:
            result = neutron.list_agents(binary=self.binary)
        elif self.host:
            result = neutron.list_agents(host=self.host)
        else:
            result = neutron.list_agents()

        agents_up = 0
        agents_disabled = 0
        agents_down = 0
        agents_total = 0

        for agent in result["agents"]:
            agents_total += 1
            if agent["admin_state_up"] and agent["alive"]:
                agents_up += 1
            elif not agent["admin_state_up"]:
                agents_disabled += 1
            else:
                agents_down += 1

        return [
            Metric("up", agents_up, min=0),
            Metric("disabled", agents_disabled, min=0),
            Metric("down", agents_down, min=0),
            Metric("total", agents_total, min=0),
        ]

    @classmethod
    def setup(cls, options: _ArgumentGroup, parser: ArgumentParser):
        super().setup(options, parser)

        options.add_argument(
            "-w",
            "--warn",
            metavar="RANGE",
            default="0:",
            help="return warning if number of up agents is outside RANGE (default: 0:, never warn)",
        )
        options.add_argument(
            "-c",
            "--critical",
            metavar="RANGE",
            default="0:",
            help="return critical if number of up agents is outside RANGE (default 1:, never critical)",
        )
        options.add_argument(
            "--warn_disabled",
            metavar="RANGE",
            default="@1:",
            help="return warning if number of disabled agents is outside RANGE (default: @1:, warn if any disabled agents)",
        )
        options.add_argument(
            "--critical_disabled",
            metavar="RANGE",
            default="0:",
            help="return critical if number of disabled agents is outside RANGE (default: 0:, never critical)",
        )
        options.add_argument(
            "--warn_down",
            metavar="RANGE",
            default="0:",
            help="return warning if number of down agents is outside RANGE (default: 0:, never warn)",
        )
        options.add_argument(
            "--critical_down",
            metavar="RANGE",
            default="0",
            help="return critical if number of down agents is outside RANGE (default: 0, always critical if any)",
        )
        options.add_argument(
            "--binary",
            dest="binary",
            default="",
            help="filter agent binary",
        )
        options.add_argument(
            "--host",
            dest="host",
            default="",
            help="filter hostname",
        )


if __name__ == "__main__":
    osnag.run_check(NeutronAgents)
