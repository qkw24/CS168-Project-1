from sim.api import *
from sim.basics import *

'''
Create your distance vector router in this file.
'''
class DVRouter (Entity):
    def __init__(self):
        # Add your code here!
        self.routing_table = RoutingTable
        self.adjacent_hosts = {}


    def handle_rx(self, packet, port):
        # Add your code here!
        if type(packet) is DiscoveryPacket:
            pass
        elif type(packet) is RoutingUpdate:
            pass
        else:
            target_port = self.routing_table.get_best_port(packet.dst)
            if not target_port:
                return
            self.send(packet, target_port)


class RoutingTable():
    def __init__(self):
        self.r_table = {}

    def size(self):
        return len(self.r_table)

    def insert_route(self, dest, port, dist):
        if not self.r_table.has_key(dest):
            self.r_table[dest] = {}
        self.r_table[dest][port] = dist

    def remove_route_host(self, dest):
        del self.table[dest]

    def remove_route_port(self, dest, port):
        del self.r_table[dest][port]
        #if dest is empty after remove, we delete the dest key as well
        if not len(self.r_table[dest]):
            del self.r_table[dest]

    #Given a destination, find the best port (smallest port)
    def get_best_port(self, dest):
        if not self.r_table.has_key(dest) or not self.r_table[dest].values():
            return None
        min_distance = self.get_minimum_distance(dest)

        #look up distance, see if they have 2 different ports
        good_ports = []
        for i, j in self.r_table.iteritems():
            if j == min_distance:
                good_ports.append(i)
        if not good_ports:
            return None
        return min(good_ports)

    def get_minimum_distance(self, dest):
        return min(self.r_table[dest].values())

    #Given a destination, find the shortest Distance Vector
    #Try to avoid bad ports/hosts
    #Bad host:经过任何ports都不通
    #Bad port:只是这个port不能通往某个host
    def get_minimum_dv(self, bad_port=None):
        out_dv = {}
        for dest in self.r_table:
            best_port_for_each_dest = self.get_best_port(dest)
            if best_port_for_each_dest == bad_port:
                continue
            else:
                out_dv[dest] = self.r_table[dest][best_port_for_each_dest]

        return out_dv
