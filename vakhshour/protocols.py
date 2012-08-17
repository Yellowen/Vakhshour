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
import cPickle

from twisted.internet import protocol, reactor

from base import VObject, Event, EventReceived


class EventTransportClient(protocol.Protocol, VObject):
    """
    Event Transport Protocol.

    Main protocol to sending events
    """
    def __init__(self, event):
        self.event = event

    def connectionMade(self):
        try:
            new_data = cPickle.dumps(self.event)
        except:
            raise

        self.transport.write(new_data)

    def dataReceived(self, data):
        """
        This function called when a client send an event to vakhshour.
        """
        try:
            response = cPickle.loads(data)
        except:
            raise

        if response.status == 0:
            self.transport.loseConnection()

            reactor.stop()

        else:
            reactor.stop()
            raise self.EventNotSent(
                "Event Not sent becuase: '%s'" % response.body)

    class EventNotSent(Exception):
        pass


class EventTransportFactoryClient(protocol.ClientFactory):
    """
    Event transport factory. reponsible for received Events.
    """
    protocol = EventTransportClient

    def __init__(self, event):
        self.event = event

    def buildProtocol(self, addr):
        p = self.protocol(self.event)
        return p

    def clientConnectionFailed(self, connector, reason):
        reactor.stop()


class EventTransport(protocol.Protocol, VObject):
    """
    Event Transport Protocol.

    This protocol class is in charge of receiving Events from clients.
    Note: Clients are applications that use Vakhshour as event passing service.
    """
    def __init__(self, sender_factory):
        """
        sender_factory: the Factory object that is responsible for publishing
        events.
        """
        self.sender = sender_factory

    def dataReceived(self, data):
        """
        This function called when a client send an event to vakhshour.
        """
        try:
            obj = cPickle.loads(data)
        except:
            raise

        # Send the received data to publishing
        self.sender.send(data)

        try:
            obj = cPickle.dumps(EventReceived())
        except:
            raise

        self.transport.write(obj)


class EventTransportFactory(protocol.Factory):
    """
    Event transport factory. reponsible for received Events.
    """
    protocol = EventTransport

    def __init__(self, sender_factory):
        self.sender = sender_factory

    def buildProtocol(self, addr):
        p = self.protocol(self.sender)
        return p


class EventPublisher(protocol.Protocol):
    """
    This protocol is in charge of publishing valid events to the
    Vakhshour clients.
    """
    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        """
        Each time a client connect to publisher the EventPublisher
        instance for that client stores in a set object in
        EventPublisherFactory.
        """
        self.factory.clients.add(self)

    def connectionLost(self, reason):
        # Remove each disconnected client from the clients set
        self.factory.clients.remove(self)

    def dataReceived(self, data):
        # EventPublisher did not respone to received data.
        return


class EventPublisherFactory(protocol.Factory, VObject):
    protocol = EventPublisher

    def __init__(self):
        self.clients = set()

    def buildProtocol(self, addr):
        p = self.protocol(self)
        return p

    def send(self, data):
        for c in self.clients:
            self.logger.info("Publish: %s" % data)
            c.transport.write(data)
