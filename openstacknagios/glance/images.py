#!/usr/bin/env python3
# pylint: disable=missing-docstring

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
Nagios plugin to check running glance images

This corresponds to the output of 'glance image-list'.
"""

import time
from argparse import ArgumentParser, Namespace, _ArgumentGroup

from glanceclient.v2.client import Client
from nagiosplugin.check import Check
from nagiosplugin.context import ScalarContext
from nagiosplugin.metric import Metric

import openstacknagios.openstacknagios as osnag


class GlanceImages(osnag.Resource):
    """
    Lists glance images and gets timing
    """

    def configure(self, check: Check, args: Namespace):
        super().configure(check, args)

        check.add(
            ScalarContext("gettime", args.warn, args.critical),
            osnag.Summary(show=["gettime"]),
        )

    def probe(self):
        start = time.time()

        glance = Client("2", session=self.session)
        glance.images.list()

        get_time = time.time()

        return Metric("gettime", get_time - start, min=0)

    @classmethod
    def setup(cls, options: _ArgumentGroup, parser: ArgumentParser):
        super().setup(options, parser)

        options.add_argument(
            "-w",
            "--warn",
            metavar="RANGE",
            default="0:",
            help="return warning if repsonse time is outside RANGE (default: 0:, never warn)",
        )
        options.add_argument(
            "-c",
            "--critical",
            metavar="RANGE",
            default="0:",
            help="return critical if repsonse time is outside RANGE (default 1:, never critical)",
        )


def main():
    osnag.run_check(GlanceImages)


if __name__ == "__main__":
    main()
