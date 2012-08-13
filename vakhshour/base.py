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


## class Event(Packet):
##     """
##     This class represent a web event and act as a client for vakhshour.
##     You can use this class to send events.
##     """

##     def __init__(self, name=None, sender=None,
##                  data=None, **kwargs):
##         if data:
##             super(Event, self).__init__(data)
##         else:
##             a = {"name": name,
##                  "params": kwargs,
##                  "sender": sender,
##                  }
##             super(Event, self).__init__(a)


class Node(object):
    """
    This Class represent a network node. You should use it to send
    Events.
    """

    def __init__(self, host="127.0.0.1", pushport="11111", pullport="11112",
                 secure=False, ssh_user="vakhshour", timeout=120,
                 ssh_key=None, ssh_pass=None, ssh_port="22"):

        self.push = zmq.Context().socket(zmq.PUSH)
        self.pull = zmq.Context().socket(zmq.PULL)

        self.host = host
        self.pushport = pushport
        self.pullport = pullport
        self.secure = secure

        self.ssh_user = ssh_user
        self.ssh_pass = ssh_pass
        self.ssh_port = ssh_port
        self.ssh_key = ssh_key
        self.timeout = timeout

        if secure:
            self.push_url = "ipc:///tmp/vakhshour.push"
            self.pull_url = "ipc:///tmp/vakhshour.pull"
        else:
            self.push_url = "tcp://%s:%s" % (host, pushport)
            self.pull_url = "tcp://%s:%s" % (host, pullport)

    def send(self, data):
        if self.secure:
            zmq.ssh.tunnel_connection(self.push,
                                      self.push_url,
                                      "%s@%s:%s" % (self.ssh_user,
                                                    self.host,
                                                    self.ssh_port),
                                      keyfile=self.ssh_key,
                                      password=self.ssh_pass,
                                      timeout=self.timeout)
            zmq.ssh.tunnel_connection(self.pull,
                                      self.pull_url,
                                      "%s@%s:%s" % (self.ssh_user,
                                                    self.host,
                                                    self.ssh_port),
                                      keyfile=self.ssh_key,
                                      password=self.ssh_pass,
                                      timeout=self.timeout)
        else:
            self.push.connect("tcp://%s:%s" % (self.host, self.pushport))
            self.pull.connect("tcp://%s:%s" % (self.host, self.pullport))

        print "Send Event: %s" % unicode(data)
        self.push.send_pyobj(data)
        print "1"
        response = self.pull.recv_pyobj()
        return response


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
