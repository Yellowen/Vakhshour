.. _quick guide:

Quick Start
===========
In this guide you will learn how to use Vakhshour event passing platform as fast as possible.

Vakhshour Installation
----------------------
Installing **Vakhshour** is easy, but before installing **Vakhshour** you have to install its dependencies.
**Vakhshour** have three dependencies that you can install them using ``pip`` or ``easy_install`` utilities.

Install dependencies just like this::

   # easy_install twisted pyopenssl pycrypto

or::

   # pip install twisted pyopenssl pycrypto

Now its time to install **Vakhshour** itself::

   # easy_install vakhshour

or::

   # pip install vakhshour

Of course you can install dependecies using your distribution package manager.

.. note:: Some of **Vakhshour** dependencies have their own dependencies that you should take care of.


Running Vakhshour daemon
------------------------
For using **Vakhshour** you need to run its daemon first (daemon is not a good word for this). **Vakhshour** daemon
is responsible for dispatching events. ``vakhshourd`` is the **Vakhshour** daemon. run it like::

   $ /usr/local/bin/vakhshourd 

``vakhshourd`` use ``/etc/vakhshour/vakhshour.json`` as its default configuration file. you can force ``vakhshourd``
to use another configuration file with ``-c`` parameter and specify new configuration file path.

.. note:: For more information about ``vakhshourd`` parameters take a look at ``vakhshourd --help``

.. note:: You should us ``vakhshourd`` with some utitlies like ``Systemd`` or ``upstart`` or etc. if you're a Debian user, there is a init script.


Sending events
--------------
After running the daemon, events can be sent using ``Node`` class. it lives in ``vakhshour.base.Node``. ``Node`` represent a network node that running the **Vakhshour** daemon.
For example::

    from vakhshour.base import Node

    node = Node(host="10.1.1.1", port="8888")
    result = node.send_event(name="foo", sender="me", first_param="bar", another_param=12)

also you can send events in secure mode (using SSL)::

    from vakhshour.base import Node

    node = Node(ssl_key="/home/lxsameer/src/Vakhshour/keys/test.key",
                ssl_cert="/home/lxsameer/src/Vakhshour/keys/test.crt",
		secure=True)
    result = node.send_event(name="foo", sender="me", first_param="bar", another_param=12)


First example will send a ``foo`` event with two parameter that called ``first_param`` and ``another_param`` to 
a **Vakhshour** server on ``10.1.1.1:8888``. Those parameters that send to server will pas to event handler.

Second example is the same as first one but send the event in secure mode using SSL transport. SSL transport use 
SSLv3 client authentication to authenticate the client. More information on `SSLv3 Client Authentication <http://en.wikipedia.org/wiki/Transport_Layer_Security#Client-authenticated_TLS_handshake>`_.

Receving events
---------------
**Vakhshour** service publish events by sending them via a TCP socket. Each client can subscribe to publisher port and receive the events.
There is a very simple client class in *vakhshour/clients.py8*.

also **Vakhshour** can dispatch the received events via HTTP protocol as a request. You have to specifiy a list of event receiver web application in **Vakhshour** configuration file. for more information read the configuration section.

Vakhshour and Django
--------------------
**Vakhshour** provide a Django application for Django webapplications. This application will receive an event from main daemon and run its handler. It will discover all the registered event handlers inside a project and run each event handler that matched with received event.

At first you should add *vakhshour.events* in your ``INSTALLED_APPS``. Add the following code snippet in your main ``urls.py`` so **Vakhshour** can discover event handlers::

    from vakhshour.events.discovery import handler_discovery

    handler_discovery()

now **Vakhshour** will find any ``events.py`` module inside your installed app and look for a event handler registeration inside them.

Event handlers
^^^^^^^^^^^^^^
Event handler is a subclass of ``vakhshour.events.EventHandler`` class and can handle more than one event. An event handler can define some methods
to handle events. each method name should be like *on_method_name*. below example will show you every thing::

    from vakhshour.events import EventHandler, handlers


    class AMHandler(EventHandler):

        def on_foo(self, sender, first_param, another_param):
            print "I received a foo event 1: %s 2: %s" % (first_param,
	                                                  another_param)


    handlers.register(AMHandler())

Do you remember the ``foo`` event ? The above code runs when the ``foo`` events receive. Bear in mind that you should register any event handler using the **handler** object. Also you should register an instance of an event handler not the event handler itself.

