### Client Portal Gateway FAQ Copy Location

###### Copy Location

Q:

###### Why is my browser saying I have an insecure connection? Why are my requests being rejected because of an invalid SSL certificate?

A:

When navigating to the Client Portal API Gateway login page, you may see a warning from your browser regarding a missing valid SSL certificate. This is expected. The API gateway does not come bundled with a valid certificate and it is up to the user to install one signed by themselves.

**Note:** It is important to note that the connection is only insecure between the user to their own localhost. In other words, only the connection on the local computer is insecure. However, requests sent from the locahost to Interactive Brokers will maintain a secure connection.

###### Copy Location

Q:

###### Can I automate the Client Portal API Gateway authentication process?

A:

There is currently no mechanism available on Interactive Brokers’ end to permit individual clients to automate the brokerage session authentication process when using Client Portal API. Interactive Brokers does not recommend the use of third-party solutions to establish a brokerage session. This can put your account at risk from potentially malicious projects.

**Note:** Interactive Brokers is unable to provide support for third-party wrappers.

###### Copy Location

Q:

###### How often do I need to log in through the browser while using the Client Portal Gateway?

A:

Clients must reauthenticate using the Client Portal Gateway at least once after midnight each day.

###### Copy Location

Q:

###### Why did I received "Server listen failed Address already in use" on my Mac when running the Client Portal Gateway?

A:

This is a known process which operates on MacOS computers which operates on the localhost:5000 port. To resolve this, you will need to Modify The Port Of Client Portal Gateway.
