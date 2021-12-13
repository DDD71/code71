# _*_coding:utf-8 _*_
from __future__ import print_function
from gurobipy import *
from GetData import *
import matplotlib.pyplot as plt
import numpy as np
import time



def VRPTW_RMP(Graph):
        
    RMP = Model('RMP') 
    customerNum = Graph.customerNum 
    path_set = {} 
    # define decision variable 
    y = {}
    for  i in range(customerNum):
        var_name = 'y_' + str(i)
        y[i] = RMP.addVar(lb = 0, ub = 1, obj = round(Graph.disMatrix[0][i] + Graph.disMatrix[i][0], 1), vtype = GRB.CONTINUOUS, name = var_name) 
        path_set[var_name] = [0, i + 1, Graph.nodeNum - 1]  

    RMP.setAttr('ModelSense',GRB.MINIMIZE)

    rmp_con = [] 
    row_coeff = [1] * customerNum
    for i in range(customerNum): 
        rmp_con.append(RMP.addConstr(y[i] == 1)) 
        
    # set objective function 
    # RMP.write('RMP.lp') 
    # RMP.setParas('')
    RMP.optimize()

    rmp_pi = RMP.getAttr("Pi", RMP.getConstrs()) 
    rmp_pi.insert(0, 0) 
    rmp_pi.append(0) 
    return RMP,rmp_pi,rmp_con,path_set
    
def VRPTW_SPP(Graph,rmp_pi):
    # build subproblem 
    SP = Model('SP') 
    # decision variables
    x = {}
    s = {}
    # mu = {} 
    big_M = 1e5 
    for i in range(Graph.nodeNum): 
        name = 's_' + str(i) 
        s[i] = SP.addVar(lb = Graph.readyTime[i], 
                        ub = Graph.dueTime[i],
                        vtype = GRB.CONTINUOUS,
                        name = name)
        for j in range(Graph.nodeNum): 
            if(i != j):
                name = 'x_' + str(i) + '_' + str(j)
                x[i, j] = SP.addVar(lb = 0,
                                    ub = 1,
                                    vtype = GRB.BINARY,
                                    name = name) 

    # set objective function of SP 
    sub_obj = LinExpr(0)
    for key in x.keys():
        node_i = key[0]
        node_j = key[1] 
        sub_obj.addTerms(Graph.disMatrix[node_i][node_j], x[key])
        sub_obj.addTerms(-rmp_pi[node_i], x[key]) 

    SP.setObjective(sub_obj, GRB.MINIMIZE)

    # constraints 1 
    lhs = LinExpr(0)
    for key in x.keys():
        node_i = key[0]
        node_j = key[1] 
        lhs.addTerms(Graph.demand[node_i], x[key])
    SP.addConstr(lhs <= Graph.capacity, name = 'cons_1')

    # constraints 2 
    lhs = LinExpr(0)
    for key in x.keys():
        if(key[0] == 0):
            lhs.addTerms(1, x[key])
    SP.addConstr(lhs == 1, name = 'cons_2')  

    # constraints 3
    for h in range(1, Graph.nodeNum - 1):
        lhs = LinExpr(0)
        for i in range(Graph.nodeNum):
            temp_key = (i, h) 
            if(temp_key in x.keys()):
                lhs.addTerms(1, x[temp_key])
        for j in range(Graph.nodeNum): 
            temp_key = (h, j)  
            if(temp_key in x.keys()):
                lhs.addTerms(-1, x[temp_key]) 
        SP.addConstr(lhs == 0, name = 'cons_3') 
        
    # constraints 4 
    lhs = LinExpr(0)
    for key in x.keys():
        if(key[1] == Graph.nodeNum - 1): 
            lhs.addTerms(1, x[key])
    SP.addConstr(lhs == 1, name = 'cons_4')  

    # constraints 5 
    for key in x.keys():
        node_i = key[0]
        node_j = key[1]
        SP.addConstr(s[node_i] + Graph.disMatrix[node_i][node_j] - s[node_j] - big_M + big_M * x[key] <= 0, name = 'cons_5')
    
    SP.optimize() 

    return SP,x


def get_new_path(Graph,x):
    '''
    @description: get new path from SPP model
    '''    
    new_path = []
    current_node = 0 
    new_path.append(current_node) 
    path_length = 0
    while(current_node != Graph.nodeNum - 1):   
        for key in x.keys():
            if(x[key].x > 0 and key[0] == current_node):
                current_node = key[1]
                new_path.append(current_node) 
                path_length += Graph.disMatrix[key[0]][key[1]]
    return new_path,path_length



if __name__=='__main__':

    # reading data
    Graph = Data()
    path = 'r101.txt'  
    Graph.read_solomon(path='c101.txt',customerNum=25)             
    Graph.get_euclidean_distance_matrix()
    # Graph.vehicleNum = 20      
    s_time = time.time()

    RMP,rmp_pi,rmp_con,path_set = VRPTW_RMP(Graph)
    SP,x = VRPTW_SPP(Graph,rmp_pi)

    RMP.setParam("OutputFlag", 0)
    SP.setParam("OutputFlag", 0) 
    #solve SP 
    SP.optimize()
    eps = -0.01 
    cnt = 0 
    while(SP.ObjVal < eps):
        cnt += 1
        print('--------cnt={}---------- '.format(cnt))
        '''
        ADD NEW COLUMN 
        '''
        new_path,path_length = get_new_path(Graph,x)
        path_length = round(path_length,2)

        # creat new column 
        col_coef = [0] * Graph.customerNum
        for key in x.keys():
            if(x[key].x > 0):
                node_i = key[0]
                if(node_i > 0 and node_i < Graph.nodeNum - 1):
                    col_coef[node_i - 1] = 1  

        print('new path length :', new_path)
        print('new path length :', path_length)
        print('new column :', col_coef)

        # Update RMP
        rmp_col = Column(col_coef, rmp_con) 
        var_name = "cg_" + str(cnt)
        RMP.addVar(lb = 0.0, ub = 1, obj = path_length, vtype = GRB.CONTINUOUS, name = var_name, column = rmp_col)
        RMP.update() 
        path_set[var_name] =  new_path    

        print('current column number :', RMP.NumVars) 
        RMP.write('RMP.lp') 
        RMP.optimize() 
        
        # get the dual variable of RMP constraints 
        rmp_pi = RMP.getAttr("Pi", RMP.getConstrs()) 
        rmp_pi.insert(0, 0) 
        rmp_pi.append(0) 
        
        # Update objective of SP 
        sub_obj = LinExpr(0)
        for key in x.keys():
            node_i = key[0]
            node_j = key[1] 
            sub_obj.addTerms(Graph.disMatrix[node_i][node_j], x[key])
            sub_obj.addTerms(-rmp_pi[node_i], x[key]) 

        SP.setObjective(sub_obj, GRB.MINIMIZE)
        SP.optimize()
        print('reduced cost :', SP.ObjVal) 

    mip_var = RMP.getVars()
    for i in range(RMP.numVars): 
        mip_var[i].setAttr("VType", GRB.INTEGER)  
    RMP.optimize() 
    print('--------------------------------')
    print('RMP.ObjVal :',RMP.ObjVal)
    for var in RMP.getVars():
        if(var.x > 0):
            print(var.VarName, ' = ', var.x, '\t path :', path_set[var.VarName])  

    print('time cost:',time.time()-s_time)
            

