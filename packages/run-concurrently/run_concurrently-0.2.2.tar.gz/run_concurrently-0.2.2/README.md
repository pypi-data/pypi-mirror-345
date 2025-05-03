# Run Concurrently

A pure python, zero dependency, package to run a list of commands concurrently.

## Installation

Install from PyPI:

```bash
pip install run-concurrently
```

or, if you prefer to keep it isolated:

```bash
pipx install run-concurrently
```

## Features

* **Zero dependencies** – works with the Python standard library only  
* **Colour‑coded output** – each command gets its own colour so logs are easy to follow  
* **Graceful shutdown** – sends SIGINT/SIGTERM to all child processes on exit  
* **Cross‑platform** – tested on Linux, macOS, and Windows

## Usage

Run any number of commands concurrently:

```bash
run-concurrently \
  "tail -f app.log" \
  "uvicorn app:app --reload"
```

By default, **run-concurrently** stops *all* commands as soon as one of them exits with a non‑zero status.
