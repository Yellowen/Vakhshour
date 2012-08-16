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

from argparse import ArgumentParser
from twisted.internet import reactor


class VObject(object):
    """
    Vakhshour objects base class.
    """

    logger = logging.getLogger("vakhshour")


class Node(Thread):
    """
    This Class represent a network node. You should use it to send
    Events.
    """

    def __init__(self, host="127.0.0.1", port="8888",
                 secure=False, ssl_key=None, *args, **kwargs):

        super(Node, self).__init__(*args, **kwargs)
        self.host = host
        self.port = port
        self.secure = secure
        self.ssl_key = ssl_key

    def send(self, data):
        from protocols import EventTransportFactoryClient

        self.factory = EventTransportFactoryClient(data)

        if self.secure:
            pass
        else:
            reactor.connectTCP(self.host, int(self.port), self.factory)
            reactor.run()


class Event(object):
    """
    Event class. Vakhshour send this object to other nodes.
    """
    def __init__(self, name, sender, **kwargs):

        import datetime

        self.name = name
        self.sender = sender
        self.kwargs = kwargs
        self.create_time = datetime.datetime.now()

    def __unicode__(self):
        return u"'%s' event on '%s' at '%s')" % (self.name,
                                                self.sender,
                                                self.create_time)

    def __str__(self):
        return "'%s' event on '%s' at '%s')" % (self.name,
                                                self.sender,
                                                self.create_time)


class Response(object):
    """
    Response Object.
    """
    def __init__(self, status, body):
        self.status = status
        self.body = body

    def __unicode__(self):
        return u"Reponse: %s: %s" % (self.status,
                                     self.body)

    def __str__(self):
        return "Reponse: %s: %s" % (self.status,
                                     self.body)


class EventReceived(Response):
    """
    This is a response to a successful event registeration.
    """
    def __init__(self):
        body = "0"
        super(EventReceived, self).__init__(status=0,
                                            body=body)
