from sim.api import *
from sim.basics import *

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
            old_DV = self.routing_table.get_minimum_dv()
            if packet.is_link_up:
                self.adjacent_hosts[packet.src] = port
                self.routing_table.insert_route(packet.src, port, 1)
            else:
                bad_port=self.adjacent_hosts[packet.src]
                del self.adjacent_hosts[packet.src]

                self.routing_table.remove_route_host(packet.src)
                bad_host=[]
                for host in self.routing_table.r_table:
                    if bad_port in host.keys():
                        bad_host.append(host)
                for host in bad_host:
                    self.routing_table.remove_route_port(host, bad_port)

                if self.routing_table.get_minimum_dv() != old_DV:
                    for adj_host in self.adjacent_hosts.keys():
                        update_packet = RoutingUpdate()
                        new_DV = self.routing_table.get_minimum_dv()
                        update_packet.paths = new_DV
                        if not isinstance(adj_host, HostEntity):
                            self.send(update_packet, self.adjacent_hosts[adj_host])

        elif type(packet) is RoutingUpdate:
            old_DV = self.routing_table.get_minimum_dv()
            remove = []
            for dest in self.routing_table.r_table:
                if self.routing_table.r_table[dest].has_key(port) and dest is not packet.src:
                    remove.append((dest, port))
            for (d, p) in remove:
                self.routing_table.remove_route_port(d, p)

            for hosts in packet.paths:
                dist = packet.get_distance(hosts)
                self.routing_table.insert_route(hosts, port, dist+self.routing_table.get_route(hosts, port))

            new_DV = self.routing_table.get_minimum_dv()
            if new_DV != old_DV:
                for adj_host in self.adjacent_hosts.keys():
                    update_packet = RoutingUpdate()
                    new_DV = self.routing_table.get_minimum_dv()
                    update_packet.paths = new_DV
                    if not isinstance(adj_host, HostEntity):
                        self.send(update_packet, self.adjacent_hosts[adj_host])

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

    def get_route(self, dest, port):
        if dest not in self.r_table or port not in self.r_table[dest]:
            return 999999
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
        if not self.r_table.has_key(dest) or not self.r_table[dest].values():
            return None
        min_distance = self.get_minimum_distance(dest)
        if not min_distance:
            min_distance = 9999999

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

    def get_minimum_dv(self, bad_port=None):
        out_dv = {}
        for dest in self.r_table:
            best_port_for_each_dest = self.get_best_port(dest)
            if best_port_for_each_dest == bad_port:
                continue
            else:
                out_dv[dest] = self.r_table[dest][best_port_for_each_dest]

        return out_dv
