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
from OpenSSL import SSL

from twisted.internet import reactor, ssl

from base import VObject
from protocols import SubscribeFactory


class CtxFactory(ssl.ClientContextFactory):
    """
    Context factory.
    """
    def __init__(self, key, cert):
        self.key = key
        self.cert = cert

    def getContext(self):
        self.method = SSL.SSLv23_METHOD
        ctx = ssl.ClientContextFactory.getContext(self)
        ctx.use_certificate_file(self.cert)
        ctx.use_privatekey_file(self.key)

        return ctx


class Subscriber(VObject):
    """
    Simplest Subscriber class.
    """

    def __init__(self, host="127.0.0.1", port="7777",
                 secure=False, ssl_key=None, ssl_cert=None):

        self.host = host
        self.secure = secure
        self.port = port
        self.key = ssl_key
        self.cert = ssl_cert
        self.factory = SubscribeFactory()

    def run(self):
        self.logger.info("Connecting to tcp://%s:%s" % (self.host,
                                                        self.port))
        if self.secure:
            self.logger.info("Running on secure mode.")
            reactor.connectSSL(self.host, int(self.port),
                               self.factory,
                               CtxFactory(self.key,
                                          self.cert))
        else:
            self.logger.info("Running on non-secure mode.")
            reactor.connectTCP(self.host,
                               int(self.port),
                               self.factory)
        reactor.run()
