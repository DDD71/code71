'''
Description: ESPPRC solved by gurobi
Version: 1.0
Author: 71
Date: 2021-04-01 11:48:47
'''
import numpy as np
from gurobipy import *
from GetData import *


def spprc_gp(nodes):
    
    BigM = 1e8
    model = Model('SPPRC')
    #定义决策变量
    x = {}
    for i in range(nodes.nodeNum):
        for j in range(nodes.nodeNum):
            if(i != j):
                name = 'x_' + str(i) + '_' + str(j) 
                x[i,j] = model.addVar(0,1,vtype= GRB.BINARY,name= name)

    model.update()
    #定义目标函数
    obj = LinExpr(0)
    for i in range(nodes.nodeNum):
        for j in range(nodes.nodeNum):
            if(i != j):
                obj.addTerms(-nodes.disMatrix[i][j], x[i,j])
    model.setObjective(obj, GRB.MINIMIZE)

    # s.t 1
    for h in range(1, nodes.nodeNum - 1):
        expr1 = LinExpr(0)
        expr2 = LinExpr(0)
        for i in range(nodes.nodeNum-1):
            if (h != i):
                expr1.addTerms(1, x[i,h])
        for j in range(1,nodes.nodeNum):
            if (h != j):
                expr2.addTerms(1, x[h,j])
        model.addConstr(expr1 == expr2, name= 'flow_conservation_' + str(i) + str(j))
        expr1.clear()
        expr2.clear()

    # s.t 2 
    lhs = LinExpr(0)
    for j in range(1,nodes.nodeNum-1):
        lhs.addTerms(1, x[0,j])
    model.addConstr(lhs == 1, name= 'depart_' + str(j))

    # s.t 3
    lhs = LinExpr(0)
    for i in range(0,nodes.nodeNum-1):
        lhs.addTerms(1, x[i,nodes.nodeNum-1])
    model.addConstr(lhs == 1, name= 'arrive_' + str(i))

    # s.t 4
    for i in range(nodes.nodeNum):
        for j in range(nodes.nodeNum):
            if (i != j):
                model.addConstr(nodes.dueTime[i] + nodes.disMatrix[i][j] - nodes.dueTime[j] <= BigM*(1-x[i,j]), name = 'time_window' + str(i) + str(j))

    # s.t 5
    lhs = LinExpr(0)
    for i in range(nodes.nodeNum-1):
        for j in range(nodes.nodeNum):
            if (i!=j):
                lhs.addTerms(nodes.demand[j], x[i,j])
    model.addConstr(lhs <= nodes.capacity, name= 'capacity_limited' )

    model.setParam("OutputFlag", 0)
    model.optimize()

    return model


def demand_meet(custums,nodes):
    demand_meet_value = 0
    for i in custums:
        demand_meet_value += nodes.demand[i]
    return demand_meet_value

def get_route(x):
    route = [0]
    while(1):
        count_flag = 1
        for i in range(len(x)):
            n = list(map(int, re.findall("\d+",x[i])))
            if (route[-1] == n[0]):
                route.append(n[1])
                count_flag = 0    
        if count_flag:
            break
    return route


if __name__=='__main__':
    nodes = Data()
    nodes.read_solomon(path=r'r101.txt',customerNum=10)
    nodes.get_euclidean_distance_matrix()
    model = spprc_gp(nodes)
    x_set,x_i,x_j = [],[],[]
    if model.Status==2:
        for item in model.getVars():  # self.model.getVars()[i]. 
            n = list(map(int, re.findall("\d+",item.varname))) # transfer to int
            if item.x == 1:
                x_set.append(item.varname)
                x_i.append(n[0])
                x_j.append(n[1])
        if x_set:
            print('--------------------------------')
            print('obj:',-model.objVal)
            print('number of nodes:',nodes.nodeNum-2)
            print('number of meet nodes:',len(x_set)-1)
            print('capacity:',nodes.capacity)
            print('demand meet:',demand_meet(x_j,nodes))
            print('x:',x_set)
            print('route:',get_route(x_set))
            nodes.plot_route(locations=nodes.location,route=get_route(x_set),edgecolor='k')
    else:
        print('no solution!!!')














