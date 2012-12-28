ZK Examples
===

These are some bare-bones examples of how you can implement ZK into your app.

Languages are put into their own folder, with their own README file, explaining what you will need to know for that language, if anything.

How it works
---
+ __Client__ -> __Server__: Hello, here's my ZKM object!
+ __Server__ validates that this is a valid license/hwid combo, if it:
	+ __is__: Server will return a ZKReply object with information for validation, telling the client it's good to go ahead with extra steps.
	+ __isn't__: Server will still return a ZKReply object, with different information, informing the client to stop right here, (criminal scum!).
+ __Client__ validates the ZKReply object internally, and, depending on what is returned, will display information on the error or continue.
+ __Client__ internally validates the ZKReply object's information against the information stored internally (a mockup ZKReply, in most regards).
	+ __valid__: The client will run whatever launching system it has in place to initialise the app.
	+ __invalid__: The client has to jump-ship now, something has gone wrong. It might be tampering, it might be a server muckup, but all we know is it needs to __get the hell out__.

So in short:
+ Client -> Server (initial transfer)
+ Server -> Client (reply)
+ Client -> Self (verify)
+ Client -> Self (launch/bail)

Notes
---
+ If you don't use SSL, your app isn't going to be inherently secure.
	+ OpenSSL is easy to use, perhaps look into it in your language.
	+ It is, however, an extra dependancy, so it isn't for everyone.
+ These examples just show how you can implement ZK into your app, it's up to you to make sure it isn't easy for crackers to get at and edit.
+ If you don't close your socket within a variable time determined by the server, your socket will be forcefully closed!
	+ This will most likely throw an exception on your app end, although all socket should be surrounded with exception catching anyway.
	+ This is to make sure that people can't keep empty sockets open to use up the servers resources.
	+ If you have a particularly bad connection to the server, this might be an issue. The default, however, is ten seconds. That should be plenty.
+ Logs are prefixed with the time as formatted by strftime().
	+ The prefix is formatted as: `[Month/Day/Year Hour:Minute:Seconds]` (`strftime("%m/%d/%Y %H:%M:%S")`)

Contributing
---
If you want to contribute an example, that's great! We'd love your example code. However, please try to stick to these guidelines:
+ If you're using SSL, try and use OpenSSL or the language's native SSL implementation.
+ Provide an example for both SSL and non-SSL. This makes it easier for everyone. (`example.cpp` and `example_ssl.cpp`, for example)
+ Include information in your README such as compiling commands, any other bits of information which might be useful, or anything else related.
	+ Feel free to include your name there aswell, if you want some credit.
+ Don't leave in local paths to files, use `/path/to/file.ext`, or some other placeholder.
	+ Don't leave in any other possibly sensitive information either, silly!
+ To keep this from being insecure, make sure your examples don't connect to the incorrect server.
	+ SSL with certificates are used for a reason. We don't want to send our information out to anyone.

### ZKM?
This is the main protobuf object. It's purely __client -> server__, however the server has it to construct it's own copy.
It has various parts:
+ __key__: Obviously just the license key the user inputs.
+ __hwid__: The unique client identifier. (Hardware information hash, whatever the program author chooses)
+ __type__: The request type:
	+ 0 = VALIDATE
	+ That's all for now.
+ __options__: A repeated string array with options the server might implement some day.

### ZKReply?
Yes, this protobuf object has three parts:
+ __reply__: This is just a constant int of what sort of reply it is. Successful, error, failure, etc.
	+ This __isnt__ used for anything other than an error display. This would be insecure as hell for checks.
+ __key__: The key the client supplied (simple check).

### Howto
+ Generate your RSA key.
	+ `openssl genrsa > privkey.pem`
+ Generate self-signed certificate.
	+ `openssl req -new -x509 -key privkey.pem -out ca.pem -days 365`
	+ This creates your self signed certificate, good for one year.
+ Use your self-signed certificate in your app with the ssl connection.

### ProtoBuf objects
In most cases, simply copying the version which comes with your server is enough.  
If you do need to compile them, for example, if you modify ZK, you can do this:

Set this to wherever your ZK installation is.
`$ export SRC_DIR="/home/user/ZK/zkpm/proto"`

This is where you'll want your final pieces to end up.
`$ export APP_DIR="/home/user/MyApp/src"`

Export to the language you're writing your app in, obviously.
`--python_out`, `--java_out`, `--cpp_out` for Python, Java and C++ respectively.
`$ protoc -I=$SRC_DIR --python_out=$APP_DIR $SRC_DIR/ZKM.proto`