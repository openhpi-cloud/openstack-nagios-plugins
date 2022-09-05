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
Nagios/Icinga plugin to check rally results

Takes the output of 'rally task results' as input on stdin. and
calculates the sum of load- and full_duration and the number of failed
scenarios.
"""

import json
import sys
from argparse import ArgumentParser, Namespace, _ArgumentGroup

from nagiosplugin.check import Check
from nagiosplugin.context import ScalarContext
from nagiosplugin.metric import Metric
from openstack.config.cloud_region import CloudRegion

import openstacknagios.openstacknagios as osnag


class RallyResults(osnag.Resource):
    def __init__(self, check: Check, args: Namespace, region: CloudRegion) -> None:
        super().__init__(check, args, region)

        if args.resultfile:
            infile = open(args.resultfile, "r", encoding="utf-8")

            with infile:
                try:
                    self.results = json.load(infile)
                except ValueError as err:
                    raise SystemExit(sys.exc_info()[1]) from err
        else:
            self.results = json.load(sys.stdin)

    def configure(self, check: Check, args: Namespace):
        super().configure(check, args)

        check.add(
            ScalarContext("errors", args.warn, args.critical),
            ScalarContext("total", args.warn_total, args.critical_total),
            ScalarContext("slafail", args.warn_slafail, args.critical_slafail),
            ScalarContext("fulldur", args.warn_fulldur, args.critical_fulldur),
            ScalarContext("loaddur", args.warn_loaddur, args.critical_loaddur),
            osnag.Summary(show=["errors", "slafail"]),
        )

    def probe(self):
        full_duration = 0
        load_duration = 0
        total = 0
        errors = 0
        slafail = 0
        for res in self.results:
            total = total + 1
            full_duration = full_duration + res["full_duration"]
            load_duration = load_duration + res["load_duration"]
            for runres in res["result"]:
                if runres["error"] != []:
                    errors = errors + 1

            if "sla" in res:
                for sla in res["sla"]:
                    if not sla["success"]:
                        slafail = slafail + 1

        return [
            Metric("total", total),
            Metric("errors", errors),
            Metric("slafail", slafail),
            Metric("fulldur", full_duration, uom="s"),
            Metric("loaddur", load_duration, uom="s"),
        ]

    @classmethod
    def setup(cls, options: _ArgumentGroup, parser: ArgumentParser):
        super().setup(options, parser)

        parser.add_argument(
            "--resultfile",
            help="file to read results from (output of rally task results) if not specified, stdin is used.",
        )

        parser.add_argument(
            "-w",
            "--warn",
            metavar="RANGE",
            default=":0",
            help="return warning if error counter is outside RANGE (default: :0, warn if any errors)",
        )
        parser.add_argument(
            "-c",
            "--critical",
            metavar="RANGE",
            default=":0",
            help="return critical if error counter is outside RANGE (default :0, critical if any errors)",
        )

        parser.add_argument(
            "--warn_total",
            metavar="RANGE",
            default="0:",
            help="return warning if number of scenarios is outside RANGE (default: 0:, never warn)",
        )
        parser.add_argument(
            "--critical_total",
            metavar="RANGE",
            default="0:",
            help="return critical if number of scenarios is outside RANGE (default: 0:, never critical)",
        )

        parser.add_argument(
            "--warn_slafail",
            metavar="RANGE",
            default=":0",
            help="return warning if number of sla failures is outside RANGE (default: :0, warn if any failures)",
        )
        parser.add_argument(
            "--critical_slafail",
            metavar="RANGE",
            default=":0",
            help="return critical if number of sla failures is outside RANGE (default: :0, critical if any failures)",
        )

        parser.add_argument(
            "--warn_fulldur",
            metavar="RANGE",
            default="0:",
            help="return warning if full_duration is outside RANGE (default: 0:, never warn)",
        )
        parser.add_argument(
            "--critical_fulldur",
            metavar="RANGE",
            default="0:",
            help="return critical if full_duration is outside RANGE (default: 0:, never critical)",
        )

        parser.add_argument(
            "--warn_loaddur",
            metavar="RANGE",
            default="0:",
            help="return warning if load_duration is outside RANGE (default: 0:, never warn)",
        )
        parser.add_argument(
            "--critical_loaddur",
            metavar="RANGE",
            default="0:",
            help="return critical if load_duration is outside RANGE (default: 0:, never critical)",
        )


if __name__ == "__main__":
    osnag.run_check(RallyResults)
