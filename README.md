# praline-config

Python app configuration library to instantiate Python objects from various
configuration inputs.

## Purpose

`praline-config` endeavours to make gathering configuration inputs from various
sources as low-friction and straightforward as possible.

## Getting Started

### Installation

```shell
pip install praline-config
```

### Example Usage

Using `praline.config` has a few steps...

1. Write configuration data in a supported format(yaml, toml, dotenv, etc..)
2. Define a dataclass to hold your configuration data
3. Instantiate the configuration object

#### Example YAML Configuration

```yaml
server_address: "www.example.com"
threads: 4
```
#### Example Program

```python
#!/usr/bin/env python3

from dataclasses import dataclass
from praline.config import AppConfigBase


@dataclass
class AppConfig(AppConfigBase):
    server_address: str = None
    threads: int = None


def main():
    app_config: AppConfig = AppConfig.load(config="example.yaml")
    print(f"Server: {app_config.server_address}")
    print(f"Threads: {app_config.threads}")


if __name__ == "__main__":
    exit(main())

```

#### Output

```text
Server: www.example.com
Threads: 4
```

## Supported Configuration Sources

`praline-config` leverages the `python-configuration` package to handle the raw
configuration data, so any format it supports is supported. Additionally,
`praline-config` can handle importing `dotenv` formatted files and binding
environment variable values to fields in your configuration class. Finally, it
can also incorporate values gathered from the CLI or similar through a
dictionary.

See the documentation for [python-configuration](https://pypi.org/project/python-configuration/) for the complete list of supported formats.

## Dependencies

### [python-configuration](https://pypi.org/project/python-configuration/)

> A library to load configuration parameters hierarchically from multiple
> sources and formats

`python-configuration` is an excellent library designed to interface with many
different sources commonly used to store configuration data. We use it here as
an adaptor for the various configuration sources being used as inputs.

### [python-dotenv](https://pypi.org/project/python-dotenv/)

> Python-dotenv reads key-value pairs from a .env file and can set them as
> environment variables. It helps in the development of applications following
> the 12-factor principles.

Used to load `.env` formatted files.
