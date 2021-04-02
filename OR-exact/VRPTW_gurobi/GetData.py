'''
Description: solomon case for vrptw, distance matrix change to float type, add demand,readytime... properties, add colors
Version: 1.1
Author: 71
Date: 2021-03-02 13:58:24
'''

import math,re,copy
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

class GetData():
    def __init__(self):
        self.color_names()

    def generate_locations(self,num_points,map_size,num_vehicles=1,depot=0):
        """generate number of locations randomly in a block unit
            default TSP : num_vehicles=1,depot=0
        """
        locations=[]  # locations = [(24, 3), (21, 4), (5, 1),...] 
        for i in range(num_points):
            locations.append(tuple(np.random.randint(low=0,high=map_size,size=2))) 
        class random_data():
            def __init__(self):
                self.locations = locations
                self.num_vehicles = num_vehicles
                self.depot = depot
        return random_data()

    def get_euclidean_distance_matrix(self,locations):
        """Creates callback to return distance between locations."""
        distances = {}
        for from_counter, from_node in enumerate(locations):
            distances[from_counter] = {}
            for to_counter, to_node in enumerate(locations):
                if from_counter == to_counter:
                    distances[from_counter][to_counter] = 0
                else:
                    # Euclidean distance
                    distances[from_counter][to_counter] = (                        
                    math.hypot((from_node[0] - to_node[0]),
                                (from_node[1] - to_node[1])))
        return distances


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
        self.locations=locations
        self.demand = demand
        self.readyTime = readyTime
        self.dueTime = dueTime
        self.serviceTime = serviceTime
        self.vehicleNum = vehicleNum
        self.capacity =capacity
        self.add_deport()

    def add_deport(self):
        self.locations.append(self.locations[0])
        self.demand.append(self.demand[0])
        self.readyTime.append(self.readyTime[0])
        self.dueTime.append(self.dueTime[0])
        self.serviceTime.append(self.serviceTime[0])


    def plot_nodes(self,locations):
        ''' function to plot locations'''
        Graph = nx.DiGraph()
        nodes_name = [str(x) for x in list(range(len(locations)))]
        Graph.add_nodes_from(nodes_name)
        pos_location = {nodes_name[i]:x for i,x in enumerate(locations)}
        nodes_color_dict = ['r'] + ['gray'] * (len(locations)-1)
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
    data=GetData()
    random_data = data.generate_locations(num_points=10,map_size=100) 
    dismatrix = data.get_euclidean_distance_matrix(random_data.locations)
    print(dismatrix)  # get dismatrix randomly

    ## read solomon data
    path = r'R101.txt'
    solomon_data = data.read_solomon(path,customerNum=9) 
    solomon_data_dismatrix = data.get_euclidean_distance_matrix(solomon_data.locations) 
    print(solomon_data_dismatrix)
    data.plot_nodes(solomon_data.locations)
    ## plot function
    # data.plot_nodes(solomon_data.locations)
    route = list(range(10))
    route.append(0)
    data.plot_route(solomon_data.locations,route)

