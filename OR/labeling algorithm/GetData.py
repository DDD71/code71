import math,re
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from numpy import random


class Data():
    def __init__(self):
        self.color_names()
        self.location = []
        self.capacity = 200 # 无要求
        self.demand = []
        self.servicetime = []
        self.nodeNum = []

    def generate_node(self,num,map_size=100,time_upper=1000,tw_size=100,demand_limit=20,servicetime_limit=20,capacity=200):
        """generate number of locations randomly in a block unit
            default TSP : num_vehicles=1,depot=0
        """
        locations = [(0,0)]  # locations = [(24, 3), (21, 4), (5, 1),...] 
        demands = [0]
        servicetimes = [0]
        readyTime = [0]
        dueTime = [0]
        for _ in range(num):
            locations.append(tuple(np.random.randint(low=0,high=map_size,size=2)))
            t_ = np.random.randint(low=0,high=time_upper) 
            readyTime.append(t_)  
            dueTime.append(t_ + np.random.randint(tw_size))  # timewindows size = 10
            demands.append(np.random.randint(low=0,high=demand_limit))
            servicetimes.append(np.random.randint(low=0,high=servicetime_limit))
        #  add the destination 
        locations.append(locations[0])
        readyTime.append(0)
        dueTime.append(time_upper*100)  # notice: no more than bigM
        demands.append(0)  
        servicetimes.append(0)
        
        self.location = locations
        self.readyTime = readyTime
        self.dueTime = dueTime
        self.demand = demands
        self.servicetime = servicetimes
        self.nodeNum = len(locations)
        self.capacity = capacity
        

    def get_euclidean_distance_matrix(self):
        """Creates callback to return distance between locations."""
        distances = {}
        for from_counter, from_node in enumerate(self.location):
            distances[from_counter] = []
            temp_list = []
            for to_counter, to_node in enumerate(self.location):
                if from_counter == to_counter:
                    temp_list.append(0)
                    # distances[from_counter][to_counter] = 0
                else:
                    # Euclidean distance
                    temp_list.append(
                    math.hypot((from_node[0] - to_node[0]),
                                (from_node[1] - to_node[1]))
                                )
                    # distances[from_counter][to_counter] = (                        
                    # math.hypot((from_node[0] - to_node[0]),
                                # (from_node[1] - to_node[1])))
            distances[from_counter] = temp_list
        self.disMatrix = distances

    def get_time_dismatrix(self):
        time_distances={}
        for i in range(len(self.dueTime)):
            time_dis = (np.array(self.dueTime)-np.array(self.dueTime[i])).tolist()
            # print(time_dis)
            for j in range(len(time_dis)):
                if time_dis[j]<0 or self.disMatrix[i][j]+self.dueTime[i]>self.dueTime[j]:
                    time_dis[j] = 100000
            time_distances[i] = time_dis
        self.timedisMatrix = time_distances

    def read_solomon(self,path,customerNum=100):
        '''Description: load solomon dataset'''        
        f = open(path, 'r')
        lines = f.readlines()
        locations,demand,readyTime,dueTime,serviceTime=[],[],[],[],[]
        for count,line in enumerate(lines):
            count = count + 1
            if(count == 5):  
                line = line[:-1].strip() 
                str = re.split(r" +", line)
                vehicleNum = int(str[0])
                capacity = float(str[1])
            elif(count >= 10 and count <= 10 + customerNum):
                line = line[:-1]
                str = re.split(r" +", line)
                locations.append((float(str[2]),float(str[3])))
                demand.append(float(str[4]))
                readyTime.append(float(str[5]))
                dueTime.append(float(str[6]))
                serviceTime.append(float(str[7]))
        self.location = locations
        self.demand = demand
        # readyTime[0],dueTime[0] = 0,0
        self.readyTime = readyTime
        self.dueTime = dueTime
        self.serviceTime = serviceTime
        self.vehicleNum = vehicleNum
        self.capacity =capacity
        self.add_deport()
        self.nodeNum = len(locations)
        self.customerNum = customerNum

    def add_deport(self):
        self.location.append(self.location[0])
        self.demand.append(self.demand[0])
        self.readyTime.append(self.readyTime[0])
        self.dueTime.append(self.dueTime[0])
        self.serviceTime.append(self.serviceTime[0])
        self.dueTime[0] = 0


    def plot_nodes(self):
        ''' function to plot locations'''
        self.location
        Graph = nx.DiGraph()
        nodes_name = [str(x) for x in list(range(len(self.location)))]
        Graph.add_nodes_from(nodes_name)
        pos_location = {nodes_name[i]:x for i,x in enumerate(self.location)}
        nodes_color_dict = ['r'] + ['gray'] * (len(self.location)-2) + ['r']
        nx.draw_networkx(Graph,pos_location,node_size=200,node_color=nodes_color_dict,labels=None)  
        plt.show(Graph)

    def plot_route(self,locations,route,edgecolor='k',showoff=True):
        ''' function to plot locations and route'''
        'e.g. [0,1,5,9,0]'
        Graph = nx.DiGraph()
        edge = []
        edges = []
        for i in route : 
            edge.append(i)
            if len(edge) == 2 :
                edges.append(tuple(edge))
                edge.pop(0)
        nodes_name = [x for x in list(range(len(locations)))]
        Graph.add_nodes_from(nodes_name)
        Graph.add_edges_from(edges)
        pos_location = {nodes_name[i] : x for i,x in enumerate(locations)}
        nodes_color_dict = ['r'] + ['gray'] * (len(locations)-2) + ['r']  # 第一个和最后一个红色
        nx.draw_networkx(Graph,pos_location,node_size=200,node_color=nodes_color_dict,edge_color=edgecolor,labels=None)  
        if showoff:
            plt.show(Graph)

    def color_names(self):
        self.colornames = [
                    '#F0F8FF',
                    '#FAEBD7',
                    '#00FFFF',
                    '#7FFFD4',
                    '#F0FFFF',
                    '#F5F5DC',
                    '#FFE4C4',
                    '#000000',
                    '#FFEBCD',
                    '#0000FF',
                    '#8A2BE2',
                    '#A52A2A',
                    '#DEB887',
                    '#5F9EA0',
                    '#7FFF00',
                    '#D2691E',
                    '#FF7F50',
                    '#6495ED',
                    '#FFF8DC',
                    '#DC143C',
                    '#00FFFF',
                    '#00008B',
                    '#008B8B',
                    '#B8860B',
                    '#A9A9A9',
                    '#006400',
                    '#BDB76B',
                    '#8B008B',
                    '#556B2F',
                    '#FF8C00',
                    '#9932CC',
                    '#8B0000',
                    '#E9967A',
                    '#8FBC8F',
                    '#483D8B',
                    '#2F4F4F',
                    '#00CED1',
                    '#9400D3',
                    '#FF1493',
                    '#00BFFF',
                    '#696969',
                    '#1E90FF',
                    '#B22222',
                    '#FFFAF0',
                    '#228B22',
                    '#FF00FF',
                    '#DCDCDC',
                    '#F8F8FF',
                    '#FFD700',
                    '#DAA520',
                    '#808080',
                    '#008000',
                    '#ADFF2F',
                    '#F0FFF0',
                    '#FF69B4',
                    '#CD5C5C',
                    '#4B0082',
                    '#FFFFF0',
                    '#F0E68C',
                    '#E6E6FA',
                    '#FFF0F5',
                    '#7CFC00',
                    '#FFFACD',
                    '#ADD8E6',
                    '#F08080',
                    '#E0FFFF',
                    '#FAFAD2',
                    '#90EE90',
                    '#D3D3D3',
                    '#FFB6C1',
                    '#FFA07A',
                    '#20B2AA',
                    '#87CEFA',
                    '#778899',
                    '#B0C4DE',
                    '#FFFFE0',
                    '#00FF00',
                    '#32CD32',
                    '#FAF0E6',
                    '#FF00FF',
                    '#800000',
                    '#66CDAA',
                    '#0000CD',
                    '#BA55D3',
                    '#9370DB',
                    '#3CB371',
                    '#7B68EE',
                    '#00FA9A',
                    '#48D1CC',
                    '#C71585',
                    '#191970',
                    '#F5FFFA',
                    '#FFE4E1',
                    '#FFE4B5',
                    '#FFDEAD',
                    '#000080',
                    '#FDF5E6',
                    '#808000',
                    '#6B8E23',
                    '#FFA500',
                    '#FF4500',
                    '#DA70D6',
                    '#EEE8AA',
                    '#98FB98',
                    '#AFEEEE',
                    '#DB7093',
                    '#FFEFD5',
                    '#FFDAB9',
                    '#CD853F',
                    '#FFC0CB',
                    '#DDA0DD',
                    '#B0E0E6',
                    '#800080',
                    '#FF0000',
                    '#BC8F8F',
                    '#4169E1',
                    '#8B4513',
                    '#FA8072',
                    '#FAA460',
                    '#2E8B57',
                    '#FFF5EE',
                    '#A0522D',
                    '#C0C0C0',
                    '#87CEEB',
                    '#6A5ACD',
                    '#708090',
                    '#FFFAFA',
                    '#00FF7F',
                    '#4682B4',
                    '#D2B48C',
                    '#008080',
                    '#D8BFD8',
                    '#FF6347',
                    '#40E0D0',
                    '#EE82EE',
                    '#F5DEB3',
                    '#FFFFFF',
                    '#F5F5F5',
                    '#FFFF00',
                    '#9ACD32']


if __name__ == "__main__":
    ## generate data randomly
    nodes = Data()
    # nodes.generate_node(num=10)
    # nodes.read_solomon(path=r'r101.txt',customerNum=30)
    nodes.generate_node(num=20)
    nodes.get_euclidean_distance_matrix()
    nodes.get_time_dismatrix()

    nodes.plot_nodes()


