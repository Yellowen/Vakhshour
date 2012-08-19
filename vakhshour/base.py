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
import hashlib
import logging
from threading import Thread

from OpenSSL import SSL

from argparse import ArgumentParser
from twisted.internet import reactor, ssl, defer
from twisted.internet.protocol import ClientCreator, amp


class VObject(object):
    """
    Vakhshour objects base class.
    """

    logger = logging.getLogger("vakhshour")


class CtxFactory(ssl.ClientContextFactory):

    def __init__(self, key, cert):
        self.key = key
        self.cert = cert

    def getContext(self):
        self.method = SSL.SSLv23_METHOD
        ctx = ssl.ClientContextFactory.getContext(self)
        ctx.use_certificate_file(self.cert)
        ctx.use_privatekey_file(self.key)

        return ctx


class Node(object):
    """
    This Class represent a network node. You should use it to send
    Events.
    """

    def __init__(self, host="127.0.0.1", port="8888",
                 secure=False, ssl_key=None, ssl_cert=None,
                 *args, **kwargs):

        super(Node, self).__init__(*args, **kwargs)
        self.host = host
        self.port = port
        self.secure = secure
        self.ssl_key = ssl_key
        self.ssl_cert = ssl_cert

        self.client = ClientCreator(reactor, amp.AMP)

    def send(self, name, sender, **kwargs):

        from commands import Event
        
        if self.secure:
            connection = self.cllient.connectSSL(self.host,
                                                 int(self.port),
                                                 CtxFactory(self.ssl_key,
                                                            self.ssl_cert))
        else:
            connection = self.client.connectTCP(self.host, int(self.port))

        connection.addCallback(lambda x: x.callRemote(name=name,
                                                      sender=sender,
                                                      kwargs))

        reactor.run()
