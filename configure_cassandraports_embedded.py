#!/usr/bin/env python2.7
'''
Script for configuring cassandra ports
'''
import os
import socket
import argparse
from lib.scriptutil import *


hostname = socket.gethostname()
ip = socket.gethostbyname(hostname)

def parseOptions() :
    global options

    parser = argparse.ArgumentParser()
    parser.add_argument("--gwdir")
    parser.add_argument("--seed_host")
    parser.add_argument("-g", "--group")
    parser.add_argument("-n", "--instance")
    parser.add_argument("--jmxPort", default="7199")
    parser.add_argument("--cassandraRpcPort", default="9160")

    parser.add_argument("--username", default="admin")
    parser.add_argument("--password", default="changeme")
    (options, unknown) = parser.parse_known_args()

    if not options.gwdir :
        parser.error("No gateway directory specified.")

    if not options.gwdir :
        parser.error("No gateway directory specified.")

    if not os.path.isdir(options.gwdir) :
        parser.error("Directory not found: %s" % options.gwdir)

    if not options.group :
        parser.error("No group specified.")

    if not options.instance :
        parser.error("No instance specified.")

def configureCassandraPorts() :
    cassandraDir = os.path.join(options.gwdir, "groups/topologylinks", "%s-%s" % (options.group, options.instance), "conf/kps/cassandra")

    _updateJvmXML(cassandraDir)
    _updateCassandraYaml(cassandraDir)
    _updateClientYaml(cassandraDir)


def _updateJvmXML(cassandraDir) :
    '''
    Enable JMX and set the port.
    '''
    jvmXml = os.path.join(cassandraDir, "jvm.xml")
    replaceAll(jvmXml, [
        (r'.*<if property="enableJMX">.*', ''), 
        (r'.*</if>.*', ''),
        (r'(.*-Dcom.sun.management.jmxremote.port=).*("/>)', r'\g<1>%s\2' % options.jmxPort)])


def _updateCassandraYaml(cassandraDir) :
    '''
    Update seeds and ports in cassandra.yaml
    '''
    cassandraYaml = os.path.join(cassandraDir, "cassandra.yaml")

    if os.path.isfile(cassandraYaml) :
        replaceAll(cassandraYaml, [
            (r'localhost', getGroupHostName(hostname, options.group)), 
            (r'rpc_port:.*', 'rpc_port: %s' % options.cassandraRpcPort), 
            (r'(.*- seeds: ).*', r'\1%s' % getGroupHostName(options.seed_host, options.group))])

def _updateClientYaml(cassandraDir) :
    '''
    Set host and port in client.yaml
    '''
    clientYaml = os.path.join(cassandraDir, "client.yaml")
    replaceAll(clientYaml, [
        (r'{hosts:.*}', "{hosts: '%s:%s'}" % (getGroupHostName(hostname, options.group), options.cassandraRpcPort))])

if __name__ == "__main__":
    parseOptions()
    configureCassandraPorts()

