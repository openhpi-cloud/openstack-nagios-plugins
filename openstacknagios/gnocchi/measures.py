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

from nagiosplugin.check import Check
from nagiosplugin.context import ScalarContext
from nagiosplugin.metric import Metric
from nagiosplugin.runtime import guarded

import openstacknagios.gnocchi.gnocchi as gnocchi
import openstacknagios.openstacknagios as osnag


class GnocchiMeasures(gnocchi.Gnocchi):
    """
    Determines the amount of measures.
    """

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


@guarded
def main():
    argp = osnag.ArgumentParser(description=__doc__)

    argp.add_argument(
        "-w",
        "--warn",
        metavar="RANGE",
        default="2:",
        help="return warning if number of measures is out of  range (default: 2:)",
    )
    argp.add_argument(
        "-c",
        "--critical",
        metavar="RANGE",
        default="1:",
        help="return critical if number of measures is out of range (default 1:)",
    )

    argp.add_argument(
        "--start",
        metavar="TIMESTAMP",
        default="-1h",
        help="start timestamp to query, default -1h",
    )
    argp.add_argument(
        "--stop",
        metavar="TIMESTAMP",
        default="+0h",
        help="start timestamp to query, default +0h (now)",
    )

    argp.add_argument(
        "--project_id",
        metavar="PROJECT_ID",
        required=True,
        help="project id to query (mandatory, since otherwise query takes too long!)",
    )

    argp.add_argument(
        "--metric", metavar="METRIC", required=True, help="metric to query"
    )

    args = argp.parse_args()

    check = Check(
        GnocchiMeasures(args=args),
        ScalarContext("measures", args.warn, args.critical),
        osnag.Summary(show=["measures"]),
    )
    check.main(verbose=args.verbose, timeout=args.timeout)


if __name__ == "__main__":
    main()
