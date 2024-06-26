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
Nagios/Icinga plugin to check nova hypervisors

This corresponds to the output of 'nova hypervisor-stats'
"""

from argparse import ArgumentParser, Namespace, _ArgumentGroup

from nagiosplugin.check import Check
from nagiosplugin.context import ScalarContext
from nagiosplugin.metric import Metric
from novaclient.client import Client

import openstacknagios.openstacknagios as osnag


class NovaHypervisors(osnag.Resource):
    def configure(self, check: Check, args: Namespace):
        super().configure(check, args)

        check.add(
            ScalarContext(
                "running_vms",
                args.warn,
                args.critical,
            ),
            ScalarContext(
                "vcpus_used",
                args.warn_vcpus,
                args.critical_vcpus,
            ),
            ScalarContext(
                "vcpus_percent",
                args.warn_vcpus_percent,
                args.critical_vcpus_percent,
            ),
            ScalarContext(
                "memory_used",
                args.warn_memory,
                args.critical_memory,
            ),
            ScalarContext(
                "memory_percent",
                args.warn_memory_percent,
                args.critical_memory_percent,
            ),
            osnag.Summary(
                show=[
                    "memory_used",
                    "memory_percent",
                    "vcpus_used",
                    "vcpus_percent",
                    "running_vms",
                ]
            ),
        )

    def probe(self):
        nova = Client("2.1", session=self.session)

        if self.args.host:
            result = nova.hypervisors.get(
                nova.hypervisors.find(hypervisor_hostname=self.args.host)
            )
        else:
            result = nova.hypervisors.statistics()

        return [
            Metric(
                "vcpus_used",
                result.vcpus_used,
                min=0,
                max=result.vcpus,
            ),
            Metric(
                "vcpus_percent",
                100 * result.vcpus_used / result.vcpus,
                min=0,
                max=100,
            ),
            Metric(
                "memory_used",
                result.memory_mb_used,
                min=0,
                max=result.memory_mb,
            ),
            Metric(
                "memory_percent",
                100 * result.memory_mb_used / result.memory_mb,
                min=0,
                max=100,
            ),
            Metric(
                "running_vms",
                result.running_vms,
                min=0,
            ),
        ]

    @classmethod
    def setup(cls, options: _ArgumentGroup, parser: ArgumentParser):
        super().setup(options, parser)

        options.add_argument(
            "-H",
            "--host",
            default=None,
            help="hostname where the hypervisor is running if not defined (default), summary of all hosts is used",
        )
        options.add_argument(
            "-w",
            "--warn",
            metavar="RANGE",
            default="0:",
            help="return warning if number of running vms is outside RANGE (default: 0:, never warn)",
        )
        options.add_argument(
            "-c",
            "--critical",
            metavar="RANGE",
            default="0:",
            help="return critical if number of running vms is outside RANGE (default 0:, never critical)",
        )
        options.add_argument(
            "--warn-memory",
            metavar="RANGE",
            default="0:",
            help="return warning if used memory is outside RANGE (default: 0:, never warn",
        )
        options.add_argument(
            "--critical-memory",
            metavar="RANGE",
            default="0:",
            help="return critical if used memory is outside RANGE (default: 0:, never critical",
        )
        options.add_argument(
            "--warn-memory-percent",
            metavar="RANGE",
            default="0:90",
            help="return warning if used memory is outside percent RANGE (default: 0:90, warn if 90%% of memory is used",
        )
        options.add_argument(
            "--critical-memory-percent",
            metavar="RANGE",
            default="0:95",
            help="return critical if used memory is outside percent RANGE (default: 0:90, critical if 95%% of memory is used",
        )
        options.add_argument(
            "--warn-vcpus",
            metavar="RANGE",
            default="0:",
            help="return warning if used vcpus is outside RANGE (default: 0:, never warn)",
        )
        options.add_argument(
            "--critical-vcpus",
            metavar="RANGE",
            default="0:",
            help="return critical if used vcpus is outside RANGE (default: 0, always critical if any",
        )
        options.add_argument(
            "--warn-vcpus-percent",
            metavar="RANGE",
            default="0:90",
            help="return warning if used vcpus is outside percent RANGE (default: 0:90, warn if 90%% of vcpus are used)",
        )
        options.add_argument(
            "--critical-vcpus-percent",
            metavar="RANGE",
            default="0:95",
            help="return critical if used vcpus is outside percent RANGE (default: 0:95, critical if 95%% of vcpus are used",
        )


def main():
    osnag.run_check(NovaHypervisors)


if __name__ == "__main__":
    main()
