# -*- coding: utf-8 -*-
#
# Copyright 2002-2004 Norwegian University of Science and Technology
#
# This file is part of Network Administration Visualized (NAV)
#
# NAV is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# NAV is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NAV; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#
# Authors: Magnus Nordseth <magnun@itea.ntnu.no>
#          Stian Soiland   <stain@itea.ntnu.no>

"""Ping multiple hosts at once."""

import threading
import sys
import time
import socket
import select
import os
import random
import struct
import circbuf
import config
import binascii
import hashlib
from debug import debug

from nav.daemon import safesleep as sleep

import icmpPacket

class Host:
    def __init__(self, ip):
        self.rnd = random.randint(10000, 2**16-1)
        self.certain = 0
        self.ip = ip
        self.packet = None

        if self.is_valid_ipv6(ip):
            self.ip_version = 6
        if self.is_valid_ipv4(ip):
            self.ip_version = 4

        self.replies = circbuf.CircBuf()

    def is_v6(self):
        return self.ip_version is 6
    
    # Help method
    def is_valid_ipv6(self, addr):
        try:
            socket.inet_pton(socket.AF_INET6, addr)
            return True
        except socket.error:
            return False
    # Help method
    def is_valid_ipv4(self, addr):
        try:
            socket.inet_pton(socket.AF_INET, addr)
            return True
        except socket.error:
            return False

    def get_ipversion(self):
        return self.ip_version

    def getseq(self):
        return self.packet.id

    def nextseq(self):
        self.packet.id = (self.packet.id + 1) % 2**16
        if not self.certain and self.packet.id > 2:
            self.certain = 1

    def __hash__(self):
        return self.ip.__hash__()

    def __eq__(self, obj):
        if type(obj) == type(''):
            return self.ip == obj
        else:
            return self.ip == obj.ip
    def __repr__(self):
        return "megaping.Host instance for ip %s " % self.ip

    def getState(self, nrping=3):
        # This is the reoundtrip time. Not sure if we need
        # status bit as well...
        return self.replies[0]

class MegaPing:
    """
    Sends icmp echo to multiple hosts in parallell.
    Typical use:
    pinger = megaping.MegaPing()
    pinger.setHosts(['127.0.0.1','10.0.0.1'])
    timeUsed = pinger.ping()
    hostsUp = pinger.answers()
    hostsDown = pinger.noAnswers()
    """
    def __init__(self, socket=None, conf=None):
        if conf is None:
            try:
                self._conf = config.pingconf()
            except:
                debug("Failed to open config file. Using default values.", 2)
                self._conf = {}
        else:
            self._conf = conf
        # delay between each packet is transmitted
        self._delay = float(self._conf.get('delay', 2))/1000  # convert from ms
        # Timeout before considering hosts as down
        self._timeout = int(self._conf.get('timeout', 5))
        self._hosts = {}
        packetsize = int(self._conf.get('packetsize', 64))
        if packetsize < 44:
            raise """Packetsize (%s) too small to create a proper cookie.
                             Must be at least 44.""" % packetsize
        self._packetsize = packetsize
        self._pid = os.getpid() % 65536
        self._elapsedtime = 0

        # Create our sockets
        self.initSockets()

    def initSockets(self):
        try:
            socketv6 = socket.socket(socket.AF_INET6, socket.SOCK_RAW, socket.getprotobyname('ipv6-icmp'))
            self._sock6 = socketv6
        except socket.error, e:
            print "socket error v6: %s" % e

        try:
            socketv4 = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname('icmp'))
            self._sock4 = socketv4
        except socket.error, e:
            print "socket error v4: %s" % e

    def setHosts(self, ips):
        """
        Specify a list of ip addresses to ping. If we alredy have the host
        in our list, we reuse that host object to ensure proper sequence
        increment
        """
        # add new hosts
        currenthosts = {}
        for ip in ips:
            if not self._hosts.has_key(ip):
                currenthosts[ip] = Host(ip)
                currenthosts[ip] = Host(ip)
            else:
                    currenthosts[ip] = self._hosts[ip]
        self._hosts = currenthosts

    def reset(self):
        self._requests = {}
        self.responses = {}
        self._senderFinished = 0

    def ping(self):
        """
        Send icmp echo to all configured hosts. Returns the
        time used.
        """
        # Start working
        self.reset()
        #kwargs = {'mySocket': makeSocket()}
        self._sender = threading.Thread(target=self._sendRequests, name="sender")
        self._getter = threading.Thread(target=self._getResponses, name="getter")
        self._sender.setDaemon(1)
        self._getter.setDaemon(1)
        self._sender.start()
        self._getter.start()
        self._getter.join()
        return self._elapsedtime


    def _getResponses(self):
        start = time.time()
        timeout = self._timeout

        while not self._senderFinished or self._requests:
            if self._senderFinished:
                runtime = time.time() - self._senderFinished
                if runtime > self._timeout:
                    break
                else:
                    timeout = self._timeout - runtime

            startwait = time.time()

            # Listen for incoming data on sockets
            while 1:
                rd, wt, er = select.select([self._sock6, self._sock4], [], [], timeout)
                break

            # If data found
            if rd:
                # okay to use time here, because select has told us
                # there is data and we don't care to measure the time
                # it takes the system to give us the packet.
                arrival = time.time()
                
                # Find out which socket got data and read
                for socket in rd:
                    if socket == self._sock6:
                        try:
                            pong, sender = self._sock6.recvfrom(56+48)
                            ipv6 = True
                        except Exception, e:
                            print str(e)
                    else:
                        try:
                            pong, sender = self._sock4.recvfrom(56+48)
                            ipv6 = False
                        except Exception, e:
                            print str(e)

                # Extract header info and payload
                if ipv6:
                    pongHeader = pong[0:8]
                    pongType, pongCode, pongChksum, pongID, pongSeqnr = struct.unpack("bbHHh", pongHeader)

                    # Check sequence number
                    if not pongSeqnr == self._pid:
                        continue
                    
                    # Extract unique identity
                    identity = pong[16:53]
                else:
                    pongHeader = pong[20:28]
                    pongType, pongCode, pongChksum, pongID, pongSeqnr = struct.unpack("bbHHh", pongHeader)
                    
                    # Check sequence number
                    if not pongSeqnr == self._pid:
                        continue
                    
                    # Extract unique identity
                    identity = pong[36:73]
                
                # Find the host with this identity
                try:
                    host = self._requests[identity]
                except KeyError:
                    debug("The packet recieved from %s does not match any of "
                          "the packets we sent." % repr(sender), 7)
                    debug("Length of recieved packet: %i Cookie: [%s]" %
                          (len(pong), identity), 7)
                    continue
                
                # Delete the entry of the host who has replied and add the pingtime
                pingtime = arrival - host.time
                host.replies.push(pingtime)
                debug("Response from %-16s in %03.3f ms" %
                      (sender, pingtime*1000), 7)
                del self._requests[identity]
            elif self._senderFinished:
                break

        # Everything else timed out
        for host in self._requests.values():
            host.replies.push(None)
            #host.logPingTime(None)
        end = time.time()
        self._elapsedtime = end - start


    def _sendRequests(self, mySocket=None, hosts=None):

        # Get ip addresses to ping
        hosts = self._hosts.values()

        # Ping each host
        for host in hosts:
            if self._requests.has_key(host):
                debug("Duplicate host %s ignored" % host, 6)
                continue

            # Choose right socket for the host    
            if host.is_v6():
                mySocket = self._sock6
            else:
                mySocket = self._sock4

            host.time = time.time()

            # Create an unique identifier for each ping
            # Format: md5 hash of the ip + host.rnd (random number)
            # Example: 'f528764d624db129b32c21fbca0cb8d623930'
            md5ip = hashlib.md5()
            md5ip.update(host.ip)
            md5ip_hashed = md5ip.hexdigest()

            identifier = ''.join([md5ip_hashed, str(host.rnd)])
            
            # Save the identifier
            self._requests[identifier] = host
            
            # Create the ping packet and attach to host
            host.packet = icmpPacket.Packet((os.getpid() % 65536), host.get_ipversion(), identifier)
            
            # TODO: why do we need this
            host.nextseq()

            # Choose what socket to send the packet to
            if not host.is_v6():
                try:
                    mySocket.sendto(host.packet.packet, (host.ip, 0))
                except Exception, e:
                    debug("Failed to ping %s [%s]" % (host.ip, str(e)), 5)
            else:
                try:
                    mySocket.sendto(host.packet.packet,(host.ip,0,0,0))
                except Exception, e:
                    debug("failed to ping %s [%s]" % (host.ip, str(e)), 5)

            sleep(self._delay)
        self._senderFinished = time.time()

    def results(self):
        """
        Returns a tuple of
        (ip, roundtriptime) for all hosts.
        Unreachable hosts will have roundtriptime = -1
        """
        reply = []
        for host in self._hosts.values():
            if host.getState():
                reply.append((host.ip, host.replies[0]))
            else:
                reply.append((host.ip, -1))
        return reply

    def noAnswers(self):
        """
        Returns a tuple of
        (ip, timeout) for the unreachable hosts.
        """
        reply = []
        for host in self._hosts.values():
            if not host.getState():
                reply.append((host.ip, self._timeout))
        return reply

    def answers(self):
        """
        Returns a tuple of
        (ip, roundtriptime) for reachable hosts.
        """
        reply = []
        for host in self._hosts.values():
            if host.getState():
                reply.append((host.ip, host.replies[0]))
        return reply
