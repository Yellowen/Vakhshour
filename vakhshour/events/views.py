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

from django.http import HttpResponse
from django.conf import settings

from base import handlers


def get_events(request):
    """
    Read the incoming event and run its handlers.
    """
    encrypted_data = request.read()

    config = {"encryption": None,
              "private key": None}

    if hasattr(settings, "VAKHSOUR"):
        config = settings.VAKHSOUR

    if not config['encryption']:
        data = json.loads(encrypted_data)
    elif config['encryption'].lower() == "rsa":
        from Crypto.PublicKey import RSA

        key = RSA.importKey(file(config["private key"]).read())
        data = json.loads(key.decrypt(encrypted_data))

    else:
        raise ValueError("'%s' encryption type not supported." % \
                         config["encryption"])

    event = data["name"]
    sender = data["sender"]

    del data["name"]
    del data["sender"]
    handlers.execute_handlers(event,
                              sender,
                              data)
    return HttpResponse("0")
