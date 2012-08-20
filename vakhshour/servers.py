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
from OpenSSL import SSL

from twisted.internet import reactor, ssl

from base import VObject
from protocols import EventPublisherFactory, EventFactory


class SSLFactory(ssl.DefaultOpenSSLContextFactory, VObject):

    cacert = None

    def getContext(self):

        x = self._context

        x.set_verify(
            SSL.VERIFY_PEER | SSL.VERIFY_FAIL_IF_NO_PEER_CERT,
            self.verify_cert,
            )

        # Since we have self-signed certs we have to explicitly
        # tell the server to trust them.
        x.load_verify_locations(self.cacert)
        return x

    def verify_cert(self, connection, x509, errnum, errdepth, ok):
        if not ok:
            self.logger.error(
                'invalid cert from subject: %s' % x509.get_subject())
            return False
        else:
            self.logger.info("Cert is fine.")
            return True


class PublisherServer(VObject):

    def __init__(self, config={}, host="127.0.0.1", pub_port="7777",
                 recv_port="8888", secure=False,
                 sslkey=None, sslcert=None, cacert=None):

        self.config = config
        self.host = self.config.get("host", host)
        self.pubport = self.config.get("publisher_port", pub_port)
        self.recvport = self.config.get("receiver_port", recv_port)
        self.secure = self.config.get("secure", secure)
        self.key = self.config.get("ssl_key", sslkey)
        self.cert = self.config.get("ssl_cert", sslcert)
        self.cacert = self.config.get("ca_cert", cacert)
        self.webapps = self.config.get("webapps", [])

        self.publisher = EventPublisherFactory(self.webapps)
        self.event_receiver = EventFactory(self.publisher)

        if self.secure:

            self.logger.info("SSL KEY: %s" % self.key)
            self.logger.info("SSL CERT: %s" % self.cert)
            self.logger.info("CA CERT: %s" % self.cacert)

            context_factory = SSLFactory(self.key,
                                         self.cert)
            context_factory.cacert = self.cacert

            reactor.listenSSL(
                int(self.recvport),
                self.event_receiver,
                context_factory)

            reactor.listenSSL(
                int(self.pubport),
                self.publisher,
                context_factory)
        else:
            reactor.listenTCP(int(self.pubport),
                              self.publisher)
            reactor.listenTCP(int(self.recvport),
                              self.event_receiver)

    def run(self):
        if self.secure:
            self.logger.info("Running in secure mode...")
        else:
            self.logger.info("Running in non-secure mode...")

        self.logger.info("Event Publisher URL: tcp://%s:%s" % (
            self.host,
            self.pubport))
        self.logger.info("Event Receiver URL: tcp://%s:%s" % (
            self.host,
            self.recvport))

        reactor.run()
