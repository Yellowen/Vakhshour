# -----------------------------------------------------------------------------
#    Vakhshour - Event and Message layer application
#    Copyright (C) 2012 Yellowen
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
# -----------------------------------------------------------------------------

import logging

from argparse import ArgumentParser

from servers import Publisher, Subscriber


class Vakhshour(object):
    """
    Vakhshour main class.
    """

    DESC = "Vakhshour - Event and Message layer application"
    FORMAT = '[%(asctime)s] %(module)s - %(lineno)d [%(levelname)s]:  %(message)s'

    def __init__(self, args):
        self._setup_arguments(args)
        self._setup_logger()

    def _setup_arguments(self, args):
        """
        Setup command line parser.
        """
        self.parser = ArgumentParser(
            description=self.DESC)

        self.parser.add_argument("-M", "--Master",
                            action="store_true",
                            default=False,
                            dest="master",
                            help="Run daemon in Master moode (look at docs)"
                            )

        self.parser.add_argument("-d", "--debug",
                                 action="store_true",
                                 default=False,
                                 help="Turn on debug mode."
                                 )

        self.parser.add_argument("-c", "--config",
                                 default="/etc/vakhshour/vakhshour.conf",
                                 dest="config",
                                 help="Use CONFIG as configuration file."
                                 )

        self.args = self.parser.parse_args()
        return

    def _setup_logger(self):
        """
        Setup logger.
        """
        # TODO: configure logger
        level = 25
        if self.args.debug:
            level = 0

        logging.basicConfig(format=self.FORMAT,
                            level=level)
        self.logger = logging.getLogger("vakhshur")
        return

    def run(self):
        if self.args.master:
            app = Publisher()
        else:
            app = Subscriber()

        app.run()
