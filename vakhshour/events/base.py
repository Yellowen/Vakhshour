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


class EventHandler(object):
    pass


class Handlers(object):
    _register = {}

    def register(self, handler):
        if handler.__class__.__name__ in self._register:
            pass
        else:
            self._register[handler.__class__.__name__] = handler

    def execute_handlers(self, event, sender, kwargs):
        for handler in self._register:
            if hasattr(self._register[handler], "on_%s" % event):
                method = getattr(self._register[handler], "on_%s" % event)
                method(sender, **kwargs)


handlers = Handlers()
