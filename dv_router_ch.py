# TODO drop packet if not in shortest_path
from sim.api import *
from sim.basics import *

'''
Create your distance vector router in this file.
'''

class DVRouter(Entity):
    def __init__(self):
        # Add your code here!
        # What info is like
        # { 'b':[['a',4],['c',6],['d',9]],
        # 'c':[['f',4],['g',6],['e',9]],
        # }
        self.info = {}
        self.neighbors = {}
        # {'b':['d',5]}
        self.shortest_path = {}
        # self.MAX = 50
        self.broke_list = {}
        self.last_p = None
        pass


    def handle_rx(self, packet, port):
        # Add your code here!
        self.last_p = packet.src
        print "where from", packet.src
        if isinstance(packet, DiscoveryPacket):
            print "Received DiscoveryPacket: ", packet.__repr__()
            latency = packet.latency
            if latency == 0 or latency == float("inf"):
                latency = 1000
            neighbor = packet.src
            if packet.is_link_up and packet.src not in self.neighbors:
                self.neighbors[packet.src] = port
            self.update_neighbor(neighbor, neighbor, latency)
            if not packet.is_link_up and packet.src in self.neighbors:
                self.neighbors.pop(packet.src, None)
        elif isinstance(packet, RoutingUpdate):
            l = packet.all_dests()
            print "Received RoutingUpdate: ", l
            print "Received RoutingUpdate: ", [packet.get_distance(item) for item in l]
            for item in l:
                if item == self:
                    pass
                else:
                    self.check_update(item, packet.src, packet.get_distance(item))
        else:
            print "time to live", packet.ttl
            # prepare to forward according to table
            des = packet.dst
            print "Packet destination: ", des
            print "shortest: ", self.shortest_path
            via = self.shortest_path[des][0]
            print "neighbors: ", self, self.neighbors
            send_port = self.neighbors[via]
            if send_port == port:
                for item in self.info[des]:
                    if item[0] in self.neighbors and self.neighbors[item[0]] == port:
                        item[1] = 1000
                distance = 10000
                via = None
                for item in self.info[des]:
                    if item[1] < distance:
                        distance = item[1]
                        via = item[0]
                    send_port = self.neighbors[via]
            print "Packet sending port: ", send_port
            self.send(packet, send_port, False)
        s = self.update_shortest_path()
        if s != []:
            self.send_update(s)
        print "shortest_path: ", self, self.shortest_path
        print "info: ", self, self.info

    # raise NotImplementedError
    def update_shortest_path(self):
        temp = []
        for key in self.info:
            dis = 10000
            via = None
            for item in self.info[key]:
                if item[1] < dis:
                    via = item[0]
                    dis = item[1]
            if key not in self.shortest_path or dis != self.shortest_path[key][1]:
                self.shortest_path[key] = [via, dis]
                temp.append([key, via, dis])
        return temp

    def check_update(self, dest, via, dis):
        # if dest in self.broke_list and dis!= 1000:
        # if self.broke_list[dest]>0:
        # 		self.broke_list.pop(dest)
        # 	else:
        # 		self.broke_list[dest]+=1
        # 		return
        if dest in self.neighbors:
            self.write_update(dest, via, dis)
        else:
            total_dis = self.shortest_path[via][1] + dis
            print "total_dis", total_dis
            self.write_update(dest, via, total_dis)
        pass

    # TODO problem removing not exist link
    def write_update(self, dest, via, cost):
        if cost >= 1000 and self.shortest_path[dest][0] == via:
            for item in self.info[dest]:
                item[1] = 1000
            return
        if dest in self.info:
            temp = self.info[dest]
            flag = False
            for item in temp:
                if via in item:
                    flag = True
                    # print 'denuggggg',dest,item[0],item[1]
                    # item[1]=min(item[1],cost)
                    item[1] = cost
                    # print 'denuggggg1111',dest,item[0],item[1]
                    break
            if not flag:
                self.info[dest].append([via, cost])
        else:
            self.info[dest] = []
            self.info[dest].append([via, cost])
        # if cost>=1000:
        # self.broke_list[dest]=0
        # print "wwwwttttfff", self.info

    def update_neighbor(self, dest, via, cost):
        if dest in self.info:
            temp = self.info[dest]
            flag = False
            for item in temp:
                if via in item:
                    flag = True
                    item[1] = cost
                    break
            if cost == 1000:
                # if dest not in self.broke_list:
                # self.broke_list[dest]=0
                # else:
                # 	self.broke_list[dest]+=1
                for key in self.info:
                    for item in self.info[key]:
                        if item[0] == dest:
                            item[1] = 1000
                for item in self.info[dest]:
                    item[1] = 1000
            if not flag:
                self.info[dest].append([via, cost])
        else:
            self.info[dest] = []
            self.info[dest].append([via, cost])

    def send_update(self, content):
        p = RoutingUpdate()
        for key in self.shortest_path:
            if self.shortest_path[key][0] != self.last_p:
                p.add_destination(key, self.shortest_path[key][1])
        send_port = []
        for item in self.neighbors:
            if not isinstance(item, BasicHost) and item == self.last_p:
                send_port.append(self.neighbors[item])
        if send_port != []:
            self.send(p, send_port, False)

        p = RoutingUpdate()
        for key in self.shortest_path:
            p.add_destination(key, self.shortest_path[key][1])
        send_port = []
        for item in self.neighbors:
            if not isinstance(item, BasicHost) and item != self.last_p:
                send_port.append(self.neighbors[item])
        #print "neighbors: ", self, self.neighbors
        #print "send_port: ", send_port
        # print "what i have sent", [packet.get_distance(item) for item in p.all_dests]
        self.send(p, send_port, False)
        pass


    # p = RoutingUpdate()
    # for item in content:
    # if item[1]!= self.last_p:
    # 		p.add_destination(item[0],item[2])
    # send_port = []
    # for item in self.neighbors:
    # 	if not isinstance(item,BasicHost) and item== self.last_p:
    # 		send_port.append(self.neighbors[item])
    # # print "what i have sent", [packet.get_distance(item) for item in p.all_dests]
    # if send_port!=[]:
    # 	self.send(p,send_port, False)
    # print 'content',content
    # p = RoutingUpdate()
    # for item in content:
    # 	p.add_destination(item[0],item[2])
    # send_port = []
    # for item in self.neighbors:
    # 	if not isinstance(item,BasicHost):# and item!= self.last_p:
    # 		send_port.append(self.neighbors[item])
    # print "neighbors: ",self,self.neighbors
    # print "send_port: ",send_port
    # # print "what i have sent", [packet.get_distance(item) for item in p.all_dests]
    # self.send(p,send_port, False)
    # pass
