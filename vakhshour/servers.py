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

from twisted.internet import reactor

from base import VObject, Event
from protocols import EventTransportFactory, EventPublisherFactory


class PublisherServer(VObject):

    def __init__(self, config={}, host="127.0.0.1", pub_port="7777",
                 recv_port="8888", secure=False,
                 sslkey=None, sslcert=None):

        self.config = config
        self.host = self.config.get("host", host)
        self.pubport = self.config.get("publisher_port", pub_port)
        self.recvport = self.config.get("receiver_port", recv_port)
        self.secure = self.config.get("secure", secure)
        self.key = self.config.get("ssl_key", sslkey)
        self.cert = self.config.get("ssl_cert", sslcert)

        if self.secure:
            pass
        else:
            self.publisher = EventPublisherFactory()
            reactor.listenTCP(int(pub_port), self.publisher)

            self.event_receiver = EventTransportFactory(self.publisher)
            reactor.listenTCP(int(recv_port), self.event_receiver)

    def run(self):
        if self.secure:
            pass
        else:
            self.logger.info("Running in non-secure mode...")
            self.logger.info("Event Publisher URL: tcp://%s:%s" % (
                self.host,
                self.pubport))
            self.logger.info("Event Receiver URL: tcp://%s:%s" % (
                self.host,
                self.recvport))

        reactor.run()
