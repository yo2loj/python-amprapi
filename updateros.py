#!/usr/bin/env python
#
# Copyright 2013, 2014 Tom Hayward <tom@tomh.us>
#
# This file is part of python-amprapi.
#
# python-amprapi is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# python-amprapi is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with python-amprapi.  If not, see <http://www.gnu.org/licenses/>.

#
#  modified for ROS API by YO2LOJ - 8/Dec/2015
#

import amprapi
import rosapi
from datetime import date
import time
import socket
import sys

import settings

def get_encap():
    ampr = amprapi.AMPRAPI()
    return ampr.encap


def filter_encap(route):
    if route.network() in settings.ignore_networks:
        return False
    return route


def parse_ros_route(rsp):
    dstaddress, gateway = None, None

    res = rsp[0]

    if (res == "!re"):
        attr = rsp[1]

        gateway = attr["=gateway"]

        if gateway.startswith("ampr-"):
            dstaddress = attr["=dst-address"]
            return dstaddress, gateway
        else:
            return None
    else:
        return None


def parse_ros_ipip(rsp):
    name, remoteaddr = None, None

    res = rsp[0]

    if (res == "!re"):
        attr = rsp[1]

        name = attr["=name"]

        if name.startswith("ampr-"):
            remoteaddr =  attr["=remote-address"]
            return name, remoteaddr
        else:
            return None
    else:
        return None


def export_ros(api, command):
    cmd = []
    cmd.append(command)
    rsp = api.talk(cmd)
    return rsp;

def export_ros_routes(api):
    return filter(None, map(parse_ros_route,
                            export_ros(api, "/ip/route/print")))


def export_ros_ipip_interfaces(api):
    return filter(None, map(parse_ros_ipip,
                            export_ros(api, "/interface/ipip/print")))


def filter_ipip_ampr(ipips):
    return filter(
        lambda (interface, gateway): interface.startswith('ampr-'), ipips)

def command_ros(api, cmd, res_param):
    val = None
    rsp = api.talk(cmd)
    res = rsp[0]
    if (res[0] == "!re"):
        attr = res[1]
        val = attr[res_param]
        if (val):
            return val;
    return None

def main():
    verbose = 0

    encap = filter(None, map(filter_encap, get_encap()))

    s = None
    for res in socket.getaddrinfo(settings.edge_router_ip, "8728", socket.AF_UNSPEC, socket.SOCK_STREAM):
        af, socktype, proto, canonname, sa = res
        try:
             s = socket.socket(af, socktype, proto)
        except (socket.error, msg):
            s = None
            continue
        try:
            s.connect(sa)
        except (socket.error, msg):
            s.close()
            s = None
            continue
        break
    if s is None:
        print ('could not open socket')
        sys.exit(1)

    try:
        apiros = rosapi.ApiRos(s)
        apiros.login(settings.username, settings.password)

        ros_routes = export_ros_routes(apiros)
        ros_ipips = export_ros_ipip_interfaces(apiros)

        unchanged = 0
        routes_to_add = set(encap)
        routes_to_remove = set(ros_routes)

        ipips_to_remove = set(filter_ipip_ampr(ros_ipips))
        for entry in encap:
            dstaddress = entry.network()
            gateway = entry['gatewayIP']
            interface = "ampr-%s" % gateway
            if (dstaddress, interface) in ros_routes and \
               (interface, gateway) in ros_ipips:
                routes_to_add.discard(entry)
                routes_to_remove.discard((dstaddress, interface))
                ipips_to_remove.discard((interface, gateway))
                unchanged += 1

        if "-v" in sys.argv:
            verbose = 1

        if (verbose): print "# %d routes unchanged" % unchanged

        ac = []

        if len(routes_to_remove) > len(routes_to_add) + 100 and "-f" not in sys.argv:
            raise UserWarning("Sanity check failed: removing too many routes (-%d +%d)" % (
                len(routes_to_remove), len(routes_to_add)))

        if routes_to_remove:
            if (verbose): print "# removing old or modified routes"
        for route in routes_to_remove:
            if (verbose): print "/ip route remove [find dst-address=\"%s\" gateway=\"%s\"]" % route
            # find
            ac = []
            ac.append("/ip/route/print")
            ac.append("?dst-address=%s" % route[0])
            ac.append("?gateway=%s" % route[1])
            ident = command_ros(apiros, ac, "=.id")
            # remove
            if (ident):
                ac = []
                ac.append("/ip/route/remove");
                ac.append("=.id=%s" % ident);
                command_ros(apiros, ac, "")
            time.sleep(0.1)
        if ipips_to_remove:
            if (verbose): print "# removing orphaned ipip interfaces"
        for interface, gateway in ipips_to_remove:
            if (verbose): print "/interface ipip remove [find name=\"%s\"]" % interface
            # find
            ac = []
            ac.append("/interface/ipip/print")
            ac.append("?name=%s" % interface)
            ident = command_ros(apiros, ac, "=.id")
            # remove
            if (ident):
                ac = []
                ac.append("/interface/ipip/remove");
                ac.append("=.id=%s" % ident);
                command_ros(apiros, ac, "")
            time.sleep(0.1)
        if routes_to_add:
            if (verbose): print "# adding new and modified routes"
        for entry in routes_to_add:
            interface = "ampr-%s" % entry['gatewayIP']
            if (verbose):
                print "/interface ipip add !keepalive clamp-tcp-mss=yes "
                "local-address=%s name=%s remote-address=%s comment=\"%s\"" % (
                    settings.edge_router_public_ip, interface, entry['gatewayIP'],
                    "AMPR last updated %s, added %s" % (
                        entry['updated'].date(), date.today()))

            # add interface
            ac = []
            ac.append("/interface/ipip/add")
            ac.append("=!keepalive")
            ac.append("=clamp-tcp-mss=yes")
            ac.append("=local-address=%s" % settings.edge_router_public_ip)
            ac.append("=name=%s" % interface)
            ac.append("=remote-address=%s" % entry['gatewayIP'])
            ac.append("=comment=AMPR last updated %s, added %s" % (entry['updated'].date(), date.today()))
            command_ros(apiros, ac, "")

            if (verbose): print "/ip route add dst-address=%s gateway=%s distance=%s pref-src=%s" % (entry.network(), interface, settings.distance, settings.pref_source)

            # add route
            ac = []
            ac.append("/ip/route/add")
            ac.append("=dst-address=%s" % entry.network())
            ac.append("=gateway=%s" % interface)
            ac.append("=distance=%s" % settings.distance)
            ac.append("=pref-src=%s" % settings.pref_source)
            command_ros(apiros, ac, "")

            if (verbose): print "/ip neighbor discovery set %s discover=no" % interface

            # disable neighbor discovery
            # find
            ac = []
            ac.append("/ip/neighbor/discovery/print")
            ac.append("?name=%s" % interface)
            ident = command_ros(apiros, ac, "=.id")
            # disable
            if (ident):
                ac = []
                ac.append("/ip/neighbor/discovery/set")
                ac.append("=.id=%s" % ident);
                ac.append("=discover=no")
                command_ros(apiros, ac, "")
            time.sleep(0.1)

    except KeyboardInterrupt:
        print "KeyboardInterrupt received, closing..."
    except UserWarning, e:
        print e
    except socket.timeout:
        print "timeout"
    finally:
        s.close()

if __name__ == '__main__':
    main()

