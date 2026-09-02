# PA1 Milestone 0: Socket Programming Warm-Up

**Individual work.** No collaboration.
**Weight:** 20% of PA1. Due date on Canvas.

## Where this fits

PA1 runs in three milestones. Here in M0 you build the socket primitives. In M1 you use them to probe a broken HTTP proxy whose source you cannot see. In M2 you receive that proxy's source, repair it, and document the repairs.

| Milestone | Focus | Weight |
| --------- | ----- | ------ |
| M0 | Socket programming warm up | 20% of PA1 |
| M1 | Functional testing of a broken proxy | 40% of PA1 |
| M2 | Repair and document | 40% of PA1 |

The rules at the end of this handout apply to all three milestones.

---

## Overview

Implement three small functions using Python's `socket` module. You will submit three files, each containing one function. The surrounding code (argument parsing, test drivers, harness setup) is not your concern.

Work out the API from the Python documentation. You will need `socket.socket`, `bind`, `listen`, `accept`, `connect`, `sendall`, `recv`, `shutdown`, `close`, and `setsockopt`. Two facts that trip up most students: `recv(N)` returns *up to* N bytes, not exactly N, so loop when you need a specific count; and sockets take `bytes`, not `str`.

Read the docstrings in the templates carefully. They specify exactly what each function must do.

**References:**
* Python `socket` docs: https://docs.python.org/3.10/library/socket.html
* Beej's Guide to Network Programming: https://beej.us/guide/bgnet/

### Objectives

By the end of milestone 0, students should be able to:

1. Establish a TCP connection from a client and transfer bytes over it.
2. Set up the server side of a TCP connection, accept a client, and configure the socket so a restarted server can rebind immediately.
3. Explain why TCP delivers a byte stream rather than discrete messages, and accumulate bytes until a known length or an end condition is reached.
4. Signal the end of a transmission without tearing down the connection, and explain why a sender that gives no such signal can leave both sides waiting on each other.
5. Distinguish EOF from a short read, and handle a peer that closes before sending the expected number of bytes as a separate outcome rather than an error.
6. Keep `bytes` and `str` distinct at the socket boundary, encoding and decoding explicitly.
7. Manage socket lifetime correctly, closing both connected sockets and listening sockets where applicable.

## Task A: `fetch(host, port, message)` (30 points)

**File:** `task_a_client.py`

```python
def fetch(host: str, port: int, message: bytes) -> bytes:
    ...
```

1. Open a TCP connection to `(host, port)`.
2. Send `message`.
3. Signal to the server that you are done sending.
4. Read all bytes the server sends back until it closes the connection.
5. Return the received bytes.

**Hint.** The test server reads until you close your send side. If you send and then start reading, you will hang. Look up `socket.shutdown()`.

## Task B: `serve_one(port)` (30 points)

**File:** `task_b_server.py`

```python
def serve_one(port: int) -> bytes:
    ...
```

1. Listen on `('localhost', port)`.
2. Accept **exactly one** client. Do not loop for more.
3. Read all bytes the client sends until it closes its send side.
4. Send back those bytes prefixed with `b"REPLY: "`.
5. Close both sockets.
6. Return the bytes received from the client, not the prefixed reply.

**Hint.** If `bind()` fails with "address already in use" on a quick re-run, there is a socket option that fixes this permanently. Find it in the socket docs and set it on every server socket you create in this course.

## Task C: `recv_exactly(sock, n)` (40 points)

**File:** `task_c_recv_exactly.py`

```python
def recv_exactly(sock: socket.socket, n: int) -> bytes | None:
    ...
```

* Return exactly `n` bytes if the peer sends at least `n` before closing.
* Return `None` if the peer closes before sending `n` bytes.

**Hint.** The harness deliberately sends bytes in small chunks with pauses. A single `sock.recv(n)` will not pass.

## Package contents

```
pa1_m0/
├── HANDOUT.md
└── student_templates/
    ├── task_a_client.py
    ├── task_b_server.py
    └── task_c_recv_exactly.py
```

Each template has a stub with a `TODO` region. **Fill in only the TODO region.** The autograder imports your functions by name.

## Submitting

Upload `task_a_client.py`, `task_b_server.py`, and `task_c_recv_exactly.py` to Gradescope.

* Python 3.10, standard library only.
* Each file exports the exact function name given.
* Do not `print()` anything. The autograder only inspects return values.

## Grading

Each function is tested against 4 inputs. Partial credit is proportional to how many pass.

| Task | Points |
| ---- | ------ |
| A: `fetch()` | 30 |
| B: `serve_one()` | 30 |
| C: `recv_exactly()` | 40 |

Total: 100 points, scaled to 20% of PA1.

## Debugging tips

* **Hangs.** Both sides are waiting on the other. Somebody has to signal end of message: a close, a half close, or a protocol level terminator.
* **`bind()` fails.** See Task B's hint.
* **Wrong number of bytes.** You are not looping on `recv`.
* **`TypeError` about `str` vs `bytes`.** Use `b"..."` literals or `.encode()`.

Test locally before submitting. For Task B, run your server in one terminal and connect with `nc localhost <port>` from another.

---

# Rules

These apply to every PA1 milestone.

**Individual work.** You may discuss the socket API, the HTTP/1.0 protocol, and general testing or debugging approaches with classmates. You may not share code or test code. All submissions are checked for similarity.

**No third party libraries.** Standard library only. No `pytest`, no `requests`, no external test frameworks.

**Python 3.10.**

**LLM policy.** You may use LLMs as a reference, the same way you would use the RFC, the Python docs, or Stack Overflow. Anything you submit must reflect your own understanding.
