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
Nagios/Icinga plugin to check keystone

The check will get a token and mesure the time used.
"""

import time
from argparse import ArgumentParser, Namespace, _ArgumentGroup

import keystoneclient.v2_0.client as ksclient2
import keystoneclient.v3.client as ksclient3
from nagiosplugin.check import Check
from nagiosplugin.context import ScalarContext
from nagiosplugin.metric import Metric

import openstacknagios.openstacknagios as osnag


class KeystoneToken(osnag.Resource):
    """
    Nagios/Icinga plugin to check keystone.
    """

    def configure(self, check: Check, args: Namespace):
        super().configure(check, args)

        check.add(
            ScalarContext("gettime", args.warn, args.critical),
            osnag.Summary(show=["gettime"]),
        )

    def probe(self):
        start = time.time()
        if self.args.token_version == "2":
            ksclient2.Client(session=self.session)
        elif self.args.token_version == "3":
            ksclient3.Client(session=self.session)
        else:
            raise ValueError(f"Unknown token-version: {self.args.token_version}")

        get_time = time.time()

        return Metric("gettime", get_time - start, min=0)

    @classmethod
    def setup(cls, options: _ArgumentGroup, parser: ArgumentParser):
        super().setup(options, parser)

        options.add_argument(
            "--tversion",
            metavar="TOKENVERSION",
            default="3",
            help="the version of the keystoneclient to use to verify the token. currently supported is 3 and 2 (default 3)",
        )
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


if __name__ == "__main__":
    osnag.run_check(KeystoneToken)
