# Compile-minifier

Compile-minifier is a tool to minify and compile a structure code python.

## Package version

0.1.4

## Requirements

Python 3.5+

## Installation & Usage

### pip install

You can install using:

```sh
pip install compile-minifier
```

Or you can install directly from sources :

```sh
pip install git+https://github.com/bimdata/compile-minifier.git#master
```

### Get started

The package is used exclusively on the command line:

```sh
compile-minify run
```

This command minify the code with [python-minifier](https://pypi.org/project/python-minifier/) and compile all .py in .pyc recursively.

By default, no python file modifications are executed in the root folder.


### Deployment

The deployment on pypi is automated by circle when a tag is pushed on master.

For manual deployment, you can run the following command :

```sh
VERSION=<VERSION_TAG> python setup.py sdist && twine upload dist/*
```

### Help

Command line interfaces are generated with [Fire](https://github.com/google/python-fire)

For display help:

```sh
compile-minify --help
```
