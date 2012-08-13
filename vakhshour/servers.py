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
import os
import stat
import logging
from Queue import Queue
from threading import Thread

import zmq

from base import VObject, Event


class Server(VObject):
    """
    Server Base Class.
    """

    def __init__(self, config):
        self.context = zmq.Context()
        self.config = config
        self.secure = config.get("secure", None)

    def _address(self, port, ip=None, sock_type="pub"):
        # TODO: create more flexible config for server address
        # so user can run PULL/PUSH socket on an address and PUB
        # on a different address
        if self.secure:
            return "ipc:///tmp/vakhshour.%s" % sock_type

        address = self.config.get("host", self._default_ip)

        if ip:
            address = ip

        ip = self.config.get("ip", address)
        return "tcp://%s:%s" % (ip, port)

    def _establish_pull_push(self, push_host=None, pull_host=None):
        # Establish PULL/PULL sockets
        self.pullsocket = self.context.socket(zmq.PULL)
        self.pushsocket = self.context.socket(zmq.PUSH)

        port = self.config.get("pull_port", self._pull_port)
        self.logger.debug("Binding PULL to %s" % self._address(port, sock_type="pull"))
        self.pullsocket.bind(self._address(port, sock_type="pull"))

        self.logger.debug("Binding PUSH to %s" % self._address(port, sock_type="push"))
        port = self.config.get("push_port", self._push_port)
        self.pushsocket.bind(self._address(port, sock_type="push"))

        if self.secure:
            os.chmod(self._address(port, sock_type="push").split("ipc://")[1],
                     stat.S_IREAD | stat.S_IWRITE)
            os.chmod(self._address(port, sock_type="pull").split("ipc://")[1],
                     stat.S_IREAD | stat.S_IWRITE)


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

        if self.secure:
            os.chmod(self._address(port).split("ipc://")[1],
                     stat.S_IREAD | stat.S_IWRITE)

        self.queue = Queue()

        self.web_clients = self.config.get("web_clients", [])

    def worker(self):
        """
        Get a task from queue and process it.
        """
        while True:
            task = self.queue.get()
            self.process(task)
            self.queue.task_done()

    def process(self, task):
        print "  --- PROCESS ---  "

    def run(self):
        """
        Main method that is responsible for server run.
        """
        for i in xrange(int(self.config.get("workers", 2))):
            worker = Thread(target=self.worker)
            worker.daemon = True
            worker.start()

        self.logger.info("EventPublisher is running.")
        while True:
            self.logger.debug("Entering event loop")
            event = self.pullsocket.recv_pyobj()
            #event = Event(data=data)

            self.pushsocket.send("0")
            self.logger.info("RECV: %s" % event)
            self.pubsocket.send_pyobj(event)


class EventSubscriber(Server):
    """
    Subscriber server. this server will receive the event using SUB socket.
    """
    _sub_port = "11113"

    _default_ip = "127.0.0.1"

    def __init__(self, *args, **kwargs):
        super(EventSubscriber, self).__init__(*args, **kwargs)

        self._establish_subscriber()
        self.queue = Queue()

    def run(self):
        """
        Main method that is responsible for server run.
        """
        while True:
            self.logger.debug("Entering event receiveing loop")
            event = self.subsocket.recv_pyobj()
            self.logger.info("EVENT RECV: %s" % event)
            self.queue.put(event)

    def _establish_subscriber(self):
        """
        Establish publisher socket
        """
        self.subsocket = self.context.socket(zmq.SUB)
        port = self.config.get("sub_port", self._sub_port)

        if self.secure:
            zmq.ssh.tunnel_connection(self.subsocket,
                                      self._address(port),
                                      self._ssh_server(),
                                      keyfile=self.config.get("ssh_key",
                                                              None),
                                      password=self.config.get("ssh_pass",
                                                               None),
                                      timeout=self.config.get("ssh_time_out",
                                                           120))
        else:
            self.subsocket.connect(self._address(port))

        self.subsocket.setsockopt(zmq.SUBSCRIBE, "")

    def _ssh_server(self):
        """
        Return the ssh server url.
        """
        host = self.config.get("host", "127.0.0.1")
        user = self.config.get("ssh_user", "vakhshour")
        ssh_port = self.config.get("ssh_port", "22")
        return "%s@%s:%s" % (user, host, ssh_port)
