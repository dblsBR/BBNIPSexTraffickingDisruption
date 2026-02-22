import networkx as nx;
import gurobipy as gp;
from gurobipy import GRB;
from datetime import datetime;
import math;
import numpy;
from numpy import *  



def Net_traffickers(G):
    
    Gt = G.copy();
    
    for i,j in Gt.edges:
        if Gt.edges[i,j]['trafficker'] == 1:
            Gt.edges[i,j]['special'] = 1;
        else:
            Gt.edges[i,j]['special'] = 0;
    return Gt;



def Opt_Tra_Const (G, s, t, budget, rate, obj_victims, Gamma_Vic, restriction):
    
    Gt = Net_traffickers(G);
    
    model = gp.Model("Opt_Tra_Const"); 
    
    gamma = model.addVars(Gt.edges, vtype=GRB.BINARY); 
    
    zt = model.addVars(Gt.edges, vtype=GRB.BINARY); 
    xt = model.addVars(Gt.edges,vtype=GRB.CONTINUOUS, lb = 0, ub = GRB.INFINITY);
    thetat = model.addVars(Gt.edges, vtype=GRB.CONTINUOUS, lb = 0, ub = 1); 
    alphat = model.addVars(Gt.nodes, vtype=GRB.CONTINUOUS, lb = 0, ub = 1); 
    betat = model.addVars(Gt.edges, vtype=GRB.CONTINUOUS, lb = 0, ub = GRB.INFINITY); 

    # Restriction on Interdiction
    if restriction == 1:
        for i,j in Gt.edges:
            if Gt.edges[i,j]['trafficker'] == 1:
                model.addConstr(gamma[i,j] == 0);
            elif Gt.edges[i,j]['bottom'] == 1:
                model.addConstr(gamma[i,j] == 0);
                model.addConstr(gamma[j,t] == 0);
        
    elif restriction == 2:
        for i,j in Gt.edges:
            if i != s:
                model.addConstr(gamma[i,j] == 0);
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


    model.addConstr(gp.quicksum(Gt.edges[i,j]['cost']*gamma[i,j] for i,j in Gt.edges) <= budget);
    

    model.addConstr(xt[t,s] >= gp.quicksum(Gt.edges[i,j]['capacity']*betat[i,j] for i,j in Gt.edges));

    model.addConstr(alphat[t] - alphat[s] >= 1);
        
    for i,j in Gt.edges:
        model.addConstr(alphat[i] - alphat[j] + thetat[i,j] >= 0);
        model.addConstr(betat[i,j] + gamma[i,j] - thetat[i,j] >= 0);
        model.addConstr(xt[i,j] - Gt.edges[i,j]['capacity']*(1-gamma[i,j]) <= 0);
    
        if Gt.edges[i,j]['special'] == 1:
            model.addConstr(xt[i,j] - Gt.edges[i,j]['capacity']*zt[i,j] <= 0);
        else:
            model.addConstr(zt[i,j] == 0);
        
    model.addConstrs(gp.quicksum(xt[v,u] for u in Gt.successors(v)) -
                      gp.quicksum(xt[u,v] for u in Gt.predecessors(v)) == 0 for v in Gt.nodes);
    
    
    # Constraint on Number of Victims ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    
    z = model.addVars(G.edges, vtype=GRB.BINARY); 
    x = model.addVars(G.edges, vtype=GRB.CONTINUOUS, lb = 0, ub = GRB.INFINITY);
    theta = model.addVars(G.edges, vtype=GRB.CONTINUOUS, lb = 0, ub = 1); 
    alpha = model.addVars(G.nodes, vtype=GRB.CONTINUOUS, lb = 0, ub = 1); 
    beta = model.addVars(G.edges, vtype=GRB.CONTINUOUS, lb = 0, ub = GRB.INFINITY); 

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
        
    model.addConstr(gp.quicksum(z[i,j] for i,j in G.edges) <= obj_victims);
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    
    
    model.setObjective(gp.quicksum(zt[i,j] for i,j in Gt.edges), GRB.MINIMIZE);

    T_Limit = 7200;
    
    for i,j in G.edges:
        gamma[i,j].start = Gamma_Vic[i,j];

    model.setParam("IntegralityFocus",1);
    model.setParam('TimeLimit', T_Limit); 
    model.setParam("LogToConsole", 0)
    model.setParam("OutputFlag", 0);
    model.update();
    model.optimize();

    Gamma = {};

    for i,j in Gt.edges:
        Gamma[i,j] = gamma[i,j].x;

    return model.objVal, Gamma;