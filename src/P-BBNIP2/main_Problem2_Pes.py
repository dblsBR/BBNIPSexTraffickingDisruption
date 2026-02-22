import networkx as nx;
import gurobipy as gp;
from gurobipy import GRB;
import sys;
import time;
from datetime import datetime;
import csv;
import math;
import numpy;
from numpy import *;

from readNet import*;
from Pes_Victims import*;
from Pes_Traffickers import*;
from Pes_Vic_Const import*;
from Pes_Tra_Const import*;

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



#  main  

nNets = 5;

Budget = [32, 40, 48, 56, 64];
Rate = [0.1, 0.4, 0.7, 1];


# Define restrictions on interdiction:
# restriction = 0 (No Restriction)
# restriction = 1 (Can only remove Victims)
# restriction = 2 (Can only remove Traffickers)

restriction = 0;



for n in range(1, nNets+1):
    
    # ------- Set the Network Instances -----------------------
    
    # ------ Different Capacities
    network = "Networks/DifferentCapacities/Net10_"+str(n)+"_DifCap.csv";
    Name = "Results/Results_"+str(n)+"/DifferentCapacities/Results_P-BBNIP2_"+str(n)+"_.csv"
    print('\n\nDifferent Capacities\n')
    
    # # ------ Same Capacities
    # network = "Networks/SameCapacities/Net10_"+str(n)+"_SameCap.csv";
    # Name = "Results/Results_"+str(n)+"/SameCapacities/Results_P-BBNIP2_"+str(n)+"_.csv"
    # print('\n\nSame Capacities\n')
    
    # # ------ Operations Same Capacities
    # network = "Networks/OperationsSameCapacities/Net10_"+str(n)+"_OpSameCap.csv";
    # Name = "Results/Results_"+str(n)+"/OperationsSameCapacities/ResultsP-BBNIP2_"+str(n)+"_.csv"
    # print('\n\nOperations Same Capacities\n')
    
    
    file = open(Name, "w");
    file.write('Instance,Budget,Rate,PF_points, Time\n');
    file.close();
    
    # ----------------------------------------------------------------------------------------

    file = open(Name, "w");
    file.write('Instance,Budget,Rate,PF_points, Time\n');
    file.close();  

    
    G, s, t, nVictims, nTraffickers, nBottoms = readNet(network);

    for budget in Budget:
        
        
        for rate in Rate:
            
            now = datetime.now();
            
            start = time.time();
            
            G_r = G.copy();
            
            for i in G.successors(s):
                    G_r.edges[s,i]['capacity'] = math.floor(rate*G.edges[s,i]['capacity']);
            
            Gt = Net_traffickers(G_r);
            
            
            obj_victims, Gamma_Vic = Pes_Victims (G_r, s, t, budget, rate, restriction);
            
            obj_traffickers, Gamma_Tra = Pes_Traffickers (G_r, s, t, budget, rate, restriction);
            
            obj_vic_const, Gamma_Vic_Const = Pes_Vic_Const (G_r, s, t, budget, rate, obj_traffickers, Gamma_Tra, restriction);
            
            obj_tra_const, Gamma_Tra_Const = Pes_Tra_Const (G_r, s, t, budget, rate, obj_victims, Gamma_Vic, restriction);


            print('\nNet = %g, Budget = %g, Rate = %g\n' %(n, budget, rate));
    
            if restriction == 0:
                print('\nNo Restriction on Interdiction!\n')
                
            elif restriction == 1:
                print('\nCan Only Remove Victims!\n')
                
            elif restriction == 2:
                print('\nCan Only Remove Traffickers!\n')
            

            delta = obj_tra_const - obj_traffickers;
                
            if delta == 0:
                PF_points = 1;
                print('Only 1 PF Point:');
                print('PF Point (Victims, Traffickers) = (%d, %d)\n' %(obj_vic_const, obj_traffickers));
                
            elif delta == 1:
                PF_points = 2;
                print('Only 2 PF Points:');
                print('PF Point1 (Victims, Traffickers) = (%d, %d)' %(obj_vic_const, obj_traffickers));
                print('PF Point2 (Victims, Traffickers) = (%d, %d)\n' %(obj_victims, obj_tra_const));
                
            else:
                PF_points = 2;
                print('Multiple PF Points\n');
                print('PF Point (Victims, Traffickers) = (%d, %d)\n' %(obj_vic_const, obj_traffickers));
                
                TEMP_Vic = [];
                TEMP_Tra = [];
                
                TEMP_GAMMA = {};
                
                temp_tra = obj_traffickers + 1;
                
                ctr = 0;
                
                while temp_tra < obj_tra_const:    
                    
                    temp_vic, Gamma_temp = Pes_Vic_Const(G_r, s, t, budget, rate, temp_tra, Gamma_Tra, restriction);
                    
                    if temp_vic <= obj_vic_const-1 and temp_vic not in TEMP_Vic: 
                        print('\nPF Point (Victims, Traffickers) = (%d, %d)\n' %(temp_vic, temp_tra));
                        
                        TEMP_Vic.append(temp_vic);
                        TEMP_Tra.append(temp_tra);
                        TEMP_GAMMA[ctr] = Gamma_temp;
                        
                        ctr += 1;
                        PF_points += 1;
                    else:
                        print("\nDominated point!\n")
                    
                    temp_tra += 1;
                
                print('PF Point (Victims, Traffickers) = (%d, %d)\n' %(obj_victims, obj_tra_const));
            
            del G_r;
            
            end = time.time();
            
            runTime = round(end - start, 2);
            
            ##################################################################
            
            # ------ Different Capacities
            Name1 = "Results/Results_"+str(n)+"/DifferentCapacities/Results_P-BBNIP2_Network_"+str(n)+"_"+str(budget)+"_"+str(rate)+".txt";
            
            # # ------- Same Capacities
            # Name1 = "Results/Results_"+str(n)+"/SameCapacities/Results_P-BBNIP2_Network_"+str(n)+"_"+str(budget)+"_"+str(rate)+".txt";
            
            # # --------- Operations Same Capacities
            # Name1 = "Results/Results_"+str(n)+"/OperationsSameCapacities/Results_P-BBNIP2_Network_"+str(n)+"_"+str(budget)+"_"+str(rate)+".txt";
            
            #######################################################################################################
            
            file2 = open(Name1, "w");
            file2.write('Instance %s, Budget %g, Rate %g\n' %(network, budget, rate));
            file2.write('Instance executed at: %s \n' %now.strftime("%c"));
            
            if restriction == 0:
                file2.write('\nNo Restriction on Interdiction!\n')
                
            elif restriction == 1:
                file2.write('\nCan Only Remove Victims!\n')
                
            elif restriction == 2:
                file2.write('\nCan Only Remove Traffickers!\n')
            
            file2.write('\nPareto Point: (%g, %g)\n' %(obj_vic_const, obj_traffickers))
            file2.write('Interdiction:\n')
            
            for i,j in G.edges:
                if Gamma_Vic_Const[i,j] > 0.0001:
                    if G.edges[i,j]['trafficker'] == 1:
                        file2.write('(%g, %g), %s\n' %(i,j, 'Trafficker'));
                    elif G.edges[i,j]['bottom'] == 1:
                        file2.write('(%g, %g), %s\n' %(i,j, 'Bottom'));
                    elif G.edges[i,j]['victim'] == 1:
                        file2.write('(%g, %g), %s\n' %(i,j, 'Victim'));
                    else:
                        file2.write('(%g, %g), %s\n' %(i,j, 'Problem with classification of arcs!'));
                        
            if delta == 0:
                file2.close(); 
                
            elif delta == 1:
                file2.write('\nPareto Point: (%g, %g)\n' %(obj_victims, obj_tra_const))
                file2.write('Interdiction:\n')
                for i,j in G.edges:
                    if Gamma_Tra_Const[i,j] > 0.0001:
                        if G.edges[i,j]['trafficker'] == 1:
                            file2.write('(%g, %g), %s\n' %(i,j, 'Trafficker'));
                        elif G.edges[i,j]['bottom'] == 1:
                            file2.write('(%g, %g), %s\n' %(i,j, 'Bottom'));
                        elif G.edges[i,j]['victim'] == 1:
                            file2.write('(%g, %g), %s\n' %(i,j, 'Victim'));
                        else:
                            file2.write('(%g, %g), %s' %(i,j, 'Problem with classification of arcs!'));
                
                file2.close();        
                
            else:
                it = 0;
                while len(TEMP_Tra) >= 1:
                    
                    file2.write('\nPareto Point: (%g, %g)\n' %(TEMP_Vic.pop(0), TEMP_Tra.pop(0)))
                    file2.write('Interdiction:\n')
                    
                    for i,j in G.edges:
                        if TEMP_GAMMA[it][i,j] > 0.0001:
                            if G.edges[i,j]['trafficker'] == 1:
                                file2.write('(%g, %g), %s\n' %(i,j, 'Trafficker'));
                            elif G.edges[i,j]['bottom'] == 1:
                                file2.write('(%g, %g), %s\n' %(i,j, 'Bottom'));
                            elif G.edges[i,j]['victim'] == 1:
                                file2.write('(%g, %g), %s\n' %(i,j, 'Victim'));
                            else:
                                file2.write('(%g, %g), %s\n' %(i,j, 'Problem with classification of arcs!'));
                    

                    it += 1;
                
                file2.write('\nPareto Point: (%g, %g)\n' %(obj_victims, obj_tra_const))
                file2.write('Interdiction:\n')
                for i,j in G.edges:
                    if Gamma_Tra_Const[i,j] > 0.0001:
                        if G.edges[i,j]['trafficker'] == 1:
                            file2.write('(%g, %g), %s\n' %(i,j, 'Trafficker'));
                        elif G.edges[i,j]['bottom'] == 1:
                            file2.write('(%g, %g), %s\n' %(i,j, 'Bottom'));
                        elif G.edges[i,j]['victim'] == 1:
                            file2.write('(%g, %g), %s\n' %(i,j, 'Victim'));
                        else:
                            file2.write('(%g, %g), %s' %(i,j, 'Problem with classification of arcs!'));
                
                file2.close();        
            
            
            write = [n, budget, rate, PF_points, runTime];
            with open(Name, 'a', newline='') as csvfile:
                csvwriter = csv.writer(csvfile);
                csvwriter.writerow(write);
                csvfile.close();