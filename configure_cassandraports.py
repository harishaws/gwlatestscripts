#!/usr/bin/env python2.7
'''
Script for configuring cassandra ports in local cassandra server
'''
import os
import socket
import argparse
from lib.scriptutil import *

hostname = socket.gethostname()

def parseOptions() :
    global options

    parser = argparse.ArgumentParser()
    parser.add_argument("--cassandraDir")
    parser.add_argument("--seed_host")
    parser.add_argument("--cassandraRpcPort", default="9160")
    (options, unknown) = parser.parse_known_args()

    if not options.cassandraDir :
        parser.error("No cassandra directory specified.")

    if not os.path.isdir(options.cassandraDir) :
        parser.error("Directory not found: %s" % options.gwdir)


def configureCassandraPorts() :
    '''
    Update seeds and ports in cassandra.yaml
    '''
    cassandraYaml = os.path.join(options.cassandraDir, "conf/cassandra.yaml")

    if os.path.isfile(cassandraYaml) :
        replaceAll(cassandraYaml, [
            (r'localhost', hostname),  
            (r'rpc_port:.*', 'rpc_port: %s' % options.cassandraRpcPort), 
            (r'(.*- seeds: ).*', r'\1%s' % options.seed_host)])


if __name__ == "__main__":
    parseOptions()
    configureCassandraPorts()

