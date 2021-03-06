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

from twisted.protocols.amp import (Integer, String, Unicode,
                                   Command, CommandLocator, AMP)

from base import VObject


class Json(String):
    """
    Json argument type.
    """
    def toString(self, inObject):
        return str(json.dumps(inObject))

    def fromString(self, inString):
        return json.loads(inString)


class Event(Command):
    arguments = [('name', Unicode()),
                 ('sender', String()),
                 ("kwargs", Json())]

    response = [('status', Integer())]
