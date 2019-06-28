#!/usr/local/bin/python3

import multiprocessing as mp 
import paramiko
import random
import subprocess
import socket
import sys
import time

def svr(output, server, server_user, server_password):
    iperf3="/usr/local/bin/iperf3"
    ssh = paramiko.SSHClient()#ssh object client creation
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(server,  username=server_user, password=server_password)
    stdin, stdout, stderr = ssh.exec_command("ls /usr/local/bin/iperf3")
    if len(stderr.readlines()) != 0: 
        iperf3="/usr/bin/iperf3"
    
    print ("Starting the server at : ", server)
    stdin, stdout, stderr = ssh.exec_command("{} -s -i 1 -1".format(iperf3))
    #output.put("Connection to server established!\n\n")
    opt = stdout.readlines()
    opt = "".join(opt)
    output.put(opt)
   
def cli(output, client, client_user, client_password):
    time.sleep(5)
    iperf3="/usr/local/bin/iperf3"
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(client,  username=client_user, password=client_password)
    stdin, stdout, stderr = ssh.exec_command("ls /usr/local/bin/iperf3")
    
    if len(stderr.readlines()) != 0: 
        iperf3="/usr/bin/iperf3"
    
    print("Connecting to: ", server, "from client: ", client)
    stdin, stdout, stderr = ssh.exec_command("{} -c {} -i 1 -t 120 -R -b 0 -P 1 -O 2".format(iperf3, server))
    print("\n\nConnection to the client established\n\n")
    opt = stdout.readlines()
    opt = "".join(opt)
    output.put(opt)

def jitter(client, client_user, client_password, server):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(client,  username=client_user, password=client_password)

    stdin, stdout, stderr = ssh.exec_command("ping -c 10 {}".format(server))
    print("started ping...")
    exit_status = stdout.channel.recv_exit_status()

    opt=stdout.readlines()
    rtt=opt[len(opt)-1].split("=")
    print(rtt)
    print("jitter: {}".format(rtt[1].split("/")[3].split(" ")[0]))
if __name__ == '__main__':

    random.seed(123)
    
    server=sys.argv[1]
    server_user=sys.argv[2]
    server_password=sys.argv[3]
    client=sys.argv[4]
    client_user=sys.argv[5]
    client_password=sys.argv[6]

    
    output = mp.Queue()#creating a queue data structure to be used as channel in our multiprocess communication

    processes = [mp.Process(target=svr, args=(output, server, server_user, server_password)), mp.Process(target=cli, args=(output, client, client_user, client_password))]
    
    for p in processes:
        p.start()
    
    for p in processes:
        print(output.get())
    jitter(client, client_user, client_password, server) 
