'''
Description:  gurobi for vrptw
Version: 1.0
Author: 71
Date: 2021-03-02 13:55:02
'''
import gurobipy as gp
from gurobipy import *
import numpy as np
from GetData import *
import time,re


def add_vrptw_st(data):
    x={}
    s={}
    model = gp.Model("VRPTW") 
    BigM = 100000
    #定义决策变量
    for k in range(data.vehicleNum):
        for i in range(data.nodeNum):
            name = 's_' + str(i) + '_' + str(k)
            s[i,k] = model.addVar(0
                                , 1500
                                , vtype= GRB.CONTINUOUS
                                , name= name)
            for j in range(data.nodeNum):
                if(i != j):
                    name = 'x_' + str(i) + '_' + str(j) + '_' + str(k)
                    x[i,j,k] = model.addVar(0
                                            , 1
                                            , vtype= GRB.BINARY
                                            , name= name)
    #更新模型
    model.update()
    #定义目标函数
    obj = LinExpr(0)
    for k in range(data.vehicleNum):
        for i in range(data.nodeNum):
            for j in range(data.nodeNum):
                if(i != j):
                    obj.addTerms(data.disMatrix[i][j], x[i,j,k])
    model.setObjective(obj, GRB.MINIMIZE)

    # s.t.1 : leave from depot once
    for k in range(data.vehicleNum):
        lhs = LinExpr(0)
        for j in range(1,data.nodeNum):
            lhs.addTerms(1, x[0,j,k])
        model.addConstr(lhs == 1, name= 'vehicle_depart_' + str(k))

    # s.t.2 : flow balance
    for k in range(data.vehicleNum):
        for h in range(1, data.nodeNum - 1):
            expr1 = LinExpr(0)
            expr2 = LinExpr(0)
            for i in range(data.nodeNum):
                if (h != i):
                    expr1.addTerms(1, x[i,h,k])
            for j in range(data.nodeNum):
                if (h != j):
                    expr2.addTerms(1, x[h,j,k])
            model.addConstr(expr1 == expr2, name= 'flow_conservation_' + str(i))
            expr1.clear()
            expr2.clear()

    # s.t.3 : comeback depot once
    for k in range(data.vehicleNum):
        lhs = LinExpr(0)
        for j in range(1,data.nodeNum - 1):
            lhs.addTerms(1, x[j, data.nodeNum-1, k])
        model.addConstr(lhs == 1, name= 'vehicle_depart_' + str(k))

    # s.t.4 : visit every custumer once
    for i in range(1, data.nodeNum - 1):
        lhs = LinExpr(0)
        for k in range(data.vehicleNum):
            for j in range(1, data.nodeNum):
                if(i != j):
                    lhs.addTerms(1, x[i,j,k])
        model.addConstr(lhs == 1, name= 'customer_visit_' + str(i))

    # s.t.5 : time windows
    for k in range(data.vehicleNum):
        for i in range(data.nodeNum):
            for j in range(data.nodeNum):
                if(i != j):
                    model.addConstr(s[i,k] + data.disMatrix[i][j] + data.serviceTime[i] - s[j,k]
                                    - BigM + BigM * x[i,j,k] <= 0 , name= 'time_windows_')

    # s.t.6 : time windows
    for i in range(1,data.nodeNum-1):
        for k in range(data.vehicleNum):
            model.addConstr(data.readyTime[i] <= s[i,k], name= 'ready_time')
            model.addConstr(s[i,k] <= data.dueTime[i], name= 'due_time')
    
    # s.t.7 : capacity limited
    for k in range(data.vehicleNum):
        lhs = LinExpr(0)
        for i in range(1, data.nodeNum - 1):
            for j in range(data.nodeNum):
                if(i != j):
                    lhs.addTerms(data.demand[i], x[i,j,k])
        model.addConstr(lhs <= data.capacity, name= 'capacity_vehicle' + str(k))

    return model


if __name__=='__main__':

    # data read
    data=GetData()
    # parameters
    data.customerNum = 25  #100
    ## read solomon data
    path = r'c101.txt'
    data.read_solomon(path,data.customerNum) 
    data.disMatrix = data.get_euclidean_distance_matrix(data.locations)
    data.nodeNum = len(data.disMatrix)
    data.vehicleNum = 20  #10

    start_time =time.time()
    model = add_vrptw_st(data) 
    model.optimize()
    end_time =time.time()

    print('\n--solving time-- :',model.Runtime)
    print('\n--running time-- :',end_time-start_time)
    print("\n-----optimal value-----")
    print('Obj:',model.ObjVal)
    print('vehicles:',data.vehicleNum)
    # model.printAttr('x')

    try:
        x_available = []
        for i in range(len(model._Model__vars)):  
            if model._Model__vars[i].Varname[0]=='x' and model._Model__vars[i].x ==1:  # take x=1 
                x_available.append(model._Model__vars[i].Varname)
        colors_ = np.random.choice(a=data.colornames, size=data.vehicleNum,replace=False)

        for i in range(data.vehicleNum):
            route_v = []
            for j in x_available:  # take vechile_x route
                n = list(map(int, re.findall("\d+",j))) # transfer to int
                if n[-1]==i:
                    n.pop()
                    route_v.append(n)
            route = [y for x in route_v for y in x]  # flatten list
            route = list(set(route))   # Eliminate the same elements
            route.append(0) # back to depot
            
            print('vehicle_{}:{}'.format(str(i),route))
            if i==data.vehicleNum-1:
                data.plot_route(data.locations,route,edgecolor=colors_[i],showoff=True)
            else:
                data.plot_route(data.locations,route,edgecolor=colors_[i],showoff=False)
    except:
        print('infeasible!')



