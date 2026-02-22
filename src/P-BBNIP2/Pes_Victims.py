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


def Pes_Victims (G, s, t, budget, rate, restriction):
    
    
    Gm = NetConverter_MFNIP(G);
    
    model = gp.Model("Pessimistic_Victims"); 
    
    gamma = model.addVars(G.edges, vtype=GRB.BINARY); 
    
    obj = model.addVar(vtype=GRB.INTEGER, lb=0, ub=GRB.INFINITY); 
    
    x = model.addVars(Gm.edges, vtype=GRB.CONTINUOUS, lb = 0, ub = GRB.INFINITY);
    theta = model.addVars(Gm.edges, vtype=GRB.CONTINUOUS, lb = 0, ub = 1); 
    alpha = model.addVars(Gm.nodes, vtype=GRB.CONTINUOUS, lb = 0, ub = 1); 
    beta = model.addVars(Gm.edges, vtype=GRB.CONTINUOUS, lb = 0, ub = GRB.INFINITY); 
    
    
    # Restriction on Interdiction
    if restriction == 1:
        for i,j in G.edges:
            if Gm.edges[i,j]['trafficker'] == 1:
                model.addConstr(gamma[i,j] == 0);
            elif Gm.edges[i,j]['bottom'] == 1:
                model.addConstr(gamma[i,j] == 0);
                model.addConstr(gamma[j,t] == 0);
        
    elif restriction == 2:
        for i,j in Gm.edges:
            if i != s:
                model.addConstr(gamma[i,j] == 0);


    model.addConstr(gp.quicksum(Gm.edges[i,j]['cost']*gamma[i,j] for i,j in Gm.edges) <= budget);

    model.addConstr(alpha[t] - alpha[s] >= 1);
    

    for i,j in Gm.edges:
        model.addConstr(alpha[i] - alpha[j] + theta[i,j] >= 0);
        model.addConstr(beta[i,j] + gamma[i,j] - theta[i,j] >= 0);
        model.addConstr(x[i,j] - Gm.edges[i,j]['capacity']*(1-gamma[i,j]) <= 0);
        
    model.addConstrs(gp.quicksum(x[v,u] for u in Gm.successors(v)) -
                      gp.quicksum(x[u,v] for u in Gm.predecessors(v)) == 0 for v in Gm.nodes);
        
    model.addConstr(x[t,s] == obj);
    
    model.setObjective(gp.quicksum(Gm.edges[i,j]['capacity']*beta[i,j] for i,j in Gm.edges), GRB.MINIMIZE);

    T_Limit = 7200;

    model.setParam("IntegralityFocus",1);
    model.setParam('TimeLimit', T_Limit); 
    model.setParam("LogToConsole", 0)
    model.setParam("OutputFlag", 0);
    model.update();
    model.optimize();

    Gamma = {};

    for i,j in G.edges:
        Gamma[i,j] = gamma[i,j].x;

    return model.objVal, Gamma;