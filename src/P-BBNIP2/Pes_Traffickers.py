import networkx as nx;
import gurobipy as gp;
from gurobipy import GRB;
from datetime import datetime;
import math;
import numpy;
from numpy import *  

def NetConverter_MFNIP(G):
    
    Gm = G.copy();
    
    for i,j in G.edges:
        if G.edges[i,j]['special'] == 1:
            Gm.edges[i,j]['capacity'] = 1;
        else:
            Gm.edges[i,j]['capacity'] = 100000; #Large value w.r.t. capacities in the net.
    
    return Gm;

def Net_traffickers(G):
    
    Gt = G.copy();
    
    for i,j in Gt.edges:
        if Gt.edges[i,j]['trafficker'] == 1:
            Gt.edges[i,j]['special'] = 1;
        else:
            Gt.edges[i,j]['special'] = 0;
    return Gt;



def Pes_Traffickers (G, s, t, budget, rate, restriction):
    
    Gt_M = NetConverter_MFNIP(Net_traffickers(G));
    
    model = gp.Model("Pessimistic_Traffickers"); 
    
    gamma = model.addVars(Gt_M.edges, vtype=GRB.BINARY); 
    
    obj = model.addVar(vtype=GRB.INTEGER, lb=0, ub=GRB.INFINITY); 
    
    x = model.addVars(Gt_M.edges, vtype=GRB.CONTINUOUS, lb = 0, ub = GRB.INFINITY);
    theta = model.addVars(Gt_M.edges, vtype=GRB.CONTINUOUS, lb = 0, ub = 1); 
    alpha = model.addVars(Gt_M.nodes, vtype=GRB.CONTINUOUS, lb = 0, ub = 1); 
    beta = model.addVars(Gt_M.edges, vtype=GRB.CONTINUOUS, lb = 0, ub = GRB.INFINITY); 


    # Restriction on Interdiction
    if restriction == 1:
        for i,j in Gt_M.edges:
            if Gt_M.edges[i,j]['trafficker'] == 1:
                model.addConstr(gamma[i,j] == 0);
            elif Gt_M.edges[i,j]['bottom'] == 1:
                model.addConstr(gamma[i,j] == 0);
                model.addConstr(gamma[j,t] == 0);
        
    elif restriction == 2:
        for i,j in Gt_M.edges:
            if i != s:
                model.addConstr(gamma[i,j] == 0);



    model.addConstr(gp.quicksum(Gt_M.edges[i,j]['cost']*gamma[i,j] for i,j in Gt_M.edges) <= budget);

    model.addConstr(alpha[t] - alpha[s] >= 1);
        
    for i,j in Gt_M.edges:
        model.addConstr(alpha[i] - alpha[j] + theta[i,j] >= 0);
        model.addConstr(beta[i,j] + gamma[i,j] - theta[i,j] >= 0);
        model.addConstr(x[i,j] - Gt_M.edges[i,j]['capacity']*(1-gamma[i,j]) <= 0);

        
    model.addConstrs(gp.quicksum(x[v,u] for u in Gt_M.successors(v)) -
                      gp.quicksum(x[u,v] for u in Gt_M.predecessors(v)) == 0 for v in Gt_M.nodes);
    
    model.addConstr(x[t,s] == obj);
        
    model.setObjective(gp.quicksum(Gt_M.edges[i,j]['capacity']*beta[i,j] for i,j in Gt_M.edges), GRB.MINIMIZE);

    T_Limit = 7200;

    model.setParam("IntegralityFocus",1);
    model.setParam('TimeLimit', T_Limit); 
    model.setParam("LogToConsole", 0)
    model.setParam("OutputFlag", 0);
    model.update();
    model.optimize();

    Gamma = {};

    for i,j in Gt_M.edges:
        Gamma[i,j] = gamma[i,j].x;

    return model.objVal, Gamma;