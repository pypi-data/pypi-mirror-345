# ok-py-subprocess-defaults

Trivial wrapper for [Python subprocess.run](https://docs.python.org/3/library/subprocess.html#subprocess.run) with defaults and logging.

You probably won't want to use this. Just call `subprocess.run` directly (it's perfectly lovely), write your own trivial helper, or use one of these libraries:
- [sh](https://github.com/amoffat/sh) - call any shell command as if it were a function
- [Plumbum](https://github.com/tomerfiliba/plumbum) - shell-like syntax for Python
- [zxpy](https://github.com/tusharsadhwani/zxpy) - `~` string operator to run shell commands
- [shellpy](https://github.com/lamerman/shellpy) - `\`` string operator to run shell commands
- [shell](https://github.com/toastdriven/shell) - another wrapper for subprocess
- [pipepy](https://github.com/kbairak/pipepy) - pipe operators and function wrappers for shell commands
- [python-shell](https://github.com/ATCode-space/python-shell) - another shell command runner

But, this is my wrapper, and it does these things:
- Lets you set defaults for `cwd` and `env` (added to `os.environ`)
- Logs the commands run (with proper escaping) for transparency
- Checks command return (`check=True`)
- Uses explicit argument vectors (`shell=False`), no messy escaping issues
- Has easy-peasy functions to capture stdout as text or lines
- Pass-through (or override) for all `subprocess.run` arguments

Collectively, this is what I want for subprocesses -- tiny tweaks to
`subprocess.run` (or actually `subprocess.check_call`) for one-liner brevity.
Your mileage almost certainly will vary.

# Usage

Add this package as a dependency:
- `pip install ok-py-subprocess-defaults`
- OR just copy `ok_subprocess_defaults.py` (it has no dependencies)

Import the module, create an `ok_subprocess_defaults.SubprocessDefaults` object, and use it to run commands:
```python
import logging
import ok_subprocess_defaults
...
sub = ok_subprocess_defaults.SubprocessDefaults()
...
logging.basicConfig(level=logging.INFO)  # to show the logging
...
sub.run("echo", "Hello World!")
```
Note that command arguments are individual function arguments; otherwise, arguments are the same as [subprocess.run](https://docs.python.org/3/library/subprocess.html#subprocess.run) including keyword arguments and return value.

The logging output looks like this:
```
$ python test.py
INFO:root:🐚 echo 'Hello World!'
Hello World!
```
Note that arguments are escaped so you can cut-and-paste the command.

## Configuring defaults

## Capturing output

If you want to do more specific output capture or processing, any keyword
arguments passed to `run` are passed on to `subprocess.run`:
