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

import json
import logging
import logging.handlers

from argparse import ArgumentParser

from servers import PublisherServer


class Vakhshour(object):
    """
    Vakhshour main class.
    """

    DESC = "Vakhshour - Event and Message layer application"
    FORMAT = '[%(asctime)s] %(module)s - %(lineno)d [%(levelname)s]:  %(message)s'

    def __init__(self):
        self._setup_arguments()
        self._parse_config()
        self._setup_logger()

    def _setup_arguments(self):
        """
        Setup command line parser.
        """
        self.parser = ArgumentParser(
            description=self.DESC)

        self.parser.add_argument("-d", "--debug",
                                 action="store_true",
                                 default=False,
                                 help="Turn on debug mode."
                                 )

        self.parser.add_argument("-c", "--config",
                                 default="/etc/vakhshour/vakhshour.json",
                                 dest="config",
                                 help="Use CONFIG as configuration file."
                                 )

        self.args = self.parser.parse_args()
        return

    def _setup_logger(self):
        """
        Setup logger.
        """

        if self.args.debug:
            level = 0
        else:
            level = self.config.get("log_level", 40)

        logging.basicConfig(format=self.FORMAT,
                            level=level)

        self.logger = logging.getLogger("vakhshour")

        filename = self.config.get("log_file", None)
        if filename:
            hdlr = logging.handlers.RotatingFileHandler(filename,
                                                mode='w+',
                                                maxBytes=10485760,  # 10MB
                                                backupCount=5)
            hdlr.setFormatter(logging.Formatter(self.FORMAT))

        self.logger.addHandler(hdlr)
        return

    def _parse_config(self):
        """
        Parse the json configuration file.
        """
        try:
            fd = open(self.args.config)

        except IOError:
            self.logger.critical("Config file '%s' does not exists." % (
                self.args.config))
            exit(1)

        try:

            self.config = json.load(fd)
        except ValueError:
            fd.close()
            self.logger.critical("Config file '%s' is not a json file." % (
                self.args.config))
            exit(1)

        fd.close()

    def run(self):
        self.logger.info("Hi Vakhshour is here.")

        app = PublisherServer(config=self.config)

        try:
            app.run()
        except KeyboardInterrupt:
            self.logger.info("Bye bye")
