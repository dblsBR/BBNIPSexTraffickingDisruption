import networkx as nx;
import gurobipy as gp;
from gurobipy import GRB;
import sys;
import time;
import csv;
import math;
import numpy;
from numpy import *  



def NetConverter_MFNIP(G):
    
    Gm = G.copy();
    
    for i,j in G.edges:
        if G.edges[i,j]['special'] == 1:
            Gm.edges[i,j]['capacity'] = 1;
        else:
            Gm.edges[i,j]['capacity'] = 100000; # Large value w.r.t. cpacities in the net
    
    return Gm;


def pessimistic2 (G, s, t, budget, rate, obj_Opt, restriction):
    
    Gm = NetConverter_MFNIP(G);
    
    model = gp.Model("MFNIP_Method"); 
    
    gamma = model.addVars(G.edges, vtype=GRB.BINARY); 
    
    objVal = model.addVar(vtype=GRB.INTEGER, lb = 0, ub = GRB.INFINITY);
    
    xm = model.addVars(Gm.edges, vtype=GRB.CONTINUOUS, name="xm", lb = 0, ub = GRB.INFINITY);
    thetam = model.addVars(Gm.edges, vtype=GRB.CONTINUOUS, name="thetam", lb = 0, ub = 1); 
    alpham = model.addVars(Gm.nodes, vtype=GRB.CONTINUOUS, name="alpham", lb = 0, ub = 1); 
    betam = model.addVars(Gm.edges, vtype=GRB.CONTINUOUS, name="betam", lb = 0, ub = GRB.INFINITY); 
    
    
    # Restriction on Interdiction
    if restriction == 1:
        for i,j in G.edges:
            if G.edges[i,j]['trafficker'] == 1:
                model.addConstr(gamma[i,j] == 0);
            elif G.edges[i,j]['bottom'] == 1:
                model.addConstr(gamma[i,j] == 0);
                model.addConstr(gamma[j,t] == 0);
        
    elif restriction == 2:
        for i,j in G.edges:
            if i != s:
                model.addConstr(gamma[i,j] == 0);  
    

    
    model.addConstr(alpham[t] - alpham[s] >= 1);
    
    
    for i,j in Gm.edges:
        model.addConstr(alpham[i] - alpham[j] + thetam[i,j] >= 0);
        model.addConstr(betam[i,j] + gamma[i,j] - thetam[i,j] >= 0);
        model.addConstr(xm[i,j] - Gm.edges[i,j]['capacity']*(1-gamma[i,j]) <= 0);
            
    model.addConstrs(gp.quicksum(xm[v,u] for u in Gm.successors(v)) -
                     gp.quicksum(xm[u,v] for u in Gm.predecessors(v)) == 0 for v in Gm.nodes);
    
    
    #######################################################################################
    
    ##  OPTIMISTIC CONSTRAINTS
    
    z = model.addVars(G.edges, vtype=GRB.BINARY); 
    x = model.addVars(G.edges, vtype=GRB.CONTINUOUS, lb = 0, ub = GRB.INFINITY);
    theta = model.addVars(G.edges, vtype=GRB.CONTINUOUS, lb = 0, ub = 1); 
    alpha = model.addVars(G.nodes, vtype=GRB.CONTINUOUS, lb = 0, ub = 1); 
    beta = model.addVars(G.edges, vtype=GRB.CONTINUOUS, lb = 0, ub = GRB.INFINITY); 


    model.addConstr(gp.quicksum(G.edges[i,j]['cost']*gamma[i,j] for i,j in G.edges) <= budget);

    model.addConstr(x[t,s] >= gp.quicksum(G.edges[i,j]['capacity']*beta[i,j] for i,j in G.edges));

    model.addConstr(alpha[t] - alpha[s] >= 1);

    for i,j in G.edges:
        model.addConstr(alpha[i] - alpha[j] + theta[i,j] >= 0);
        model.addConstr(beta[i,j] + gamma[i,j] - theta[i,j] >= 0);
        model.addConstr(x[i,j] - G.edges[i,j]['capacity']*(1-gamma[i,j]) <= 0);
    
        if G.edges[i,j]['special'] == 1:
            model.addConstr(x[i,j] - G.edges[i,j]['capacity']*z[i,j] <= 0);
        else:
            model.addConstr(z[i,j] == 0);
        
    model.addConstrs(gp.quicksum(x[v,u] for u in G.successors(v)) -
                      gp.quicksum(x[u,v] for u in G.predecessors(v)) == 0 for v in G.nodes);
    
    model.addConstr(gp.quicksum(z[i,j] for i,j in G.edges) <= obj_Opt);
    
    
    ######################################################################################
    
    model.addConstr(objVal == xm[t,s]);
    
    model.setObjective(gp.quicksum(Gm.edges[i,j]['capacity']*betam[i,j] for i,j in Gm.edges), GRB.MINIMIZE);
    
    model.setParam("IntegralityFocus",1);
    model.setParam("LogToConsole", 0)
    model.setParam("OutputFlag", 0);
    model.update();
    model.optimize();
    
    Gamma = {};
    
    for i,j in G.edges:
        Gamma[i,j] = gamma[i,j].x;

    return model.objVal, Gamma;
