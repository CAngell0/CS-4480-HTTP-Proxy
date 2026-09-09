# PA1 Milestone 1: Functional Testing

**Individual work.** No collaboration.
**Weight:** 40% of PA1. Due date on Canvas.

## Where this fits

PA1 runs in three milestones. In M0 you built the socket primitives; you will use them here. In this milestone you probe a broken HTTP proxy whose source you cannot see. In M2 you receive that proxy's source, repair it, and document the repairs.

| Milestone | Focus | Weight |
| --------- | ----- | ------ |
| M0 | Socket programming warm up | 20% of PA1 |
| M1 | Functional testing of a broken proxy | 40% of PA1 |
| M2 | Repair and document | 40% of PA1 |

The rules at the end of this handout apply to all three milestones.

---

## Overview

You are given a broken HTTP/1.0 proxy. Write Python tests that expose its bugs.

* `HTTPproxy_buggy.bin`: the proxy under test.
* `HTTPproxy_clean.bin`: a correct reference proxy, for comparison.

The buggy proxy contains **exactly 7 planted bugs**, each producing behavior that differs between the two proxies. Your tests are run against both. A test **catches a bug** when it reports a problem on the buggy proxy and reports nothing on the clean one. Any other outcome earns no credit.

You are not writing a proxy in this milestone. That is M2.

This milestone is to be performed on the CADE Lab machines. Instructions for accessing these machines are included on the Canvas "Using the CADE Lab1 Machines" page.

### Objectives

By the end of milestone 1, students should be able to:

1. Reason about a block box from behavior alone. Derive expected behavior from a written specification, form a hypothesis about where an implementation deviates, and design an observation that confirms or rejects it.
2. Identify which requirements are observable from outside a running system and which are not.
3. Construct HTTP/1.0 requests at the byte level, including malformed ones, and read a raw response off a socket without a HTTP client library.
4. State what a proxy must do that a plain client or server does not, specifically in rewriting and forwarding requests.
5. Instrument the far side of a system to observe behavior its replies do not reveal.
6. Write a differential test that reports on a faulty implementation and stays silent on a correct one. Explain why a test that reports on both carries no information.
7. Attribute several observed misbehaviors to distinct underlying defects rather than counting symptoms.

As this is a bug finding exercise, objectives are not directly assigned to e.g. "task a" etc.

## How to approach this

We are not telling you where the bugs are. Finding them is the exercise. Study the required behaviors below, form a model of what a correct proxy must do, then probe the buggy proxy in each of those places.

**The "Required behaviors" section below is the specification for this milestone.** When a test disagrees with the clean proxy, the clean proxy is correct by definition.

RFC 1945 is useful background (sections 4, 5, 6, 8, and 10 are short): https://www.rfc-editor.org/rfc/rfc1945. But a proxy has requirements HTTP/1.0 does not spell out, so some behaviors below are stated here rather than in the RFC. Where the two appear to differ, this handout governs.

Turning a required behavior into a test is the exercise. Some violations are visible in the proxy's reply to you; others are not. Working out which is which is part of the task.

## The proxy's scope

Both proxies are single endpoint HTTP/1.0 proxies: GET only, absolute URI request lines, listening on `-p` (default 2100) and `-a` (default localhost). **Caching, filtering, blocklists, and HTTPS are out of scope** and are not implemented in either proxy.

## Required behaviors

These are the specification for this milestone. The clean proxy satisfies all of them. Anything not listed here is out of scope.

**Request validation.**
* A request line that is not exactly three space separated tokens (method, absolute URI, and the literal `HTTP/1.0`) is malformed and must be answered with `400 Bad Request`.
* A version token other than `HTTP/1.0` (for example `HTTP/1.1` or `HTTP/2.0`) must be answered with `400 Bad Request`.
* A header line must have the form `Name: value`, with the colon immediately following the field name and no whitespace before it. A header such as `Connection : close` is malformed and must be answered with `400 Bad Request`.

**Method handling.**
* `GET` is supported.
* Any other well formed method (for example `POST`, `HEAD`) must be answered with `501 Not Implemented`.

**Forwarding to the origin.**
* The forwarded request line must use the relative path, not the absolute URI. `GET http://host/path HTTP/1.0` is forwarded as `GET /path HTTP/1.0`.
* A `Host` header identifying the origin must be present in the forwarded request.
* The proxy must **replace** the client's `Connection` header with `Connection: close`. The forwarded request must contain `Connection: close`. It must not contain the client's original value, and it must not omit the header.

**Reading and relaying.**
* The proxy must treat the client's request as complete only once it has received the full `\r\n\r\n` end of headers marker, and must not forward anything upstream before that marker arrives.
* The proxy must relay the origin's entire response back to the client, however large. It must not truncate a response that exceeds a single buffer read.

**Concurrency.**
* The proxy must serve multiple clients at the same time. A client that connects and stalls partway through its request must not block other clients.

## Package contents

```
pa1_m1/
├── HANDOUT.md
├── HTTPproxy_buggy.bin         # your target
├── HTTPproxy_clean.bin         # the reference
└── test_harness.py             # helpers, including MockOrigin
```

You create the two files you submit, `tests.py` and `mapping.json`, yourself. There are no templates; the examples below show the shape of each.

Run both proxies on different ports so you can compare side by side:

```bash
./HTTPproxy_buggy.bin -p 2100
./HTTPproxy_clean.bin -p 2101
```

## Writing tests

A test is a top level function that takes a proxy port and returns `True` if it saw the proxy misbehave or `False` if it did not. Open a socket, send bytes, and decide from what you observe whether a required behavior was violated:

```python
def test_something(proxy_port):
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', proxy_port))
    s.sendall(b'<your request here>\r\n\r\n')
    response = b''
    while True:
        chunk = s.recv(4096)
        if not chunk: break
        response += chunk
    s.close()
    # Inspect `response` and decide whether a required behavior was violated.
    return False
```

Not every required behavior can be checked by reading the proxy's reply. `test_harness.py` provides `MockOrigin`, a server you control that stands in for an origin and records what it receives. Point a request at it through the proxy, then inspect `origin.received`. Whether and when you need it is for you to work out.

```python
from test_harness import MockOrigin

def test_three(proxy_port):
    origin = MockOrigin(port=18080)
    try:
        # Send a request through the proxy that targets your mock origin,
        # then inspect what the origin captured.
        received = origin.received
        # ... decide whether a required behavior was violated ...
        return False
    finally:
        origin.close()
```

See `test_harness.py` for the full `MockOrigin` API.

## How your tests are run

Each test is called twice, once against the buggy proxy and once against the clean one, and the two return values are compared:

```python
detected_on_buggy = test_something(2100)   # buggy proxy
detected_on_clean = test_something(2101)   # clean proxy

caught = detected_on_buggy and not detected_on_clean
```

Only `True` then `False` counts. `False` on both means your test saw nothing. Anything returning `True` on the clean proxy is broken, since the clean proxy has no bugs to find, and earns zero whatever it does on the buggy one. A test taking longer than 15 seconds counts as `False`.

## Checking your tests locally

There is no local runner. Check your tests yourself before you submit, one function at a time. Start both proxies, then open a Python shell in the same directory as your `tests.py`:

```
$ ./HTTPproxy_buggy.bin -p 2100 &
$ ./HTTPproxy_clean.bin -p 2101 &
$ python3.10
>>> import tests
>>> tests.test_something(2100)
True
>>> tests.test_something(2101)
False
```

`True` then `False` means that test catches something. Anything else means more work. If you prefer a script, loop over your functions:

```python
import tests

for name in dir(tests):
    if not name.startswith('test_'):
        continue
    fn = getattr(tests, name)
    buggy, clean = fn(2100), fn(2101)
    print(name, buggy, clean, 'CAUGHT' if buggy and not clean else '')
```

Restart both proxies if a test leaves one wedged, and use a different `MockOrigin` port in each test so a leftover socket from the previous run does not interfere.

You can also submit to the autograder and read the count it reports, but that is slow feedback and tells you only how many bugs you caught, not which test did what. Use it to confirm, not to iterate.

Develop the same way. If a request produces identical responses from both proxies, either the behavior you are probing is not violated or your test is not sensitive enough. If the responses differ, narrow the test until it reliably distinguishes them, then confirm it still returns `False` against clean.

## What to submit

**`tests.py`** contains your tests, at most **10** of them:

```python
def test_one(proxy_port):
    ...
    return False

def test_two(proxy_port):
    ...
    return False
```

* Every test is a top level function named `test_<anything>`.
* Every test takes exactly one argument, the proxy port.
* Every test returns `True` or `False`.
* Every test cleans up its own sockets and mock origins.

**`mapping.json`** declares which bug each test targets. Number the bugs 1 through 7 in whatever order you like; the numbers are labels for grouping tests aimed at the same issue, not a canonical ordering:

```json
{
  "test_one": 1,
  "test_two": 1,
  "test_three": 2,
  "test_four": 3
}
```

Every test in `tests.py` must appear here. Several tests may share a number.

## Grading

For each bug number in your mapping, 1 point if any test in that group catches something. We deduplicate across groups, so two groups catching the same underlying bug earn 1 point, not 2. This is why the mapping matters: it makes you state what each test is for, and it stops the same bug scoring twice under two numbers.

Max: 7 points, scaled to 40% of PA1.

| Bugs caught | Score |
| ----------- | ----- |
| 7 / 7 | 100% |
| 6 / 7 | 90% |
| 5 / 7 | 78% |
| 4 / 7 | 65% |
| 3 / 7 | 50% |
| ≤ 2 / 7 | Needs resubmit; see instructor |

The autograder reports immediately how many bugs your submission caught. After the deadline we publish the full bug list. Study all 7, especially the ones you missed, since M2 asks you to repair every one.

## Notes

**No decompilation.** Do not decompile or otherwise read the `.bin` files. Submissions that appear to be derived from decompiled bytecode will be treated as academic dishonesty.

**Real servers for sanity only.** You can point tests at `example.com` or `httpforever.com` for basic checks, but most bugs require inspecting what the proxy forwarded or precise control over timing. Use `MockOrigin`.

## FAQ

**How many tests should I write?** Enough to cover 7 distinct bugs, plus a spare or two on the harder ones. Strong solutions are typically 7 to 10 tests, which is also the cap.

**Can one test catch multiple bugs?** Yes, but grading counts unique bugs across groups, so overlap does not help. Focused tests are easier to reason about.

**How do I know when to stop?** When you have 7 distinct issues that reproduce cleanly. If you think you found an 8th, contact the instructor.

**My test is flaky.** Fix it before submitting. Each test is run once per proxy, so a test that happens to return the wrong value on either run earns nothing. Timing based tests need generous margins.

---

# Rules

These apply to every PA1 milestone.

**Individual work.** You may discuss the socket API, the HTTP/1.0 protocol, and general testing or debugging approaches with classmates. You may not share code, test code, bug hypotheses, or mapping files. All submissions are checked for similarity.

**No third party libraries.** Standard library only. No `pytest`, no `requests`, no external test frameworks.

**Python 3.10.**

**LLM policy.** You may use LLMs as a reference, the same way you would use the RFC, the Python docs, or Stack Overflow. Anything you submit must reflect your own understanding.

