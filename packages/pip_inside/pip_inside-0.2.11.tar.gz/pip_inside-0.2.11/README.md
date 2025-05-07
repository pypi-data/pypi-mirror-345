# pip-inside

Like [poetry](https://python-poetry.org/), but using `pip` to maintain dependencies.

Using `flit-core` as the `build-backend`.

**CONVENSIONS**:

- dynamic `version` (`__version__ = 'your version'` in `{root_module}/__init__.py`)
- non-dynamic `description` (in `pyproject.toml`)
- no `src` folder in project root
- virtualenv folder named `.venv` in project root
- not checking hashes

## install

```shell
# in each of your virtual env
pip install pip-inside
```

## commands

- pip-inside
- pi

```shell
> pi
Usage: pi [OPTIONS] COMMAND [ARGS]...

Options:
  -V, --version  show version of this tool
  --help         Show this message and exit.

Commands:
  add       Add package(s) to project dependencies
  build     Build the wheel and sdist
  deps      Show dependency tree
  export    Export dependencies to 'requirements.txt'
  info      Get info of a package from PYPI
  init      Init project in current directory
  install   Install project dependencies by groups
  publish   Publish the wheel and sdist to remote repository
  remove    Remove package(s) from project dependencies
  shell     Create or activate virtualenv in '.venv', and new shell into it
  upgrade   Upgrade pip and pip-inside
  version   Show / Change version of current project
  versions  Show recent releases of a package in PYPI

```
