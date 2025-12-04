# -*- coding: utf-8 -*-
# Publisher.py

import csv
import time
import argparse
import utl
import json
class Publisher(object):
    def __init__(self, topic, broker_address, broker_port, data, rate):
    	'''
        :param topic: the topic associated with messages
        :param broker_address: broker public IP
        :param broker_port: XSub port number
        :param data: csv file path
        :param rate: publishing rate, unit is second
        '''
        self.topic = topic
        self.pub_socket = utl.get_publisher(broker_address, broker_port)
        self.data = data
        self.rate = rate

    def publish_data(self):
        while True:
            mes=''
            mes=raw_input()
            #test mes
            data_json=self.mes_help()
            #data_json=self.mes_reply_help()
            
            mes=str(self.topic)+","+data_json
            print('[Publisher] Published message: %s' % mes)
            self.pub_socket.send_string(str(mes))
            
            #time.sleep(self.rate)
    def mes_help(self):
        data_json=json.dumps({"command":"Help",
        "Domain":1,
        "in_switch":13,
        "out_switch":4,
        "src_ip":"10.0.0.1",
        "dis_ip":"10.0.0.3",
        "max_bw":4}, sort_keys=True)
        return data_json
    def mes_reply_help(self):
        data_json=json.dumps({"command":"Help_Reply",
        "Domain":1,
        "Can_Help_Domain":2,
        "in_switch":13,
        "out_switch":4,
        "src_ip":"10.0.0.1",
        "dis_ip":"10.0.0.3"}, sort_keys=True)
        return data_json

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--topic', type=str, help='Topic')
    parser.add_argument('-a', '--address', type=str, help='Broker public IP address')
    parser.add_argument('-p', '--port', type=str, help='Broker XSub port number')
    parser.add_argument('-f', '--file', type=str, help='Data file path')
    parser.add_argument('-r', '--rate', type=int, help='Publishing rate in second')
    args = parser.parse_args()
    pub = Publisher(args.topic, args.address, args.port, args.file, args.rate)
    pub.publish_data()