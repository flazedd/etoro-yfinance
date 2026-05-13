### How To Modify The Client Portal Gateway Port Copy Location

In some cases, a user may need to modify the port for their Client Portal Gateway. This most often arises because another process is already occupying Localhost port 5000.

To modify your port:

1. (Optional) Close the Client Portal Gateway if it is already running
2. Navigate to your Client Portal Gateway directory, such as /Users/my\_user/cpgw
3. Enter the ./root directory to edit your conf.yaml file
4. Modify “listenPort” on line 4 from “5000” to the value of your choice.

- Port “5001” is a standard alternative that is not typically in use.

5. Save the content of the file and launch the Client Portal Gateway

```
ip2loc: "US"
proxyRemoteSsl: true
proxyRemoteHost: "https://api.ibkr.com"
listenPort: 5001
listenSsl: true
ccp: false
svcEnvironment: "v1"
sslCert: "vertx.jks"
sslPwd: "mywebapi"
authDelay: 3000
portalBaseURL: ""
serverOptions:
    blockedThreadCheckInterval: 1000000
    eventLoopPoolSize: 20
    workerPoolSize: 20
    maxWorkerExecuteTime: 100
    internalBlockingPoolSize: 20
webApps:
    - name: "demo"
      index: "index.html"
cors:
    origin.allowed: "*"
    allowCredentials: false
ips:
  allow:
    - 192.*
  deny:
```
