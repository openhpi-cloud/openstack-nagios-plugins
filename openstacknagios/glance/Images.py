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

from glanceclient.v2.client import Client

import openstacknagios.openstacknagios as osnag


class GlanceImages(osnag.Resource):
    """
    Lists glance images and gets timing
    """

    def __init__(self, args=None):
        self.openstack = self.get_openstack_vars(args=args)
        osnag.Resource.__init__(self)

    def probe(self):
        start = time.time()
        try:
            glance = Client(
                "2",
                session=self.get_session,
            )
            glance.images.list()
        except Exception as e:
            self.exit_error(str(e))

        get_time = time.time()

        yield osnag.Metric("gettime", get_time - start, min=0)


@osnag.guarded
def main():
    argp = osnag.ArgumentParser(description=__doc__)

    argp.add_argument(
        "-w",
        "--warn",
        metavar="RANGE",
        default="0:",
        help="return warning if repsonse time is outside RANGE (default: 0:, never warn)",
    )
    argp.add_argument(
        "-c",
        "--critical",
        metavar="RANGE",
        default="0:",
        help="return critical if repsonse time is outside RANGE (default 1:, never critical)",
    )

    args = argp.parse_args()

    check = osnag.Check(
        GlanceImages(args=args),
        osnag.ScalarContext("gettime", args.warn, args.critical),
        osnag.Summary(show=["gettime"]),
    )
    check.main(verbose=args.verbose, timeout=args.timeout)


if __name__ == "__main__":
    main()
