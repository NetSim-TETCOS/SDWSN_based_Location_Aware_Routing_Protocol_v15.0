####################################################################################
# Copyright (C) 2019                                                               #
# TETCOS, Bangalore. India                                                         #
#                                                                                  #
# Tetcos owns the intellectual property rights in the Product and its content.     #
# The copying, redistribution, reselling or publication of any or all of the       #
# Product or its content without express prior written consent of Tetcos is        #
# prohibited. Ownership and / or any other right relating to the software and all  #
# intellectual property rights therein shall remain at all times with Tetcos.      #
#                                                                                  #
# Author:    Dilip Kumar Kundrapu                                                  #
# Date:      16-01-2019                                                            #
# Modified:  Sreerang R   														   #
# Date:		 22-06-2026                                                            #
# ---------------------------------------------------------------------------------#

# An example script to send client request to NetSim server using socket programming in Python
import socket # for socket
import sys
import time


# This is the script for the Most Forward within Fixed Radius R (MFR) alforithm
from math import sqrt #for using sqrt() in MFR
from collections import OrderedDict #for making the dictionary as ordered


#-----------------------Functions------------------------
def _distance(a,b):
    return sqrt((b[0]-a[0])*(b[0]-a[0])+(b[1]-a[1])*(b[1]-a[1]))

def _area(a,b,c):
    return abs(  ( (a[0]*(b[1]-c[1])) + (b[0]*(c[1]-a[1])) + (c[0]*(a[1]-b[1])) ) / 2  )

def _height(a,b):
    return ((2 * a)/b)

def _projDist(a,c):
    return sqrt((c*c)-(a*a))


#-----------------------File I/P-------------------------
nodes = OrderedDict()
with open('Device_log.txt','r') as f:
    for lineno, line in enumerate(f, 1):
        line = line.strip()
        if not line:
            continue
        try:
            node_name, xpos, ypos, ipadd = line.split()
            nodes[node_name] = [float(xpos), float(ypos), ipadd]
        except Exception as e:
            print("line #{} seems broken (got {})".format(lineno, e))

#----------------------File for AppInfo-----------------
app = OrderedDict()

with open('Appinfo_log.txt','r') as f:
    for lineno, line in enumerate(f,1):
        line = line.strip()
        if not line:
            continue
        try:
            app_count, source, dest = line.split()
            app[app_count] = [source, dest]
        except Exception as e:
            print("line #{} seems broken (got {})".format(lineno, e))


#-----------------Declarations for MFR-------------------

flag = 0

for i in range(len(list(app))):
  
    source = app[list(app)[i]][flag]
    flag += 1
    dest = app[list(app)[i]][flag]
    
    tx = 170.00 #transmission range
    temp=0
    temp_node = source
    route = list()
    route.append(source)
    
    for j in range(len(list(nodes))):
        
    #to only do the computation if the current node is a route node.
        if list(nodes)[j] != temp_node:
            continue
        
        base = _distance(nodes[list(nodes)[j]],nodes[dest])
        
        for k in range(j+1,len(list(nodes))):
            result = _distance(nodes[list(nodes)[j]],nodes[list(nodes)[k]])
       

            if result <= tx:
                area = _area (nodes[list(nodes)[j]],nodes[list(nodes)[k]],nodes[dest])
                height = _height(area,base)
                projDist = _projDist(height,result)
         
            #to compare the distances and select the most forward node along the line from current node to destination
                if projDist > temp:
                    temp = projDist
                    temp_node = list(nodes)[k]
              

         

        if temp_node not in route:
            route.append(temp_node)
        if dest not in route:
            route.append(dest)
        temp = 0

    print (route)
   
   
#----------------------Socket code-----------------------
    count = 0
    node_count = 0


    for node in route:
        
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print ("Socket successfully created.")
        except socket.error as err:
            print ("Socket creation failed with error %s" %(err))

    # default port for socket
        port = 8999

        try:
            host_ip = socket.gethostbyname('127.0.0.1')
        except socket.gaierror:
            # this means could not resolve the host
             print ("Error resolving host.")
             sys.exit()

    # connecting to the server
        s.connect((host_ip, port))
        print ("Connection established to NetSim.")
       

        name ='SINK'
        name = name + '\0'
        s.send(name.encode())

             
    
#append the device name route[each]
       
        if (node_count < (len(route) - 1)):
            command = route[node_count] +  ' route ADD ' + nodes[dest][2] + ' MASK 255.255.255.255 ' + nodes[route[node_count + 1]][2] + ' METRIC 1 IF 1'
        else:
            command = route[node_count] + ' route ADD ' + nodes[dest][2] + ' MASK 255.255.255.255 ' + nodes[route[node_count]][2] + ' METRIC 1 IF 1'
        
        command = command + '\0'
        s.send(command.encode())
    #print("Command sent successfully:")
    #print ('static for ', route[each].decode('utf-8'), '=', command.decode('utf-8'))
   
        resp = s.recv(1024).decode('utf-8')
        cont = '__continue__'
        while cont not in resp:
            resp = resp + s.recv(1024).decode('utf-8')

        print ("Received:", resp)
        s.close()
    
        node_count += 1

    node_count = 0

    flag -= 1
    
   
 


       