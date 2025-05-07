# Compile-minifier

Compile-minifier is a tool to minify and compile a structure code python.

## Package version

0.2.1

## Requirements

Python 3.5 to 3.13

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

For manual deployment, you can run the following command :

```sh
poetry publish --build --username=__token__ --password=
```

### Help

Command line interfaces are generated with [Fire](https://github.com/google/python-fire)

For display help:

```sh
compile-minify --help
```
