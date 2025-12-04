import sys
import time
import utl
import zmq


class Broker(object):
    def __init__(self, xsub_port, xpub_port):
        self.xsub_socket, self.xpub_socket = utl.get_broker(xsub_port, xpub_port)
        self.poller = zmq.Poller()
        self.poller.register(socket=self.xpub_socket, flags=zmq.POLLIN)#9090
        self.poller.register(socket=self.xsub_socket, flags=zmq.POLLIN)#9089
        self.buffer = {}
    def handler(self):

        while True:
            events = dict(self.poller.poll(1000))
            if self.xpub_socket in events:
                message = self.xpub_socket.recv_multipart()
                print("subscription message: {}".format(message[0]))
                self.xsub_socket.send_multipart(message)
            if self.xsub_socket in events:
                message = self.xsub_socket.recv_multipart()
                print("publishing message: {}".format(message))
                self.xpub_socket.send_multipart(message)

if __name__ == '__main__':
	# The 1st argument is XSub port number, the 2nd is XPub port number
    broker = Broker(sys.argv[1], sys.argv[2])
    broker.handler()