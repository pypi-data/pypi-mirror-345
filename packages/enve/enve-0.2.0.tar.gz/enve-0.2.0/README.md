![PyPI - Python Version](https://img.shields.io/pypi/pyversions/enve?style=for-the-badge)
![PyPI - Version](https://img.shields.io/pypi/v/enve?style=for-the-badge)
![PyPI - Types](https://img.shields.io/pypi/types/enve?style=for-the-badge)

![GitHub License](https://img.shields.io/github/license/aachick/enve?style=for-the-badge)

![Mypy](https://img.shields.io/badge/mypy-checked-blue?style=for-the-badge)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json&style=for-the-badge)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json&style=for-the-badge)](https://github.com/astral-sh/uv)

[![test](https://github.com/aachick/enve/actions/workflows/ci.yaml/badge.svg)](https://github.com/aachick/enve/actions/workflows/ci.yaml)
[![codecov](https://codecov.io/gh/aachick/enve/graph/badge.svg?token=T7SPPN48OK)](https://codecov.io/gh/aachick/enve)

<div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/aachick/enve/main/docs/assets/enve.png" />
</div>

# enve

An environment variable parser library with type hint and conversion support.

The complete documentation is available [here](https://aachick.github.io/enve/).

## Installation

Install `enve` (preferably in a virtual environment) with:

```bash
pip install enve
```

## Usage

### Python

`enve.get` is the main package function. It's essentially `os.getenv` on
(arguably unnecessarily strong) steroids. It's advantage is that it will
automatically validate the environment variable's data type based on what
you desire and provide typing support for the used variable. For complete
details, see the `enve.get` function docstring.

The example below illustrates how you can obtain environment variables and
convert them to a desired data type.

```python
import enve


ENVVAR = enve.get("ENVVAR")  # will be parsed and typed as `str`
ENVVAR_STR = enve.get("ENVVAR", dtype=str)  # will be parsed and typed as `str`
MY_SWITCH = enve.get("MY_SWITCH", dtype=bool)  # will be parsed and typed as `bool`
HASH_SALT = enve.get("HASH_SALT", dtype=bytes)  # will be parsed and typed as `bytes`
RANDOM_SEED = enve.get("RANDOM_SEED", dtype=int)  # will be parsed and typed as `int`
MY_PI = enve.get("MY_PI", dtype=float)  # will be parsed and typed as `float`
CUDA_VISIBLE_DEVICES = enve.get("CUDA_VISIBLE_DEVICES", dtype=list)  # will be parsed and typed as `list`
CUDA_VISIBLE_DEVICES = enve.get("CUDA_VISIBLE_DEVICES", dtype=tuple)  # will be parsed and typed as `tuple`
```

Supported data types are `bool`, `bytes`, `float`, `int`, `str` (the default), `list` and `tuple`.

In all these examples, a `ValueError` will be raised if the environment variable is not
defined. To use a default value, set the `default` parameter accordingly. Note that the
default value's type must be `None` or the same as the expected return type.

```python
import enve


ENVVAR_WITH_DEFAULT = enve.get("MISSING_ENVVAR", default="foobar")
```

`enve.get` also supports [Docker secrets](https://docs.docker.com/engine/swarm/secrets/).
By setting the `docker_secret` parameter to `True` or to the name of a Docker secret,
`enve.get` will attempt to retrieve its value (even if unset in the current environment).

```python
import enve


# The following snippet will:
# 1. Check whether the `MY_SECRET` envvar exists. If true, this will be returned.
# 2. Check whether `/run/secrets/MY_SECRET` exists. If true, the file will be read
#    and the value will be returned.
# 3. Check whether `/run/secrets/my_secret` exists. If true, the file will be read
#    and the value will be returned.
# 4. Raise a `ValueError` as no default is provided.
MY_SECRET = enve.get("MY_SECRET", docker_secret=True)
```

#### Improved error messages

Rather than obtaining a sometimes annoyingly obscure error when accessing an
environment variable, `enve.get` provides an arguably nicer error message.

Using `os.environ` on a missing environment variable:

```python
>>> import os
>>> os.environ["FOOBAR"]
Traceback (most recent call last):
  File "<python-input-2>", line 1, in <module>
    os.environ["FOOBAR"]
    ~~~~~~~~~~^^^^^^^^^^
  File "<frozen os>", line 716, in __getitem__
KeyError: 'FOOBAR'
```

Using `enve.get`:

```python
>>> import enve
>>> enve.get("FOOBAR")
Traceback (most recent call last):
  File "<python-input-6>", line 1, in <module>
    enve.get("FOOBAR")
    ~~~~~~~~^^^^^^^^^^
  File "enve/parser.py", line 638, in get
    raise EnvError(err_msg)
enve.parser.EnvError: Environment variable 'FOOBAR' is not set and no default or default_factory is provided.
```

Note that `enve.EnvError` exceptions inherit from `ValueError` and `KeyError` so they
can be caught the same way as if you were using `os.environ`.

### CLI

Once pip-installed, the `enve` CLI command will be available for usage. This can
be used to echo environment variable values without worrying about variable
substitution (e.g., `$FOOBAR` vs. `${FOOBAR}` vs. `%FOOBAR%` vs. `$Env:FOOBAR`).

Some common usage examples are:

```bash
$ FOOBAR=1 enve FOOBAR
FOOBAR=1

$ enve UNSET_VAR -d
UNSET_VAR=

$ enve UNSET_VAR -d default
UNSET_VAR=default

# Also check if the var is a docker secret.
$ enve UNSET_VAR -s
```

All `enve` command options are listed below:

```bash
usage: enve [-h] [-d [DEFAULT]] [-s [DOCKER_SECRET]] [--version] [env_var]

Print environment variables values without worrying about substitutions.

positional arguments:
  env_var               The environment variable to print

options:
  -h, --help            show this help message and exit
  -d, --default [DEFAULT]
                        The default value to use if the environment variable is not set. This can be
                        used a boolean flag (i.e., this option can be set without a value). In this
                        case, the default value will be an empty string if the environment variable
                        is not set.
  -s, --docker-secret [DOCKER_SECRET]
                        If set, specify that the environment variable can also be a Docker secret.
                        This can be used a boolean flag (i.e., this option can be set without a
                        value). If set this way, a docker secret with the same name as the
                        environment will be search for. If set with a value, the value will be used
                        as the docker secret name.
  --version             show program's version number and exit
```
