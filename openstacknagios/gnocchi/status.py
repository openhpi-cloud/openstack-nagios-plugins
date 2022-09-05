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
Nagios/Icinga plugin to check gnocchi status

This corresponds to the output of 'gnocchi status'.
"""

from argparse import ArgumentParser, Namespace, _ArgumentGroup

from nagiosplugin.check import Check
from nagiosplugin.context import ScalarContext
from nagiosplugin.metric import Metric
from nagiosplugin.runtime import guarded

import openstacknagios.openstacknagios as osnag
from openstacknagios.gnocchi.gnocchi import Gnocchi


class GnocchiStatus(Gnocchi):
    """
    Determines the status of gnocchi.
    """

    def configure(self, check: Check, args: Namespace):
        super().configure(check, args)

        check.add(
            ScalarContext("measures", args.warn, args.critical),
            ScalarContext("metrics", args.warn_metrics, args.critical_metrics),
            osnag.Summary(show=["measures", "metrics"]),
        )

    def probe(self):
        client = self.get_client()
        result = client.status.get()["storage"]["summary"]

        # {u'storage': {u'summary': {u'metrics': 98, u'measures': 98}}}

        return [
            Metric("measures", result["measures"]),
            Metric("metrics", result["metrics"]),
        ]

    @classmethod
    def setup(cls, options: _ArgumentGroup, parser: ArgumentParser):
        super().setup(options, parser)

        options.add_argument(
            "-w",
            "--warn",
            metavar="RANGE",
            default="0:100",
            help="return warning if number of measures to process is out of range (default: 0:100)",
        )
        options.add_argument(
            "-c",
            "--critical",
            metavar="range",
            default="0:200",
            help="return critical if number of measures to process is out of range (default 0:200)",
        )
        options.add_argument(
            "--warn_metrics",
            metavar="RANGE",
            default="0:100",
            help="return warning if number of metrics having measures to process outside RANGE (default: 0:100)",
        )
        options.add_argument(
            "--critical_metrics",
            metavar="RANGE",
            default="0:200",
            help="return critical if number of metrics having measures to process is outside RANGE (default: 0:200)",
        )


if __name__ == "__main__":
    osnag.run_check(GnocchiStatus)
