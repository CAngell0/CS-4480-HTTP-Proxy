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
> The ```handle_client()``` method didn't have any logic for handling missing ```Host``` headers in the 
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
