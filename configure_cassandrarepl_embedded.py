#!/usr/bin/env python2.7
'''
Script for configuring cassandra ports
'''
import os
import socket
import string
import argparse
from lib.scriptutil import *
import subprocess
from configure_cassandratools import configureCassandraToolsJvm

hostname = socket.gethostname()
ip = socket.gethostbyname(hostname)

def parseOptions() :
    global options

    parser = argparse.ArgumentParser()
    parser.add_argument("--gwdir")
    parser.add_argument("--primary_host", default="localhost")
    parser.add_argument("--primary_rpc_port", default="9160")
    parser.add_argument("--repl_factor")
    parser.add_argument("-g", "--group")
    parser.add_argument("-n", "--instance")
    parser.add_argument("--host", action="append", type=str, dest="hosts")

    (options, unknown) = parser.parse_known_args()

    if not options.gwdir :
        parser.error("No gateway directory specified.")

    if not os.path.isdir(options.gwdir) :
        parser.error("Directory not found: %s" % options.gwdir)

    if not options.repl_factor :
        options.repl_factor = len(options.hosts)

    if not options.group :
        parser.error("No group specified.")

    if not options.instance :
        parser.error("No instance specified.")

    productVersion = getProductVersionFromTopology(options.gwdir)
    if productVersion >= "7.5.0" :
        print "productVersion", productVersion
        topologyId = getIdFromTopology(options.gwdir)
        groupId = getGroupIdFromTopology(options.gwdir, options.group);
        options.keyspace = ("x" + topologyId + "_" + groupId).replace("-", "_")
    else:
        options.keyspace = "kps"


def configureCassandraRepl() :
    _configureReplFactor()
    _updateNodeToolConf()
    _nodetoolRepair()
    _nodetoolRing()


def _configureReplFactor() :
    args = ["-h", options.primary_host, "-p", options.primary_rpc_port]

    proc = subprocess.Popen(
        [os.path.join(options.gwdir, "posix/bin/cassandra-cli")] + args, 
        stdin=subprocess.PIPE,
        stderr=subprocess.STDOUT)

    proc.stdin.write("""use %s;
        update keyspace %s with strategy_options = {replication_factor:%s};
        quit;\n""" % (options.keyspace, options.keyspace, str(options.repl_factor)))

    if proc.wait() != 0 :
        raise Exception("Command failed. Exit status %d" % proc.returncode)


def _updateNodeToolConf() :
    # 7.4.0+ require us to set the cassandra.config property
    configureCassandraToolsJvm(options)


def _nodetoolRepair() :
    _nodetool("repair")


def _nodetoolRing() :
    _nodetool("ring")


def _nodetool(cmd) :
    for (host, port) in _splitHostPortList(options.hosts) :
        args = ["-h", host]
        if port is not None:
            args.extend(["-p", str(port)])

        args.append(cmd)
        args.append(options.keyspace)
        
        execute(os.path.join(options.gwdir, "posix/bin/nodetool"), args)


def _splitHostPortList(hosts) :
    result = []
    for host in hosts :
        result.append(_splitHostPort(host))
    return result

def _splitHostPort(host) :
    toks = string.split(host, ":", 1)

    return (toks[0], None if len(toks) < 2 else toks[1])

if __name__ == "__main__":
    parseOptions()
    configureCassandraRepl()

