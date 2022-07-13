import subprocess, os, pathlib
from paramiko import AuthenticationException, AutoAddPolicy, BadHostKeyException, SSHClient, SSHException
from getpass import getpass
import socket
import multiprocessing as mp
import datetime, time
from time import sleep
import readline

# Find own IP to take part containing domain that we will be
# looking for other machines in
local_ip = subprocess.run(["hostname", "-I"], capture_output=True)
local_ip = str(local_ip.stdout.decode())
local_ip = local_ip.strip()

# Truncate own IP to extract common part for all other candidate ones
front = local_ip[0:local_ip.rfind('.')]
front = front + "."

# Obtain path to 'ping.sh' so it can be executed
ping_path = str(pathlib.Path(__file__).parent.resolve()) + "/ping.sh"
to_ping = [ping_path]
# Change permissions of 'ping.sh' so that it can execute
subprocess.call(["chmod", "u+x", ping_path])

# Generate all IPs that will be ping-ed
for i in range(0, 255):
    to_ping.append(front + str(i))

# Ping all IPs - available machines are listed in 'available.txt'
subprocess.run(to_ping)

available = []

# Best way to open a file - don't need to worry about closing
with open('available.txt', 'r') as file:
    for line in file:
        available.append(line.strip())

servers = []
while len(servers) == 0:
    user = str(input("Server Username: "))
    pw = getpass("Server Password: ")
    servers = []
    with open("sshable.txt", "w") as file:
        for ip in available:
            try:
                client_tmp = SSHClient()
                client_tmp.load_system_host_keys()
                client_tmp.set_missing_host_key_policy(AutoAddPolicy())
                # print("Trying to connect to " + ip)
                client_tmp.connect(ip, username=user, password=pw, allow_agent=False, look_for_keys=False, timeout=2.0)
            except (BadHostKeyException, AuthenticationException, 
                    SSHException, socket.error) as e:
                client_tmp.close()
                continue
            file.write(ip + "\n")
            servers.append(client_tmp)
    if len(servers) == 0:
        print("No hosts under those credentials - try again")

# Pull out all names of available hosts by sending 
# 'hostname -I' command
# hosts format: {hostname (str): client (SSHClient), shell}
hosts = {}
for server in servers:
    stdin, stdout, stderr = server.exec_command("hostname")
    hostname = stdout.read().decode().strip()
    # store channel associated with client session
    channel = server.invoke_shell()
    hosts[hostname] = server, channel

# Runs a command on a given channel - returns terminal stream
def run_cmd(channel, command):
    try:
        while not channel.send_ready():
            sleep(1.0)
        channel.send(command + '\n')
        channel.settimeout(10.0)
        out = channel.recv(1024).decode("utf-8")
        print(out)
        while len(out) > 0:
            try:
                out = channel.recv(1024).decode("utf-8")
                print(out)
            except socket.timeout:
                break
    except SSHException:
        print("Request rejected or channel closed")

# Execute commands on any or all of the host machines
while True:
    print("Available hosts: " + str(list(hosts.keys())))
    print("If you wish to exit, press 'e' and hit Enter")
    print("To send command to all hosts, type 'a' or 'all'")
    hosts_to_command = input("Host(s) to command: ")
    hosts_to_command = hosts_to_command.lower().strip()
    if hosts_to_command == "e":
        break
    elif hosts_to_command == "a" or hosts_to_command == "all":
        hosts_to_command = list(hosts.keys())
    else:
        hosts_to_command = hosts_to_command.replace(',', ' ')
        hosts_to_command = hosts_to_command.split()
        for host in hosts_to_command:
            if host not in hosts:
                print(host + " not a connected host")
                hosts_to_command.remove(host)
        if len(hosts_to_command) == 0:
            continue
    print("If you wish to stop a running process on a given machine, type 'stop' and hit Enter")
    command = input("Input command: ")
    if command != "" and command != "e" and command != "stop":
        for host in hosts_to_command:
            print("Host running: " + host)
            process = mp.Process(target=run_cmd(hosts[host][1], command))
            process.start()
            process.join()
    elif command == "e":
        break
    elif command == "stop":
        for host in hosts_to_command:
            print("Host running: " + host)
            process = mp.Process(target=run_cmd(hosts[host][1], "\x03"))
            process.start()
            process.join()

for server in servers:
    server.close()