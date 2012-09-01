Vakhshour Developer Mini Guide
==============================

At first let me say that i don't like to write documents ( as other programmer do ), so i will write about some details that you should be awar of. If you want to know more about the **Vakhshour** please read the code. It's well commented.


Let's go straight to the point. As you may read in :ref:`quick guide`, you can send an event using *Node* object. Here is some details about *Node*:

.. class:: Node(host="127.0.0.1", port="8888", secure=False, ssl_key=None, ssl_cert=None, expect_answer=False)
   :module: vakhshour.base

   This class represent a network node that runs an instance of **Vakhshour** daemon. 

.. option:: host

   **Vakhshour** server address.

.. option:: port

   **Vakhshour** server port to connect.

.. option:: secure

   whether send the event in secure mode or not.

.. option:: ssl_key

   Path to SSL key of the client.

.. option:: ssl_cert

   Path to client certificate of client.

.. option:: except_answer

   Whether except event answer or not.

.. method:: send_event(name, sender, **kwargs):

   Send an event to remote host with the name of ``name``. ``sender`` is the name of client that send th event.

   every other arguments the you pass to this method by ``**kwargs`` will send as the event parameters ans will pass to event handler.

.. class:: Event
   :module: vakhshour.base.Node

   This is the base class the *Node* class use to send the event. Its is an `AMP <http://http://amp-protocol.net/>`_ protocol implementation.

