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

import zmq


class Server(object):
    """
    Server Base Class.
    """

    def __init__(self, config):
        self.context = zmq.Context()
        self.config = config
        self.logger = logging.getLogger("vakhshour")


class EventPublisher(Server):
    """
    Publisher server. This server will publish events using zmq pub/sub socket.
    """

    socket_type = zmq.PUB
    _rep_port = "11111"
    _pub_port = "11112"
    _default_ip = "127.0.0.1"

    def __init__(self, *args, **kwargs):
        super(EventPublisher, self).__init__(*args, **kwargs)

        # TODO: maybe i have to use PUSH/PULL socket instead of rep/req
        # Establish Response socket
        self.repsocket = self.context.socket(zmq.REP)
        port = self.config.get("rep_port", self._rep_port)
        self.logger.debug("Binding REP to %s" % self._address(port))
        self.repsocket.bind(self._address(port))

        # Establish publisher socket
        self.pubsocket = self.context.socket(zmq.PUB)
        port = self.config.get("pub_port", self._pub_port)
        self.pubsocket.bind(self._address(port))

    def run(self):
        """
        Main method that is responsible for server run.
        """
        self.logger.info("EventPublisher is running.")
        while True:
            self.logger.debug("Entering event loop")
            data = self.repsocket.recv()
            self.logger.info("RECV: %s" % data)
            self.pubsocket.send(data)

    def _address(self, port):
        # TODO: create more flexible config for server address
        # so user can run REP/RES socket on an address and PUB
        # on a different address
        ip = self.config.get("ip", self._default_ip)
        return "tcp://%s:%s" % (ip, port)


class EventSubscriber(Server):
    """
    Subscriber server. this server will receive the event using SUB socket.
    also push the events.
    """
    socket_type = zmq.PUB

    def run(self):
        pass
