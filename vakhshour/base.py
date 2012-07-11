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

import zmq
import json
import logging

from argparse import ArgumentParser


class VObject(object):
    """
    Vakhshour objects base class.
    """

    logger = logging.getLogger("vakhshour")


class Packet(VObject):
    """
    Base Class For all packets
    """
    _structure = {}

    def __init__(self, data=None):
        if data:
            # TODO: Error handling
            self._structure = json.loads(data)

    def __unicode__(self):
        return json.dumps(self._structure)


class EventPacket(Packet):
    """
    Event Packet
    """
    def __init__(self, data=None, **kwargs):
        if data:
            self._structure = json.loads(data)
        else:
            self._structure = kwargs


class Event():
    """
    This class represent a web event and act as a client for vakhshour.
    You can use this class to send events.
    """

    def __init__(self, name, ip="127.0.0.1", pushport="11111",
                 pullport="11112"):
        self.ip = ip
        self.pushport = pushport
        self.pullport = pullport
        self.push = zmq.Context().socket(zmq.PUSH)
        self.pull= zmq.Context().socket(zmq.PULL)
        self.packet = EventPacket(name=name)

    def send(self):
        self.push.connect("tcp://%s:%s" % (self.ip, self.pushport))
        self.pull.connect("tcp://%s:%s" % (self.ip, self.pullport))
        print "Send Event: %s" % unicode(self.packet)
        self.push.send_unicode(unicode(self.packet))
        result = self.pull.recv()
        if result == "0":
            print "GOOD"
        else:
            print "bad"
