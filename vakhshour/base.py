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
from twisted.internet import ssl, defer
from twisted.internet.protocol import ClientCreator
from twisted.protocols import amp

from amp import ampy


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
    def __init__(self, host="127.0.0.1", port="8888",
                 secure=False, ssl_key=None, ssl_cert=None,
                 expect_answer=False,
                 *args, **kwargs):

        super(Node, self).__init__(*args, **kwargs)
        self.host = host
        self.port = port
        self.secure = secure
        self.ssl_key = ssl_key
        self.ssl_cert = ssl_cert
        self.expect_answer = expect_answer

    def send_event(self, name, sender, **kwargs):
        proxy = ampy.Proxy(self.host, int(self.port), self.secure,
                           ssl_key=self.ssl_key,
                           ssl_cert = self.ssl_cert).connect()

        if self.expect_answer:
            response = proxy.callRemote(self.Event, name=name,
                                        sender=sender,
                                        kwargs=kwargs)
            responses = {}
            for k, v in response.items():
                responses[k] = v
            return responses
        else:
            proxy.callRemote(self.Event, name=name,
                             sender=sender,
                             kwargs=kwargs)
            return {}

    class Event(ampy.Command):

        class Json(ampy.String):
            """
            Json argument type.
            """
            def toString(self, inObject):
                return str(json.dumps(inObject))

            def fromString(self, inString):
                return json.loads(inString)

        commandName = "Event"

        arguments = [('name', ampy.Unicode()),
                     ('sender', ampy.String()),
                     ("kwargs", Json()),
                     ]

        response = [('status', ampy.Integer())]

        def deserializeResponse(cls, wireResponse):
            return wireResponse
        deserializeResponse = classmethod(deserializeResponse)
