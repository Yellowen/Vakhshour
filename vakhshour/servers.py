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


class Server(object):
    """
    Server Base Class.
    """

    def __init__(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(self.soeckt_type)


class Publisher(Server):
    """
    Publisher server. This server will publish events using zmq pub/sub socket.
    """

    socket_type = zmq.PUB

    def run(self):
        pass


class Subscriber(Server):
    """
    Subscriber server. this server will receive the event using SUB socket.
    also push the events.
    """
    socket_type = zmq.PUB

    def run(self):
        pass