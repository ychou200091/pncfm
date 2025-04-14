# -*- coding: utf-8 -*-
# Subscriber.py
import sys
import argparse
import utl
import json

class Subscriber(object):
    def __init__(self, broker_address, broker_port, topics):
        self.topics = topics
        self.socket = utl.get_subscriber(broker_address, broker_port, topics)

    def subscribe(self):
        while True:
            msg = self.socket.recv_multipart()
            print('[Subscriber] Received message: %s' % msg[0].split(',',1)[1])
            jsondata=json.loads(msg[0].split(',',1)[1])
            print jsondata['Domain']
  
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--topics', type=str, help='Topics separated by comma')
    parser.add_argument('-a', '--address', type=str, help='Broker address')
    parser.add_argument('-p', '--port', type=str, help='Broker port number')
    args = parser.parse_args()
    topics = args.topics.split(',')
    print args.address," ",args.port," ",topics
    sub = Subscriber(args.address, args.port, topics)
    sub.subscribe()