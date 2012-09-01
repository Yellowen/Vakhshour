Configuration
=============
**Vakhshour** daemon use a configuration file in json format and it look for the configuration file in :/etc/vakhshour/vakhshour.json`` by default but you can force the daemon to load another configuration file by using **-c** argument.

If you use **Vakhshour** then you should be a python developer. So you already know about json. There is no script to manipulate the configuration file at this time but your can edit the configuration file by hand. **Just make sure to do not corrupt the configuration syntax**.

Here is an example of a configuration file::

    {
        "host": "0.0.0.0",
	"publisher_port": "7777",
	"receiver_port": "8888",
	"ssl_key": "/home/lxsameer/src/Vakhshour/keys/vakhshour.key",
	"ssl_cert": "/home/lxsameer/src/Vakhshour/keys/vakhshour.crt",
	"ca_cert": "/home/lxsameer/src/Vakhshour/keys/ca.crt",
	"secure": true,
	"webapps": {
	    "rsa://localhost:3333": "/home/lxsameer/src/tmp/ida_rsa.pub"
	},
	"log_file": "/tmp/vakhshour.log",
	"log_level": 40
    }

As you can see **Vakhshour** configuration is very simple.

General configuration
---------------------

.. function:: host: "address"

   Specify the ip address to bind to. Default value is "127.0.0.1"

.. function:: publisher_port: "port"

   Specify the port number to publish the events. Default value is "7777"

.. function:: receiver_port: "port"

   Specify the port number that **Vakhshour** will listen to. Any event sender will emit events to this port. Defaykt value is "8888".

Security configuration
----------------------

.. function:: secure: true|false

   **Vakhshour** transport mode. Default is *false*.

.. function:: ssl_key: "/path/to/ssl/private/key"

   Path to SSL private key of **Vakhshour** server.

.. function:: ssl_cert: "/path/to/ssl/certificate"

   Path to SSL certificate of **Vakhshour** server.

.. function:: ca_cert: "/path/to/your/CA/certificate"

   Path to your CA certificate of **Vakhshour** server SSL keys.

With specifing the abow configuration options and running the daemon, **Vakhshour** will operate in secure mode. The important note to remember is the your clients SSL keys should sign with the same CA. **Vakhshour** will authenticate the event senders with their SSL key. If sender key signed with the CA key then sender is authorized to send an event, If not sender request will reject.

.. note:: For more information about SSL authentication take a look at `Transport Layer Security <http://en.wikipedia.org/wiki/Transport_Layer_Security>`_ and also take a look at `this <http://www.debiantutorials.com/create-your-private-certificate-authority-ca/>`_ tutorial.

Logger options
--------------
.. function:: log_file: "/path/to/log/file"

   Path to a file that main daemon will store the logger output. Default is *none*.

.. function:: log_level: 40

   Python logger level. As a python developer you know about it but for more information take a look at the python **logging** documents. Default is *40*
