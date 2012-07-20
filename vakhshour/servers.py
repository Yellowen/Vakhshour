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
from Queue import Queue
from threading import Thread

import zmq


from base import VObject


class Server(VObject):
    """
    Server Base Class.
    """

    def __init__(self, config):
        self.context = zmq.Context()
        self.config = config

    def _address(self, port, ip=None):
        # TODO: create more flexible config for server address
        # so user can run PULL/PUSH socket on an address and PUB
        # on a different address
        address = self._default_ip
        if ip:
            address = ip

        ip = self.config.get("ip", address)
        return "tcp://%s:%s" % (ip, port)

    def _establish_pull_push(self, push_host=None, pull_host=None):
        # Establish PULL/PULL sockets
        self.pullsocket = self.context.socket(zmq.PULL)
        self.pushsocket = self.context.socket(zmq.PUSH)

        host = pull_host or self._default_ip
        port = self.config.get("pull_port", self._pull_port)
        self.logger.debug("Binding PULL to %s" % self._address(port, host))
        self.pullsocket.bind(self._address(port))

        host = push_host or self._default_ip
        self.logger.debug("Binding PUSH to %s" % self._address(port, host))
        port = self.config.get("push_port", self._push_port)
        self.pushsocket.bind(self._address(port))


class EventPublisher(Server):
    """
    Publisher server. This server will publish events using zmq pub/sub socket.
    """

    _pull_port = "11111"
    _push_port = "11112"
    _pub_port = "11113"
    _default_ip = "127.0.0.1"

    def __init__(self, *args, **kwargs):
        super(EventPublisher, self).__init__(*args, **kwargs)

        self._establish_pull_push()

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
            data = self.pullsocket.recv()
            self.pushsocket.send("0")
            self.logger.info("RECV: %s" % data)
            self.pubsocket.send(data)


class EventSubscriber(Server):
    """
    Subscriber server. this server will receive the event using SUB socket.
    also push the events.
    """
    _sub_port = "11113"
    _pull_port = "22222"
    _push_port = "22223"

    _default_ip = "127.0.0.1"

    # {"event": [("project.event.handler", "project path")]
    _register = {}

    def __init__(self, *args, **kwargs):
        super(EventSubscriber, self).__init__(*args, **kwargs)

        self._establish_pull_push(push_host="127.0.0.1",
                                  pull_host="127.0.0.1")

        self._establish_subscriber()
        self.queue = Queue()

        self.subscriber_thread = Thread(target=self._subscriber_loop)
        self.register_events_thread = Thread(target=self._register_events_loop)

        self.subscriber_thread.daemon = True
        self.register_events_thread.daemon = True

    def _subscriber_loop(self):
        """
        Subscriber thread.
        """
        while True:
            self.logger.debug("Entering event receiveing loop")
            data = self.subsocket.recv()
            self.logger.info("EVENT RECV: %s" % data)
            self.queue.put(data)

    def _register_events_loop(self):
        """
        Event registering thread.
        """
        while True:
            self.logger.debug("Entering event registering loop")
            data = self.pullsocket.recv()
            self.logger.info("PULL RECV: %s" % data)
            self.queue.put(data)

    def run(self):
        """
        Main method that is responsible for server run.
        """
        self.subscriber_thread.start()
        self.logger.info("EventSubscriber is running.")
        self.register_events_thread.start()
        self.logger.info("Event registeration is running.")
        while 1:
            task = self.queue.get()
            print task

    def _establish_subscriber(self):
        """
        Establish publisher socket
        """
        self.subsocket = self.context.socket(zmq.SUB)
        port = self.config.get("sub_port", self._sub_port)
        self.subsocket.connect(self._address(port))
        self.subsocket.setsockopt(zmq.SUBSCRIBE, "")
