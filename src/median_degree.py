import pandas as pd
import numpy as np
import csv
import datetime
import sys

#read in the file in basic format
f=open(sys.argv[1])
pay=list(csv.reader(f))
w=open(sys.argv[2],'w')

#three columns in the dataframe
date=[]
sender=[]
receiver=[] 

# clear the data by just filtering the actor,target, and time
#change time to python format datetime

for row in pay:
    time=row[0].replace("{\"created_time\": \"","")
    time=time.replace("\"","")
    
    rece=row[1].replace(" \"target\": \"","")
    rece=rece.replace("\"","")
    
    send=row[2].replace(" \"actor\": \"","")
    send=send.replace("\"}","")
    time=datetime.datetime.strptime(time,"%Y-%m-%dT%H:%M:%SZ")
    
    date.append(time)
    sender.append(send)
    receiver.append(rece)

d={'time':date,'sender':sender,'receiver':receiver}
df=pd.DataFrame(d)

#create the dataframe
df.shape

#import the networkx as a graph based analyzing tools
import networkx as nx
G=nx.Graph()

G.clear()
time_lis=[]
edge_lis=[]
node_lis=[]

#time_lis is the list of tuples (i,time), where i is row index.
# here I guarantee that the time_lis is within the 60 sec time window.
#edge_lis is edge tuples in the graph, 
#node_lis is nodes in graph. These lists are all within 60 secs time window.

for i in range(df.shape[0]):
    t = df.time.iloc[i]
# this control the case where only case1 happens, directly remove the incoming payment.
# other cases, add the incoming payment into the 60 sec time_lis window.
    ctrl=True 
 
#    print(i)
    #only works for the fist data, t_min and t_max is min and max time in time_lis.
    if i==0:
        t_min = t 
        t_max = t
        time_lis.append((i,t))

# the 5 cases for the incoming payment, depending on the previous time_lis.
    t1=int((t-t_max).total_seconds())
    t2=int((t-t_min).total_seconds())

    if i>0:    
        #when incoming time is smaller than (t_max-60) sec, ignore this
        if t1<=-60:
            print('case 1')
            ctrl=False
            pass
        #when incoming time is larger than (t_max+60) sec, only use this time
        if t1>=60:
            print('case 2')
            time_lis=[]
            time_lis.append((i,t))
        #when incoming time is between t_min and t_max, add this time
        if (t1 <=0) & (t2>=0):
            print('case 3')
            time_lis.append((i,t))
        # when incoming time is larger than t_max, but not in case 2, need to truncate time_lis
        if (t1 >0) & (t1 <60):
            print('case 4')
            time_lis.append((i,t))            
            t_max=t
            copy_time_lis=list(time_lis)
        # truncate the time_lis, edge_lis and node_lis, 
        # if old time_lis has some time larger than 60 sec older of incoming time,remove it.
        #since time_lis is list of tuple, j[1] is time, j[0] is index. 
            for j in copy_time_lis:
                if int((t_max-j[1]).total_seconds())>=60:
                    time_lis.remove(j)
                    edge_lis.remove((df.receiver.iloc[j[0]],df.sender.iloc[j[0]]))
                    node_lis.remove(df.receiver.iloc[j[0]])
                    node_lis.remove(df.sender.iloc[j[0]])
        # case 5, incoming time is less than t_min, but still within t_max and t_max-60                    
        if (t2 <0) & (t1 > -60):
            print('case 5')
            time_lis.append((i,t))
#final_t_lis is removing index in previous time_lis.                
    final_t_lis=[]
    for k in time_lis:
        final_t_lis.append(k[1])        
    final_t_lis.sort()
#    print(final_t_lis) 
# check that the time interval in the final_t_lis is between 60 secs.
    t_min=final_t_lis[0]
    t_max=final_t_lis[len(time_lis)-1]
    t_inter=int((t_max-t_min).total_seconds())
# if not, print out error message for debug
    if t_inter>60:
        print('error',int((t_max-t_min).total_seconds()))
#except case 2, all other cases need to add the new incoming time.    
    if ctrl==True:
        tup=(df.receiver.iloc[i],df.sender.iloc[i])
        edge_lis.append(tup)    
        node_lis.append(df.receiver.iloc[i])
        node_lis.append(df.sender.iloc[i])
# use the network graphs,after add in nodes and edges lists.
# I double check that if a edge or node is added twice, it will not be counted twice for the vertex median.
# another method is use python dictionary to loop through the nodes list, 
# use the names of receiver or sender as the key and value for vertex degree.
    G.clear()
    G.add_nodes_from(node_lis)
    G.add_edges_from(edge_lis)
    degree=list(G.degree(node_lis).values())
#    print(sorted(degree))    
    med = np.median(degree)
    print("%.2f" %med)

    w.write("%.2f" %med)
    w.write("\n")

