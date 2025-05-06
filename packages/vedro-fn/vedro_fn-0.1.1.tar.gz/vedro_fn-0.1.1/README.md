# vedro-fn

[![Codecov](https://img.shields.io/codecov/c/github/vedro-universe/vedro-fn/main.svg?style=flat-square)](https://codecov.io/gh/vedro-universe/vedro-fn)
[![PyPI](https://img.shields.io/pypi/v/vedro-fn.svg?style=flat-square)](https://pypi.python.org/pypi/vedro-fn/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/vedro-fn?style=flat-square)](https://pypi.python.org/pypi/vedro-fn/)
[![Python Version](https://img.shields.io/pypi/pyversions/vedro-fn.svg?style=flat-square)](https://pypi.python.org/pypi/vedro-fn/)

A plugin for the [Vedro](https://vedro.io) framework that enables a functional-style syntax for defining Vedro scenarios.

## Installation

<details open>
<summary>Quick</summary>
<p>

For a quick installation, you can use a plugin manager as follows:

```shell
$ vedro plugin install vedro-fn
```

</p>
</details>

<details>
<summary>Manual</summary>
<p>

To install manually, follow these steps:

1. Install the package using pip:

```shell
$ pip3 install vedro-fn
```

2. Next, activate the plugin in your `vedro.cfg.py` configuration file:

```python
# ./vedro.cfg.py
import vedro
import vedro_fn


class Config(vedro.Config):
    class Plugins(vedro.Config.Plugins):
        class VedroFn(vedro_fn.VedroFn):
            enabled = True
```

</p>
</details>

## Usage

### Basic Example

```python
import base64
from vedro_fn import scenario, given, when, then

@scenario()
def decode_base64_encoded_str():
    with given:
        encoded = "YmFuYW5h"

    with when:
        decoded = base64.b64decode(encoded)

    with then:
        assert decoded == b"banana"
```

To run scenarios, use:

```shell
$ vedro run
```

### Using Scenario Decorators

Scenario decorators (such as `@skip`, `@only`, etc.) can be passed via an extended syntax:

```python
import base64
from vedro import skip
from vedro_fn import scenario, given, when, then

@scenario[skip]()
def decode_base64_encoded_str():
    with given:
        encoded = "YmFuYW5h"

    with when:
        decoded = base64.b64decode(encoded)

    with then:
        assert decoded == b"banana"
```

### Parametrization

You can also use Vedro’s built-in `@params` decorator with `@scenario` for parametrized scenarios:

```python
import base64
from vedro import params
from vedro_fn import scenario, when, then

@scenario([
    params("YmFuYW5h", b"banana"),
    params("", b""),
])
def decode_base64_encoded_str(encoded, expected):
    with when:
        decoded = base64.b64decode(encoded)

    with then:
        assert decoded == expected
```

# Async Example

Here’s an example of an asynchronous scenario:

```python
from vedro_fn import scenario, when, then
from interfaces.api import fetch_users

@scenario()
async def fetch_users_from_api():
    with when:
        users = await fetch_users()

    with then:
        assert users == [
            {"id": 1, "name": "Bob"},
            {"id": 2, "name": "Alice"},
        ]
```
