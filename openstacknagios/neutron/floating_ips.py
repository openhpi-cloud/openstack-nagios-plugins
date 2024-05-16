#!/usr/bin/env python3
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
Nagios/Icinga plugin to check floating IPs

Counts the assigned IPs (= used + unused). This corresponds to the
output of 'neutron floatingip-list'.
"""

from argparse import ArgumentParser, Namespace, _ArgumentGroup

from nagiosplugin.check import Check
from nagiosplugin.context import ScalarContext
from nagiosplugin.metric import Metric
from neutronclient.neutron import client

import openstacknagios.openstacknagios as osnag


class NeutronFloatingIPs(osnag.Resource):
    """
    Determines the number of assigned (used and unused) floating ip's
    """

    def configure(self, check: Check, args: Namespace):
        super().configure(check, args)

        check.add(
            ScalarContext("assigned", args.warn, args.critical),
            ScalarContext("used"),
            osnag.Summary(show=["assigned", "used"]),
        )

    def probe(self):
        neutron = client.Client("2.0", session=self.session)
        result = neutron.list_floatingips()

        assigned = 0
        used = 0

        for floatingip in result["floatingips"]:
            assigned += 1
            if floatingip["fixed_ip_address"]:
                used += 1

        return [
            Metric("assigned", assigned, min=0),
            Metric("used", used, min=0),
        ]

    @classmethod
    def setup(cls, options: _ArgumentGroup, parser: ArgumentParser):
        super().setup(options, parser)

        options.add_argument(
            "-w",
            "--warn",
            metavar="RANGE",
            default="0:200",
            help="return warning if number of assigned floating ip's is outside range (default: 0:200, warn if more than 200 are used)",
        )
        options.add_argument(
            "-c",
            "--critical",
            metavar="RANGE",
            default="0:230",
            help="return critical if number of assigned floating ip's is outside RANGE (default 0:230, critical if more than 230 are used)",
        )


def main():
    osnag.run_check(NeutronFloatingIPs)


if __name__ == "__main__":
    main()
