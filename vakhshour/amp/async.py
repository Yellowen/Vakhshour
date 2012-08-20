"""
Asyncore-based implementation of the AMP protocol.
"""

import socket
import threading
import asyncore, asynchat, socket, struct, sys
import defer, ampy

class AMP_Server(asyncore.dispatcher):
    def __init__(self, port, bindHost="0.0.0.0"):
        self.port = port
        self.bindHost = bindHost
        asyncore.dispatcher.__init__(self) # we get added to the global asyncore "map" here

    def start_listening(self):
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind((self.bindHost, self.port))
        self.listen(10)

    def loop(self):
        asyncore.loop()

    def stop(self):
        """
        I don't think this will actually cause any existing connections to be closed, and if it doesn't
        then the asyncore loop won't terminate. Kinda lame.
        """
        self.close()

    def handle_accept(self):
        conn, addr = self.accept()
        self.buildProtocol(conn, addr)

    def buildProtocol(self, conn, addr):
        """
        Override this to instantiate your own AMP_Protocol subclass
        """
        pass


def synchronized(func):
    """
    Decorator to synchronize access to a method through self.lock
    """
    def _synchronized(self, *args, **kw):
        self.lock.acquire()
        try:
            return func(self, *args, **kw)
        finally:
            self.lock.release()
    return _synchronized


KEY_LEN_READ, KEY_DATA_READ, VAL_LEN_READ, VAL_DATA_READ = range(4)

class AMP_Protocol(asynchat.async_chat):
    current_key = None
    counter = 0

    box = None

    responders = {}

    def __init__(self, conn, addr):
        asynchat.async_chat.__init__(self, conn)
        self.addr = addr
        self.ibuffer = []
        self.obuffer = ""
        self.set_terminator(2)

        self.state = KEY_LEN_READ

        self.box = {}

        self.awaitingResponse = {}

        self.lock = threading.Lock()

    def registerResponder(self, command, responder):
        self.responders[command.commandName] = (command, responder)

    def collect_incoming_data(self, data):
        """Buffer the data"""
        self.ibuffer.append(data)

    def found_terminator(self):
        # handle buffered data and transition state

        if self.state == KEY_LEN_READ:
            # keys should never be longer that 255 bytes, but we aren't actually
            # enforcing that here. todo?
            key_len = struct.unpack('!H', "".join(self.ibuffer))[0]
            self.ibuffer = []
            if key_len == 0: # a null key length (two NULL bytes) indicates the termination of this AMP box
                box = self.box

                self.current_key = None # no need to keep this around until the next box overwrites it
                self.val_data = None # no need to keep this around until the next box overwrites it
                self.box = {} # new data belongs to a new AMP box

                self.processFullMessage(box)
                self.set_terminator(2)
            else:
                self.set_terminator(key_len)
                self.state = KEY_DATA_READ

        elif self.state == KEY_DATA_READ:
            self.current_key = "".join(self.ibuffer)
            self.ibuffer = []
            self.set_terminator(2) # collect 2 bytes (length of the value that this key corresponds to
            self.state = VAL_LEN_READ

        elif self.state == VAL_LEN_READ:
            val_len = struct.unpack('!H', "".join(self.ibuffer))[0]
            self.ibuffer = []
            self.set_terminator(val_len)
            self.state = VAL_DATA_READ

        elif self.state == VAL_DATA_READ:
            val_data = "".join(self.ibuffer)
            self.ibuffer = []
            self.box[self.current_key] = val_data
            self.state = KEY_LEN_READ # start over again
            self.set_terminator(2)

    def processFullMessage(self, box):
        if ampy.COMMAND in box:
            cmdName = box[ampy.COMMAND]
            command, handler = self.responders.get(cmdName, (None, None))
            askKey = box.get(ampy.ASK, None)
            if not handler:
                if askKey:
                    resp = [ampy.ERROR, askKey,
                            ampy.ERROR_CODE, ampy.UNHANDLED_ERROR_CODE,
                            ampy.ERROR_DESCRIPTION, "No handler for command"]
                    self.push(''.join(ampy.insertPrefixes((resp))))
            else:
                kw = command.deserializeRequest(box)
                if askKey:
                    defer.maybeDeferred(handler, **kw).addCallbacks(self._cb_gotResponse, self._eb_gotResponseError,
                        callbackArgs=(command, askKey), errbackArgs=(command, askKey))
                else:
                    handler(**kw)

        elif ampy.ANSWER in box:
            answerKey = box[ampy.ANSWER]
            command, deferred = self.awaitingResponse.pop(answerKey, (None,None) )
            if command:
                kw = command.deserializeResponse(box)
                deferred.callback(kw)
            else:
                sys.stderr.write("Got answer key %s, but we weren't waiting for it! weird!\n" % (answerKey,))
        elif ampy.ERROR in box:
            errorKey = box[ampy.ERROR]
            command, deferred = self.awaitingResponse.pop(errorKey, (None,None) )
            if command:
                e = ampy.AMPError(box[ampy.ERROR_CODE], box[ampy.ERROR_DESCRIPTION])
                deferred.errback(e)
            else:
                sys.stderr.write("Got error key %s, but we weren't waiting for it! weird!\n" % (errorKey,))
        else:
            sys.stderr.write("Insane AMP packet!\n")


    def _cb_gotResponse(self, kw, command, askKey):
        dataList = [ampy.ANSWER, askKey]
        command.serializeResponse(dataList, kw)
        self.push(''.join(ampy.insertPrefixes(dataList)))

    def _eb_gotResponseError(self, f, command, askKey):
        key = f.check(*command.errors.keys())
        if key:
            code = command.errors[key]
            descr = "" # TODO what should go here?
        else:
            sys.stderr.write("Unhandled exception raised in AMP Command handler:\n")
            f.printTraceback()
            code = ampy.UNKNOWN_ERROR_CODE
            descr = "Unknown Error"

        resp = [ampy.ERROR, askKey,
                ampy.ERROR_CODE, code,
                ampy.ERROR_DESCRIPTION, descr]
        self.push(''.join(ampy.insertPrefixes(resp)))

    def callRemote(self, command, **kw):
        """
        Asyncronously call a remote AMP command.
        """

        # compose packet
        dataList = [ampy.COMMAND, command.commandName]

        retVal = None
        # remember that we sent this command if a response is expected
        if command.requiresAnswer:
            # XXX TODO a race condition exists between the two lines below
            askKey = str(self.counter)
            self.counter += 1

            retVal = defer.Deferred()
            self.awaitingResponse[askKey] = (command, retVal)

            dataList.extend( [ampy.ASK, askKey] )

        #for kv in COMMAND, command.commandName, ASK, askKey:
        #    dataList.append(struct.pack('!H', len(kv)))
        #    dataList.append(kv)

        command.serializeRequest(dataList, kw)
        ampy.insertPrefixes(dataList)

        data = ''.join(dataList)

        # write packet
        self.push(data)

        return retVal

    callRemote = synchronized(callRemote)

    # synchronize access to these methods since calls to this singleton object
    # can come from the main asyncore thread and also from the FXCM API thread(s)
    def handle_read(self):
        return asynchat.async_chat.handle_read(self)
    handle_read = synchronized(handle_read)

    def initiate_send(self):
        return asynchat.async_chat.initiate_send(self)
    initiate_send = synchronized(initiate_send)



