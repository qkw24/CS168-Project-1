from sim.api import *
from sim.basics import *

'''
    Create your distance vector router in this file.
    '''
class DVRouter (Entity):
    def __init__(self):
        self.neighbor = {self: [0]}
        self.table = {self: [0, self]}
    
    def handle_rx (self, packet, port):
        if type(packet) is DiscoveryPacket:
            routingUpdate = RoutingUpdate()    #create a routingupdate packet
            routingUpdate.src = self           #source of routing update is itself
            if (not (packet.src in self.neighbor.keys())): #the packet source is not in current neighbors 
                self.neighbor[packet.src], self.table[packet.src] = [packet.latency, port], [packet.latency, packet.src]
                routingUpdate.add_destination(packet.src, packet.latency)
            else:    #the packet source is in current neighbors
                self.neighbor[packet.src] = [packet.latency, port]
                routingUpdate.add_destination(packet.src, packet.latency)
                for key in self.table.keys():
                    if (key == packet.src):
                        self.table[packet.src][0] = packet.latency
                    if (key == self.table[packet.src][1]):
                        if (packet.latency == float("inf")):
                            self.table[packet.src][0] = float("inf")
                        else:
                            self.table[packet.src][0] = self.table[packet.src][0] - currLatency + packet.latency
                        routingUpdate.add_destination(key, self.table[packet.src][0])
            if (len(routingUpdate.all_dests()) > 0):
                self.send(routingUpdate, port, True)  # do I send to every packet here?
        elif type(packet) is RoutingUpdate:
            routingUpdate = RoutingUpdate()
            routingUpdate.src = self
            for key in packet.all_dests():
                if (not (key == self)):
                    if (not (key in self.table.keys())):
                        self.table[key] = [packet.get_distance(key) + self.neighbor[packet.src][0], packet.src]
                        routingUpdate.add_destination(key, packet.get_distance(key) + self.neighbor[packet.src][0])
                    if (packet.get_distance(key) == float("inf")):
                        for subkey in self.table.keys():
                            if (subkey == key):
                                self.table[subkey][0] = float("inf")
                                routingUpdate.add_destination(subkey, float("inf"))
                            elif(self.table[subkey][1] == key):
                                self.table[subkey][0] = float("inf")
                                routingUpdate.add_destination(subkey, float("inf"))
                    elif (key in self.table.keys()):
                        passValue = packet.get_distance(key) + self.neighbor[packet.src][0]
                        currValue = self.table[key][0]
                        if (currValue == passValue):
                            if (self.neighbor[self.table[key][1]][1] > self.neighbor[packet.src][1]):
                                self.table[key][1] = packet.src
                                routingUpdate.add_destination(key, currValue)
                        if (currValue > passValue):
                                self.table[key][0], self.table[key][1] = passValue, packet.src
                                routingUpdate.add_destination(key, passValue)
            if (len(routingUpdate.all_dests()) > 0):
                self.send(routingUpdate, port, True)
        else:
            if (packet.dst is self):
                return
            #packet.ttl = packet.ttl - 1;
            if ((packet.dst in self.table.keys()) and ((self.table[packet.dst][0] > 50))):
                routingUpdate = RoutingUpdate()
                if (packet.dst in self.neighbor.keys()):
                    self.neighbor[packet.dst] = float("inf")
                self.table[packet.dst][0] = float("inf")
                routingUpdate.add_destination(packet.dst, float("inf"))
                if (len(routingUpdate.all_dests()) > 0):
                    self.send(routingUpdate, None, True)
            if ((packet.dst in self.table.keys()) and (self.table[packet.dst][0] <= 50) and (self.table[packet.dst][0] != float("inf"))):
                self.send(packet, self.neighbor[self.table[packet.dst][1]][1])


