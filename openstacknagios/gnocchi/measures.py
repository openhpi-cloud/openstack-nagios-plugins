# pylint: disable=missing-docstring

#
#    Copyright (C) 2020  Cirrax GmbH  https://cirrax.com
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
Nagios/Icinga plugin to check gnocchi gnocchi measures

This will check the amount of available measures for a project and a
metric. Use a canary project to get measures (query for all available
projects take to long !)
"""

from argparse import ArgumentParser, Namespace, _ArgumentGroup

from nagiosplugin.check import Check
from nagiosplugin.context import ScalarContext
from nagiosplugin.metric import Metric

import openstacknagios.gnocchi.gnocchi as gnocchi
import openstacknagios.openstacknagios as osnag


class GnocchiMeasures(gnocchi.Gnocchi):
    """
    Determines the amount of measures.
    """

    def configure(self, check: Check, args: Namespace):
        super().configure(check, args)

        check.add(
            ScalarContext("measures", args.warn, args.critical),
            osnag.Summary(show=["measures"]),
        )

    def probe(self):
        client = self.get_client()
        result = client.status.get()["storage"]["summary"]
        result = client.aggregates.fetch(
            operations=f"(metric {self.args.metric} mean)",
            search=f"project_id={self.args.project_id}",
            start=self.args.start,
            stop=self.args.stop,
        )["measures"]

        count = 0
        for res in result:
            count = count + len(result[res][self.args.metric]["mean"])

        return Metric("measures", count)

    @classmethod
    def setup(cls, options: _ArgumentGroup, parser: ArgumentParser):
        super().setup(options, parser)

        options.add_argument(
            "-w",
            "--warn",
            metavar="RANGE",
            default="2:",
            help="return warning if number of measures is out of  range (default: 2:)",
        )
        options.add_argument(
            "-c",
            "--critical",
            metavar="RANGE",
            default="1:",
            help="return critical if number of measures is out of range (default 1:)",
        )
        options.add_argument(
            "--start",
            metavar="TIMESTAMP",
            default="-1h",
            help="start timestamp to query, default -1h",
        )
        options.add_argument(
            "--stop",
            metavar="TIMESTAMP",
            default="+0h",
            help="start timestamp to query, default +0h (now)",
        )
        options.add_argument(
            "--project_id",
            metavar="PROJECT_ID",
            required=True,
            help="project id to query (mandatory, since otherwise query takes too long!)",
        )
        options.add_argument(
            "--metric", metavar="METRIC", required=True, help="metric to query"
        )


def main():
    osnag.run_check(GnocchiMeasures)


if __name__ == "__main__":
    main()
