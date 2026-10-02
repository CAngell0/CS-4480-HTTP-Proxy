# Bug Fixes for PA2 Milestone #2
---

> #### Bug #1  -  Incorrect Response to Invalid HTTP Version
> Inside the ```handle_client()``` method, there wasn't a check written for the request version after
> it had been parsed. I added that check on lines 202 - 205. Now if it sees that any HTTP versions
> that are not ```HTTP/1.0``` it response with ```400 Bad Request```.

Code:
```python
if parsed['version'] != 'HTTP/1.0':
    send_error(client_sock, 400, "Bad Request")
    return
```

<br/>

> #### Bug #2  -  Incorrect Parsing of HTTP Headers
> The parsing of HTTP headers inside the parse_request method was a bit too lenient for the proxy
> specifications. I changed the partition call on line 97 to partition for ```": "``` instead of 
> ```":"```. And then I had it check for spaces in the header name, and return None if it found any.
> This fixed the bug for not responding with ```400 Bad Request``` whenever there was a malformed 
> header.

Code:
```python
name, _, value = line.partition(": ")
if ' ' in name:
    return None
```

<br/>

> #### Bug #3  -  Incorrect Construction of Forwarded Request
> How forwarded requests are put together in ```build_forwarded_requests()``` method was a little off.
> When making the request, it passed the absolute URL using the method's ```url``` parameter. Instead
> of using the ```path``` paremeter like it's supposed to. I made this small change on line 150. This
> fixed the bug of the proxy forwarding the absolute URL instead of the relative path to the origin.

Code:
```python
lines = [f"{method} {path} HTTP/1.0"]
```

<br/>

> #### Bug #4  -  No Checks for Host Header
> The ```handle_client()``` method didn't have any logic for handling missing ```Host``` headers for the 
> incoming requests. I added an if statement in lines 221-222 to fix this. I also converted the 
> ```headers``` fields that are used around the codebase to be dictionaries instead of an array of
> tuples. This made the checking and handling of headers to be a bit more readable. You can see these
> changes on lines 91, 107, and 157. All this fixed the bug where the proxy wasn't garenteeing a host
> header for the origin. By default, if the header is missing it will add ```{'Host': 'localhost'}```
> to the forwarded request.
Code:
```python
# Dictionary Changes
headers = {} # Line 91
headers[name] = value # Line 107
for name, value in headers.items(): # Line 157

# Header Checking
if 'Host' not in parsed["headers"]:
    parsed["headers"]['Host'] = 'localhost'
```

<br/>

> #### Bug #5  -  No Checks for Connection Header
> The ```handle_client()``` method didn't have any logic for handling missing or invalid 
> ```Connection``` headers for the incoming requests. I added that check on lines 224-226. If an
> incoming request doesn't have the header ```Connection: close``` with that exact name or value.
> It will add/overwrite the header to the request before forwarding it. This fixes the bug of the
> proxy not adding the header when needed, or not changing it to ```close``` when needed.

Code:
```python
if ('Connection', 'close') not in parsed["headers"].items():
    parsed["headers"]['Connection'] = 'close'
```

<br/>

> #### Bug #6  -  Sending Chunk to Client Only Done Once
> Inside the ```forward_and_stream_response()``` method. It only sends one data chunk from the origin
> server back to the client. If the total request is big enough to be split into multiple chunks, the
> the proxy needs to recieve and send those chunks repeatadely. And currently, it only does this once.
> I changed the streaming code on lines 172-175 to run in a loop and to keep looping chunks until it's
> not receiving any more data chunks from the origin. This fixes the bug where the proxy cuts longer
> responses short when the origin sends one back.

Code:
```python
while True:
    chunk = origin_sock.recv(SMALL_BUFFER)
    if not chunk: break

    client_sock.sendall(chunk)
```
