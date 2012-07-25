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
import hashlib
import logging

from argparse import ArgumentParser


class VObject(object):
    """
    Vakhshour objects base class.
    """

    logger = logging.getLogger("vakhshour")


class Packet(object):

    _data = {"data": None,
             "hash": None}

    def __init__(self, data):
        if isinstance(data, basestring):
            self._data = json.loads(data)
        else:
            self._data["data"] = data

    def _gen_hash(self, key):
        m = hashlib.sha1()
        m.update(unicode(self._data["data"]) + key)
        return m.hexdigest()

    def sign(self, key):
        """
        Sign a packet and add the corresponding checksum.
        """
        self._data["hash"] = self._gen_hash(key)
        return self._data["hash"]

    def is_valid(self, key):
        hash_ = self._gen_hash(key)
        if self._data["hash"] == hash_:
            return True
        else:
            return False

    def __unicode__(self):
        return json.dumps(self._data)

    def __str__(self):
        return self.__unicode__()

    def __getattr__(self, name):
        if name in self._data["data"]:
            return self._data["data"][name]
        else:
            raise AttributeError(
                "'Packet' object has no attribute '%s'" % name)

    def __setattr__(self, name, value):
        self._data[name] = value


class Event(Packet):
    """
    This class represent a web event and act as a client for vakhshour.
    You can use this class to send events.
    """

    def __init__(self, name=None, sender=None,
                 data=None, **kwargs):
        if data:
            super(Event, self).__init__(data)
        else:
            a = {"name": name,
                 "params": kwargs,
                 "sender": sender,
                 }
            super(Event, self).__init__(a)


class Node(object):
    """
    This Class represent a network node. You should use it to send
    Events.
    """

    def __init__(self, ip="127.0.0.1", pushport="11111", pullport="11112"):
        self.push = zmq.Context().socket(zmq.PUSH)
        self.pull = zmq.Context().socket(zmq.PULL)

        self.ip = ip
        self.pushport = pushport
        self.pullport = pullport

    def send(self, data):
        self.push.connect("tcp://%s:%s" % (self.ip, self.pushport))
        self.pull.connect("tcp://%s:%s" % (self.ip, self.pullport))

        print "Send Event: %s" % unicode(data)
        self.push.send_unicode(unicode(data))
        print "1"
        response = self.pull.recv()
        return int(response)
