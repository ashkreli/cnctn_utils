# Application to SSH into multiple machines
## Code and docs by Arba Shkreli 
#### email: ashkreli@college.harvard.edu
#### GitHub: ashkreli


### Introduction
This application was born out of the need to run code already in other machines, 
particularly for experiments with many robots.
Because there could be different users, it is intractable to store SSH keys.
We also do not want to manually set a static IP for each machine, nor
have to open as many terminal windows as we have machines when "bringing up"
their resources for experiments.

### Usage
This application will connect to multiple machines via SSH when they are all
connected within the same network. The assumption is that the authentication
method is by username and password, which is the same for all machines.
Furthermore, we assume that the current and remote machines are running bash.
One SSH terminal instance is generated for each machine connected to, from
which commands can be run.

1) In terminal within the `ssh_connect` directory, type 
    `python3 connect.py`
2) Once prompted for username, type the username of the intended hosts.
    Similarly for the password. If no hosts are found, you will be
    prompted again. Make sure that your machines are currently connected
    to the network, otherwise the same set of IPs will be checked (of which
    the requested machines are not part of since they were not PING-able
    initially).
3) A list of available hosts will appear. When the prompt for the hosts
to command appears, type the ones which you want to receive the command.
The hostnames should be separated by whitespace only.
Alternatively, type `a` or `all` to command all of the listed hosts.
Full terminal output for each should become available shortly.
Note: The channel times out after 10 seconds.
4) In future host prompts, type `e` and press Enter to exit the program.
5) In future prompts for the command, type `stop` and hit Enter to stop running processes
on the target machines. Also, you can press `e` and hit Enter to exit the program.

### Design
The application first pings all of the devices on the same network as the user.
For now, 256 machines are pinged. The responsive ones are written in `available.txt`
in the same directory as `connect.py`. Afterwards, the program will try to SSH into
each machine on this list, and write all of the successful IPs in `sshable.txt` for
the user to make use of if they so choose.

The SSH session is Pythonically handled as an `SSHClient` session. The channel associated
with the client session is initialized and stored so that commands can be sent to it.
This is done when I call `invoke_shell()`, which opens a pseudo-terminal.
Note: I use `Paramiko.Channel.send()` to send commands rather than `exec_command()`,
because I encountered problems in doing so (i.e. threw an `SSHException`).
It may have to do with the devices not supporting the channel type that `exec_command()`
uses. At any rate, the workaround I used appears to work in my limited use cases.


### Future Development
The following are areas to be developed beyond the initial prototype
- Better system to specify which machines need current command. Typing is indeed cumbersome.
- We may want to add support for more SSH sessions for each machine, instead of just one
- More robustness to bad usage :)
- Pinging should be dynamic to the bandwidth of the network. Will have to consult commands
    that make this information available and parse them accordingly.

### Resources
Paramiko SSH Library for Python
https://docs.paramiko.org/en/stable/

Bash Guide for Beginners
https://tldp.org/LDP/Bash-Beginners-Guide/html/