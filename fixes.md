# Bug Fixes for PA2 Milestone #2
---

> #### Bug #1  -  Incorrect Response to Invalid HTTP Version
> Inside the handle_client() method, there wasn't a check written for the request version after
> it had been parsed. I added that check on lines 202 - 205. Now if it sees that any HTTP versions
> that are not ```HTTP/1.0``` it response with ```400 Bad Request```.

Code:
```python
if parsed['version'] != 'HTTP/1.0':
    send_error(client_sock, 400, "Bad Request")
    return
```


> #### Bug #2  -  Incorrect Parsing of HTTP Headers
> The parsing of HTTP headers inside the parse_request method was a bit too lenient for the proxy
> specifications. I changed the partition call on 97 to partition for ```": "``` instead of ```":"```.
> And then I had it check for spaces in the header name, and return None if it found any. This fixed
> the bug for not responding with ```400 Bad Request``` whenever there was a malformed header.

Code:
```python
name, _, value = line.partition(": ")
if ' ' in name:
    return None
```
