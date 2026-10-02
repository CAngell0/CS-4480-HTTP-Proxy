# Bug Fixes for PA2 Milestone #2
---

> #### Bug #1  -  Incorrect Response to Invalid HTTP Version
> Inside the handle_client() method, there wasn't a check written for the request version after
> it had been parsed. I added that check on lines 202 - 205. Now if it sees that any HTTP versions
> that are not ```HTTP/1.0``` it response with ```400 Bad Request```.

Code Sample:
```python
if parsed['version'] != 'HTTP/1.0':
    send_error(client_sock, 400, "Bad Request")
    return
```
