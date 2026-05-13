### Run the API Gateway Copy Location

In order to launch the Client Portal Gateway, you must execute a set of commands through the Windows Command Prompt or Unix Terminal. This can not be done through the default file explorer. The API gateway is meant to be run on a local machine. As such, attempting to operate the gateway on a separate machine from where commands are generated may result in the issues and is not a supported practice by Interactive Brokers.

By default, the gateway will listen on port 5000. Clients can however change this to any available port on their device by modifying the listenPort field in the gateway configuration file ‘conf.yaml’, found in the ‘root’ directory of the gateway.

After successfully running the gateway, you may proceed through the [Authentication](#authentication) steps before proceeding to calling your requested endpoints.

Using the terminal, Find and open the unzipped Client Portal Gateway directory.

For example, assume my Client Portal Gateway directory is in the Windows *C:/Users/Example/Downloads/* , then I can run the following command to change to the directory:

`cd C:/Users/Example/Downloads/clientportal.gw`

After that, on Windows, launch the gateway using the following command:

`bin\run.bat root\conf.yaml`

And in the case of Unix systems:

`bin/run.sh root/conf.yaml`
