'''
Author: 71
Date: 2021-11-26 20:00:39
LastEditTime: 2022-02-22 16:06:09
Description: Feillet (2004). implementation with python
'''

import numpy as np
import time 
import matplotlib.pyplot as plt
import copy,json
from GetData import *
import torch as tf

class Label:
    def __init__(self):
        self.path = [0]
        self.travel_time = 0
        self.obj = 0
        self.demand=0
        self.unreachNum = 0

class Labeling():
    def __init__(self,Graph) -> None:
        self.Graph = Graph
        self.Q = {}  # initial Queue
        self.des = Graph.nodeNum-1
        self.unreachNum = 0
        
    def preprocess(self,tabu_list=None):
        # preprocessing for ARCS 
        if tabu_list is None:
            tabu_list = []
        self.query_arc = {}  # 任意节点的可行路径, 关键
        Graph = self.Graph
        Graph.arcs = {}
        self.arcNum = 0
        self.neg_arcs = 0
        for i in range(Graph.nodeNum):
            self.query_arc[i] = []  # list
            for j in range(Graph.nodeNum):
                if (i!=Graph.nodeNum-1) and (j!=0) and (i!=j)and (Graph.readyTime[i]+Graph.serviceTime[i]+Graph.disMatrix[i][j] < Graph.dueTime[j]) and i not in tabu_list and j not in tabu_list:
                    Graph.arcs[i,j] = 1
                    self.arcNum += 1
                    self.query_arc[i].append(j)
                    if Graph.disMatrix[i][j]-Graph.rmp[i]<0:
                        self.neg_arcs += 1
                else:
                    Graph.arcs[i,j] = 0  
        self.Graph = Graph  # update
    
    def dominant_rule(self,node_num): #espprc
        cur_node = self.Q[node_num][-1]  
        remove_list = []
        for node in self.Q[node_num]:
            if node.path[-1] == cur_node.path[-1] and node.path != cur_node.path: # 如果终点相同
                if node.obj<=cur_node.obj and node.travel_time<=cur_node.travel_time and node.demand<=cur_node.demand and node.unreachNum<=cur_node.unreachNum:
                    cur_node = node  # replace
                elif node.obj>=cur_node.obj and node.travel_time>=cur_node.travel_time and node.demand>=cur_node.demand and node.unreachNum>=cur_node.unreachNum:
                    remove_list.append(node)  #记录dominant的节点
        for i in remove_list:
            self.Q[node_num].remove(i)

    def get_unreached_nodes(self,extended_label):
        count = 0
        last_node = extended_label.path[-1]
        for n in extended_label.path:
            if n in self.query_arc[last_node]:
                count += 1
        return count

    def select_opt(self):
        opt_sol = self.Q[self.Graph.nodeNum-1].pop()
        for sol in self.Q[self.Graph.nodeNum-1]:
            if opt_sol.obj > sol.obj:
                opt_sol = sol
        self.opt_sol = opt_sol
        self.Q[self.Graph.nodeNum-1] = [opt_sol]


    def run(self,tabu_list=None):
        self.preprocess(tabu_list)  # 去处理，去掉不用的弧
        print('the total number of arcs is :{}, neg arcs:{}'.format(self.arcNum,self.neg_arcs))
        for i in range(self.Graph.nodeNum):
            self.Q[i] = []
        current_label = Label()  #从0开始
        self.Q[0].append(current_label)
        break_flag = 1
        self.epoch = 0
        while(break_flag):
            self.epoch += 1
            for i in range(self.Graph.nodeNum-1):
                break_flag = 0
                if self.Q[i]:
                    break_flag = 1
                    break
            if len(self.Q[self.Graph.nodeNum-1]):  # feasible solution
                self.select_opt()
                # print('current obj:{}, feasible path:{}'.format(self.opt_sol.obj,self.opt_sol.path))
            for node in range(self.Graph.nodeNum-1):
                if len(self.Q[node])>100:   # dominante before extend label
                    self.dominant_rule(node)
                while(len(self.Q[node])>0) : 
                    current_label = self.Q[node].pop()
                    for next_node in self.query_arc[node]:
                        if next_node in current_label.path: # 禁止重复探索
                            continue
                        extended_label = copy.deepcopy(current_label)
                        extended_label.path.append(next_node)
                        extended_label.demand += self.Graph.demand[next_node]
                        extended_label.obj += self.Graph.disMatrix[node][next_node]-self.Graph.rmp[node]
                        extended_label.unreachNum = self.get_unreached_nodes(extended_label)
                        arrive_time = extended_label.travel_time+self.Graph.disMatrix[node][next_node]+self.Graph.serviceTime[node]
                        if arrive_time < self.Graph.readyTime[next_node]:
                            extended_label.travel_time = self.Graph.readyTime[next_node]
                        elif arrive_time <= self.Graph.dueTime[next_node]:
                            extended_label.travel_time = arrive_time
                        else:
                            extended_label.travel_time = np.Inf
                        
                        if extended_label.demand <= self.Graph.capacity:  # capacity
                            if  extended_label.travel_time >= self.Graph.readyTime[next_node] and extended_label.travel_time <= self.Graph.dueTime[next_node]:
                                self.Q[next_node].append(extended_label)
        self.select_opt()
     

# np.random.seed(1)
if __name__=='__main__':

    customerNum = 30
    Graph = Data()
    Graph.read_solomon(path=r'r101.txt',customerNum=customerNum)
    Graph.get_euclidean_distance_matrix()
    start = time.time()
    Graph.rmp = np.random.randint(0,50,customerNum+2)
    # Graph.rmp = [100] * (customerNum+2)
    espprc = Labeling(Graph)
    espprc.run()
    print('time cost:',time.time()-start)
    print('best obj:',espprc.opt_sol.obj)
    print('best path:',espprc.opt_sol.path)
    print('demand:',espprc.opt_sol.demand)


    

    


