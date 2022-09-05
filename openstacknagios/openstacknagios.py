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

import sys
from argparse import ArgumentParser as ArgArgumentParser

import openstack
import openstack.connection
from nagiosplugin import Check, Metric
from nagiosplugin import Resource as NagiosResource
from nagiosplugin import ScalarContext
from nagiosplugin import Summary as NagiosSummary
from nagiosplugin import guarded


class Resource(NagiosResource):
    """
    Openstack specific
    """

    @property
    def session(self):
        connection = openstack.connect()
        connection.authorize()
        return connection.session


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


class ArgumentParser(ArgArgumentParser):
    def __init__(self, description, epilog=""):
        ArgArgumentParser.__init__(self, description=description, epilog=epilog)

        self.add_argument(
            "-v",
            "--verbose",
            action="count",
            default=0,
            help="increase output verbosity (use up to 3 times)"
            "(not everywhere implemented)",
        )
        self.add_argument(
            "--timeout",
            type=int,
            default=10,
            help="amount of seconds until execution stops with unknown state (default 10 seconds)",
        )
