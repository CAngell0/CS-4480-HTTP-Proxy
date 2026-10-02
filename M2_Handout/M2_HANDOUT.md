# PA1 Milestone 2: Repair

**Individual work.** No collaboration.
**Weight:** 40% of PA1. Due date on Canvas.

## Where this fits

PA1 runs in three milestones. In M0 you built the socket primitives. In M1 you probed a broken HTTP proxy whose source you could not see. In this milestone you receive that proxy's source, fix the bugs, and document what you fixed.

| Milestone | Focus | Weight |
| --------- | ----- | ------ |
| M0 | Socket programming warm up | 20% of PA1 |
| M1 | Functional testing of a broken proxy | 40% of PA1 |
| M2 | Repair and document | 40% of PA1 |

The rules at the end of this handout apply to all three milestones.

---

## Overview

You are given the source of the broken proxy you tested in M1. Fix the 7 bugs.

* `HTTPproxy.py`: the source of `HTTPproxy_buggy.bin`, with all 7 bugs still in it. This is the file you edit and submit.
* `HTTPproxy_clean.bin`: the reference proxy, unchanged from M1.

You are not writing a proxy in this milestone. You are repairing one.

This milestone is to be performed on the CADE Lab machines. See the [Using the CADE Lab1 Machines](https://utah.instructure.com/courses/1264600/pages/using-the-cade-lab1-machines) page for access instructions; nothing about the environment has changed.

### Objectives

By the end of milestone 2, students should be able to:

1. Read an implementation they did not write and locate the point where it departs from a written specification.
2. Trace an externally observed symptom back to the line of code that produced it.
3. Recognize when several symptoms share one cause, and repair the cause rather than the symptom.
4. Judge whether a change satisfies a requirement in general or only for the input that revealed it.
5. Change code without disturbing behavior that was already correct.
6. Explain a repair precisely enough that another engineer can verify it against the diff.

## How to approach this

Start with the tests you wrote in M1. Run them against the source you now have and work through the failures one at a time. Every failure you can still reproduce points at code you need to read.

Expect several of your tests to go green at once from a single change. In M1 you were counting distinct bugs behind a larger number of symptoms. Here you see why. Think of a calendar that stores appointment times in the server's local time zone rather than UTC. Every meeting shifts by an hour when daylight saving changes, and meetings booked from another country show up at the wrong time. Those arrive as two unrelated complaints, and one fix ends both. Expect the same here.

When your own tests all pass, submit. If your score is short of full marks, your M1 tests did not cover everything. That is normal and expected, which is why the autograder tests each bug in more than one way. Read the required behaviors one at a time against the source, find what you missed, and submit again.

**The "Required behaviors" section below is the specification for this milestone**, unchanged from M1. Not everything listed is broken. Some of it describes what the proxy already does correctly, and breaking one of those costs you points.

## The proxy's scope

Unchanged from M1. A single endpoint HTTP/1.0 proxy: GET only, absolute URI request lines, listening on `-p` (default 2100) and `-a` (default localhost). **Caching, filtering, blocklists, and HTTPS are out of scope** and must not be added.

## Required behaviors

These are the specification for this milestone, unchanged from M1. `HTTPproxy_clean.bin` satisfies all of them. Anything not listed here is out of scope.

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
pa1_m2/
├── M2_HANDOUT.md
├── HTTPproxy.py                # the broken source; edit and submit this
├── HTTPproxy_clean.bin         # the reference, unchanged from M1
└── test_harness.py             # unchanged from M1
```

You create `fixes.md` yourself. There is no template; the examples below show the shape.

Run your proxy alongside the reference, the same way you did in M1:

```bash
python3.10 HTTPproxy.py -p 2100
./HTTPproxy_clean.bin -p 2101
```

## Fixing the bugs

Fix each bug where it is, not where it shows up. A change that makes one test pass while leaving the underlying error in place will fail the other test for the same bug.

Keep the structure of the file you were given. Small local changes are what this milestone asks for. Reorganizing the file, or replacing it with a proxy written from scratch, makes `fixes.md` impossible to verify and costs you points there.

## How your submission is graded

Each bug is tested twice, in two different ways. Both tests must pass to earn that bug's points:

```
bug_points = 8 if (test_a_passed and test_b_passed) else 0
```

Six further tests check that the proxy still meets the required behaviors it already met. Those are constructed so that none of the 7 bugs can make them fail, which means a failure there is something you broke.

A test taking longer than 20 seconds counts as a failure.

## Checking your work locally

Run your own M1 tests first, one function at a time, exactly as you did in M1:

```
$ python3.10 HTTPproxy.py -p 2100 &
$ ./HTTPproxy_clean.bin -p 2101 &
$ python3.10
>>> import tests
>>> tests.test_something(2100)
False
>>> tests.test_something(2101)
False
```

In M1 you wanted `True` then `False`. Now you want `False` on both, since your repaired proxy should behave like the clean one. When every test you wrote reports `False` on both, submit and read the score.

## What to submit

**`HTTPproxy.py`**, repaired. It must run under `python3.10` and accept `-p` and `-a` as described above.

**`fixes.md`**, one short section per bug, 7 in total, numbered 1 through 7. Two to four sentences each. No preamble, no conclusion.

Each section says three things:

* what the bug did
* the function it was in, and the specific line or construct that was wrong
* what you changed it to

A section that earns full credit reads like the following. The example is from an unrelated program, so it shows you the shape without handing you one of your answers. Your headings are the bug numbers.

> ### Bug N
> Scores above 999 were ranked below smaller ones. In `rank_players`, the list was sorted with `sorted(scores)` on the raw strings read from the save file, so ordering was lexicographic rather than numeric. I convert each score to `int` at parse time and sort on that.

A section that earns nothing reads like this:

> ### Bug N
> The ranking was incorrect. I fixed the code so the leaderboard sorts properly and the program now behaves as expected.

The difference is specificity to your code. An explanation that would apply equally to any of the 7 bugs, or to any proxy, earns nothing. Name the function and the line from the file you actually submitted.

## Grading

| Component | Points |
| --------- | ------ |
| Autograder | 65 |
| `fixes.md` | 35 |

The autograder gives 8 points per bug, 56 total, plus 9 points across the six checks that the proxy still works. Every bug is worth the same.

`fixes.md` gives 5 points per bug. Three points for naming the function and the line that was wrong, two points for that change actually being present in the file you submitted.

The autograder runs your file with `python3.10 HTTPproxy.py -p <port>` on a port it chooses. If your file does not start, or does not accept `-p`, it scores 0. Test this before you submit.

Max: 100 points, scaled to 40% of PA1.

## Notes

**Do not add scope.** Caching, filtering, blocklists, and HTTPS are not bugs. Adding them earns nothing and risks breaking what already worked.

**Keep a copy of the original.** `diff` against it is the fastest way to confirm you changed only what you meant to change.

**Real servers for sanity only.** As in M1, `example.com` and `httpforever.com` are fine for a quick check, but most of these bugs are only visible from the origin side or under precise timing. Use `MockOrigin`.

## FAQ

**My M1 tests all pass but the autograder does not give full marks.** Your tests covered fewer cases than the required behaviors do. Work through the behaviors one at a time against the source.

**One change fixed several of my M1 tests. Did I miss a bug?** Probably not. Several symptoms sharing one cause is expected, and telling symptoms apart from bugs was objective 7 in M1.

**I never found this bug in M1 and I still cannot see it.** Pick the required behavior you cannot demonstrate, find the function that behavior passes through, and read it line by line. If a behavior has no obvious home in the source, that absence is the bug.

**I think I found an 8th bug.** Contact the instructor, as in M1. Do not add an 8th section to `fixes.md`.

**Can I restructure the file while fixing it?** Small local changes are fine. Wholesale reorganization makes `fixes.md` unverifiable and costs you points on every section.

---

# Rules

These apply to every PA1 milestone.

**Individual work.** You may discuss the socket API, the HTTP/1.0 protocol, and general testing or debugging approaches with classmates. You may not share code, test code, bug hypotheses, mapping files, or `fixes.md` text. All submissions are checked for similarity.

**No third party libraries.** Standard library only. No `pytest`, no `requests`, no external test frameworks.

**Python 3.10.**

**LLM policy.** You may use LLMs as a reference, the same way you would use the RFC, the Python docs, or Stack Overflow. Anything you submit must reflect your own understanding.