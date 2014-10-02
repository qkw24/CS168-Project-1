from sim.api import *
from sim.basics import *
INFINITY = 100
'''
Create your distance vector router in this file.
'''
class DVRouter (Entity):
    def __init__(self):
        # Add your code here!
        self.routing_table = RoutingTable()
        self.adjacent_hosts = {}

    def handle_rx(self, packet, port):
        # Add your code here!
        if type(packet) is DiscoveryPacket:
            old_DV = self.routing_table.get_optimized_dv()
            if packet.is_link_up:
                self.adjacent_hosts[packet.src] = port
                self.routing_table.insert_route(packet.src, port, 1)
            else:
                self.remove_neighbor(packet)

            if self.routing_table.get_optimized_dv() != old_DV:
                self.send_routing_update()

        elif type(packet) is RoutingUpdate:
            old_DV = self.routing_table.get_optimized_dv()

            for dest in self.routing_table.r_table.keys():
                if port in self.routing_table.r_table[dest].keys() and dest is not packet.src:
                    self.routing_table.remove_route_port(dest, port)

            for dest in packet.paths:
                dist = packet.get_distance(dest)
                self.routing_table.insert_route(dest, port, dist+self.routing_table.get_route(packet.src, port))

            if self.routing_table.get_optimized_dv() != old_DV:
                self.send_routing_update()

        else:
            target_port = self.routing_table.get_best_port(packet.dst)
            self.send(packet, target_port)

    def send_routing_update(self):
        for adj_host in self.adjacent_hosts.keys():
            update_packet = RoutingUpdate()
            new_DV = self.update_dv(adj_host, self.adjacent_hosts[adj_host])
            update_packet.paths = new_DV
            if not type(adj_host) is HostEntity:
                self.send(update_packet, self.adjacent_hosts[adj_host])

    def remove_neighbor(self, packet):
        if self.adjacent_hosts.has_key(packet.src):
            bad_port = self.adjacent_hosts[packet.src]
            del self.adjacent_hosts[packet.src]
            self.routing_table.remove_route_host(packet.src)

            for dest in self.routing_table.r_table.keys():
                if self.routing_table.r_table[dest].has_key(bad_port):
                    self.routing_table.remove_route_port(dest, bad_port)

    def update_dv(self, bad_host, bad_port):  # avoids disconnected hosts and ports
        new_dv = {}
        for dest in self.routing_table.r_table:
            best_port_for_each_dest = self.routing_table.get_best_port(dest)
            if best_port_for_each_dest == bad_port or dest == bad_host:
                continue
            else:
                new_dv[dest] = self.routing_table.r_table[dest][best_port_for_each_dest]
        return new_dv


class RoutingTable():
    def __init__(self):
        self.r_table = {}

    def size(self):
        return len(self.r_table)

    def insert_route(self, dest, port, dist):
        if not self.r_table.has_key(dest):
            self.r_table[dest] = {}
        self.r_table[dest][port] = dist

    def get_route(self, dest, port):
        #if dest not in self.r_table or port not in self.r_table[dest]:
            #return INFINITY
        return self.r_table[dest][port]

    def remove_route_host(self, dest):
        del self.r_table[dest]

    def remove_route_port(self, dest, port):
        del self.r_table[dest][port]
        #if dest is empty after remove, we delete the dest key as well
        if not len(self.r_table[dest]):
            del self.r_table[dest]

    #Given a destination, find the best port (smallest port)
    def get_best_port(self, dest):
        #if not self.r_table.has_key(dest) or not self.r_table[dest].values():
            #return None
        min_distance = self.get_minimum_distance(dest)

        #look up distance, see if they have 2 different ports
        good_ports = []
        for i, j in self.r_table[dest].iteritems():
            if j == min_distance:
                good_ports.append(i)
        #if not good_ports:
            #return None
        return min(good_ports)

    def get_minimum_distance(self, dest):
        return min(self.r_table[dest].values())

    #Given a destination, find the shortest Distance Vector
    #Try to avoid bad ports/hosts
    def get_optimized_dv(self):
        out_dv = {}
        for dest in self.r_table:
            best_port_for_each_dest = self.get_best_port(dest)
            out_dv[dest] = self.r_table[dest][best_port_for_each_dest]
        return out_dv