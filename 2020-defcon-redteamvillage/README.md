## DEF CON Red Team Village CTF 2020: SSH Tunneling Masterclass

Unlike last year's DEF CON, where I hung around the Monero and Crypto/Privacy villages, I spent most of this year's DEF CON in the virtual Red Team Village. Mostly because there was no Monero CTF this year, and the Red Team CTF looked really interesting. 

For the Red Team Village CTF, there was first a qualifying round which was a typical jeopardy CTF. My team "Organizers" came 6th out of over 700 teams. The top 20 teams were selected to compete in the finals, which was definitely one of the best CTFs I've ever played. It was a red team engagement against a corporate network themed after the film [Office Space](https://en.wikipedia.org/wiki/Office_Space). Each of the 20 teams received their own environment - requiring the CTF organizers to deploy over 300 machines in total -  and we had 24 hours to hack as much of it as possible. Flags were littered all over the network, with no hints given as to where to find them. After hours of crunching through the network, we took 4th place.

![Red Team Village Finals Scoreboard](finals_scoreboard.png)

While the vulnerabilities and privilege escalations were not particularly challenging, the amount of information gathering and pivoting needed were beyond what I had experienced in any CTF before. In the final hours of the CTF, we had setup an SSH tunnel through the network from our own laptops, through Windows workstations, through Linux development boxes, through the Security Operations Centre, to the CEO's desktop!

In other words, the ability to efficiently tunnel and pivot was absolutely critical here, and we had the chance to practice it in the Qualifying round. The "Tunneler" series of challenges was by far the best part of the Qualifiers (IMO) and it tested our ability to tunnel and pivot through multiple hosts under different scenarios. It really helped solidify my knowledge of this essential but tricky area of lateral movement.

Also at the Red Team Village this year, Evan Anderson gave a [fantastic introductory talk on SSH pivoting](https://www.youtube.com/watch?v=XTaKWdIdg8g), which I recommend before reading further if you're unclear on the basics.

### 1 Bastion
> Hosts: 161.35.239.216 164.90.147.41 164.90.147.46 User: tunneler Password: tunneler SSH Port: 2222 

This warmup challenge simply involves connecting to the "bastion" host, our entry point to the internal network:
```bash
ssh tunneler@164.90.147.41 -p 2222 
tunneler@164.90.147.41's password:
```
And the login message gives us the flag.

Note that the password prompt can be automated with `sshpass`. I wouldn't recommend this in a real scenario - where you'd hopefully be using SSH pubkey authentication anyway - but it's a useful tip for CTFs:
```bash
sshpass -p tunneler ssh tunneler@164.90.147.41 -p 2222
```

### 2 Browsing Websites
> Browse to http://10.174.12.14/ 

We now need to setup a tunnel to visit a website on a host in the internal network. One way to do it would be to use a local port forwarding:
```bash
sshpass -p tunneler ssh tunneler@164.90.147.41 -p 2222 -L 1234:10.174.12.14:80
curl http://127.0.0.1:1234 # in another terminal
```
 ` -L 1234:10.174.12.14:80` sets up a forwarding of our localhost port 1234 (on our laptop), to 10.174.12.14:80. Now traffic directed to localhost port 1234 will be sent via the bastion host to the target box running a HTTP server on the internal network.
We can verify that SSH is listening on port 1234 on our own machine with `netstat`:
```
sudo netstat -tulpn | grep ssh
tcp        0      0 127.0.0.1:1234          0.0.0.0:*               LISTEN      847830/ssh          
tcp6       0      0 ::1:1234                :::*                    LISTEN      847830/ssh  
```

A more flexible solution is to setup a dynamic port forwarding via the bastion host:
```bash
sshpass -p tunneler ssh tunneler@164.90.147.41 -p 2222 -D 1080
```
Now, if we configure our browser to use localhost port 1080 as a SOCKS proxy, we can visit http://10.174.12.14/ directly in the browser. The traffic will be routed through the bastion host to the target. This option is more flexible than local port forwarding because we can visit any IP or port on the internal network with our tools as long as the tool supports using a SOCKS proxy. Local port forwarding on the other hand requires us to specify the hosts and ports we want to map up-front. Multiple `-L` options can be given for multiple local port forwards, but in many circumstances the dynamic proxy is just easier to use.

### 3 SSH in tunnels
> SSH through the bastion to the pivot. IP: 10.218.176.199 User: whistler Pass: cocktailparty

The easiest way of reaching a pivot host through a bastion host is to use a ProxyJump:
```bash
ssh -J tunneler@164.90.147.41:2222 whistler@10.218.176.199
```
With this syntax, we can "jump" through a bastion host to reach hosts that are SSH-able from it.

The challenge could also be accomplished by setting up a local port forward to port 22 on the pivot, similar to the previous challenge.

Alternatively, we could setup [proxychains](https://github.com/rofl0r/proxychains-ng) to enable Linux commands to use a dynamic proxy. After configuring proxychains to use port 1080 (in `/etc/proxychains.conf`), we can do:
```bash
ssh tunneler@164.90.147.41 -p 2222 -N -f -D 1080
proxychains ssh whistler@10.218.176.199
```
The `-N -f` flags to SSH aren't necessary; they just silently set up the dynamic proxy in the background rather than giving us a login shell on the bastion host which would clutter up the terminal.

### 4 Beacons everywhere
> Something is Beaconing to the pivot on port 58671-58680 to ip 10.112.3.199, can you tunnel it back?

Now, rather than sending traffic from our laptop through the bastion to a host on the internal network, we want to receive traffic being initiated from a host on the internal network back to our laptop.

For that, we can use remote port forwarding, the counterpart to local port forwarding:

```bash
ssh -J tunneler@164.90.147.41:2222 whistler@10.218.176.199 -R 58671:localhost:1234
nc -lvp 1234 # in another terminal
```
This command is listening on port 58671 on the pivot server, then tunneling traffic that connects to it back to our laptop on port 1234. By listening on port 1234 with netcat on our laptop, we can capture the flag.

### 5 Beacons annoying
> Connect to ip: 10.112.3.88 port: 7000, a beacon awaits you

For this challenge, we first have to connect to a particular host on the internal network on a specific port. Let's setup the dynamic proxy through the pivot, and connect using netcat through proxychains:
```bash
ssh -J tunneler@164.90.147.41:2222 whistler@10.218.176.199 -N -f -D 1080
proxychains nc 10.112.3.88 7000
```

We receive a message:
```
I hope you like tunneling, I will send you the flag on a random port... How fast is your tunnel game?
I will send the flag to ip: 10.112.3.199 on port: 12265 in 15 seconds
```
It's certainly possible to automate this, but given 15 seconds we just decided to type quickly. Using the same command as the previous challenge, we quickly typed out the listed port and entered the passwords, setting up a remote port forwarding to a netcat listener as before:
```bash
nc -lvp 1234
ssh -J tunneler@164.90.147.41:2222 whistler@10.218.176.199 -R 12265:localhost:1234
```
And the next flag shows up in the netcat stdout.

### 6 Scan me
> We deployed a ftp server but we forgot which port, find it and connect ftp: 10.112.3.207 user: bishop pass: geese

We can nmap scan every port of a host through the dynamic proxy with:
```bash
proxychains nmap -Pn 10.112.3.207 -p-
```
`-Pn` instructs nmap not to ping the target host, as ICMP is a lower-level nework protocol and won't work over a TCP tunnel.

This was extremely slow, so I took advantage of `socat` which was available on the next pivot box in the next challenge to scan from within the network:
```bash
for i in `seq 1 65535`; do socat - TCP:10.112.3.207:$i ; done 2>/dev/null
```
This is an order of magnitude faster, since packets aren't getting forwarded through multiple proxy boxes, and the machine doing the scanning is on the same network as the target.

We find the FTP server on port 53121, and it just sends the flag immediately rather than requiring us to login.

### 7 Another pivot
> Connect to the second pivot IP: 10.112.3.12 User: crease Pass: NoThatsaV

Now we have to hop through both the bastion host and the first pivot box to reach a second pivot box. The `-J` flag conveniently allows us to specify multiple chained proxy jumps:
```bash
ssh -J tunneler@164.90.147.41:2222,whistler@10.218.176.199 crease@10.112.3.12
```
When we land on the second pivot, it informs us that it's configured not to allow SSH forwarding on this box, however it does contain a local copy of `socat`.

### 8 SNMP
> There is a snmp server at 10.24.13.161

This challenge was my favourite as it required some ingenuity. We have to send SNMP traffic to a host which can only be reached from the second pivot, however we have two problems:
1) SNMP is a UDP-based protocol, but we have a TCP tunnel
2) The second pivot doesn't allow SSH port forwarding

`socat` is a powerful "multipurpose relay" tool that can substitute for the unavailability of SSH port forwarding, and can do even better by allowing us to translate TCP traffic to UDP:

```bash
socat -v TCP-LISTEN:13377,fork UDP:10.24.13.161:161
```
This listens on TCP port 13377 and forwards the traffic sent there to the target host on UDP port 161, which is the SNMP port. 
With this `socat` command running on the second pivot, we now just need to figure out how to get SNMP traffic masquerading as TCP traffic to port 13377 on the second pivot.

[This guide](http://zarb.org/~gc/html/udp-in-ssh-tunneling.html) shows a neat way to forward UDP traffic as TCP on our local machine:
```bash
mkfifo /tmp/fifo
sudo nc -l -u -p 161 < /tmp/fifo | nc localhost 1234 > /tmp/fifo
```
This netcat command listens on UDP port 161 locally and sends it via TCP to port 1234. The response from port 1234 is written to a named pipe, which is sent back as input to port 161, allowing two-way communication.

Next, we forward localhost port 1234 to port 13377 on the second pivot, using the first pivot since the second pivot doesn't allow running port forwarding commands:

```bash
ssh -J tunneler@164.90.147.41:2222 whistler@10.218.176.199 -L 1234:10.112.3.12:13377
```

Finally, we can run an SNMP walk against localhost, and it will get routed correctly to the target server!
```bash
snmpwalk -v2c -c public 127.0.0.1
```
Let's summarise what's happening here:
1) we're running an SNMP walk against localhost UDP port 161 on our laptop
2) netcat listening on UDP port 161 sends the traffic to localhost TCP port 1234, thus "wrapping" the UDP datagrams in TCP segments
3) due to the SSH local port forward, the traffic is forwarded from localhost TCP port 1234 to the second pivot server on TCP port 13377
4) on the second pivot server, socat is listening on TCP port 13377 and "unwrapping" the segments and sending them to UDP port 161 on the target host 10.24.13.161
5) The flag is sent back over the tunnel as an SNMP value

### 9 Samba
> There is a samba server at 10.24.13.10, find a flag sitting in the root file system /

SMB works over ports 139 and 445, so let's forward our local copies of these ports to the remote ones on 10.24.13.10. Because SMB is a TCP protocol, this is easier than SNMP.

As in the previous challenge, since we can't forward directly from the second pivot, let's port forward from the first pivot onto the second, then use socat to forward from the second pivot to the SMB server:

```bash
ssh -J tunneler@164.90.147.41:2222 whistler@10.218.176.199 -L 139:10.112.3.12:13376 -L 445:10.112.3.12:13377
```
```bash
ssh -J tunneler@164.90.147.41:2222,whistler@10.218.176.199 crease@10.112.3.12
socat -v TCP-LISTEN:13376,fork TCP:10.24.13.10:139 &
socat -v TCP-LISTEN:13377,fork TCP:10.24.13.10:445 
```
We can now run `smbclient` against localhost, listing the available shares on 10.24.13.10 and connecting to the one available share called `myshare`:
```bash
smbclient -L '\\127.0.0.1'
myshare
smbclient '\\127.0.0.1\myshare'
smb: \> ls
  .                                   D        0  Thu Aug  6 19:59:08 2020
  ..                                  D        0  Thu Aug  6 16:27:05 2020
  rootfs                              D        0  Thu Aug  6 16:34:57 2020
  HowElseCanYouSeeTheRootFileSystem      N        0  Thu Aug  6 16:27:08 2020
  NothingToSeeHere                    N        0  Thu Aug  6 16:27:07 2020
```

We clearly need to read what's in the rootfs, however we get access denied when trying to list it. This combined with the fact that we have wrjte access to the share suggests we can use an exploit to escalate permissions. Some googling leads to [SambaCry](https://medium.com/@bondo.mike/sambacry-rce-cve-2017-7494-41c3dcc0b7ae). After configuring the corresponding Metasploit module (`is_known_pipename()`) to attack localhost, we have RCE on the Samba server and can read the flag.

### 10 Browsing websites 2
> Browse to http://2a02:6b8:b010:9010:1::86/

We need to make an HTTP request to a server that is only available over an IPv6 connection from Pivot 2. It's surely an unintended solution, but it's easy to make HTTP requests directly using `socat`:

```
socat - TCP:[2a02:6b8:b010:9010:1::86]:80
GET /
```

Similarly to the previous challenges it's also easy to forward IPv4 traffic from our box and use `socat` at the "last mile" to send to the IPv6 address:
```bash
socat TCP4-LISTEN:13376,fork TCP6:[2a02:6b8:b010:9010:1::86]:80
```
