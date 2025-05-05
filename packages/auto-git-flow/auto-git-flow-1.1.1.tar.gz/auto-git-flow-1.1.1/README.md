Auto git flow
[![PEP8](https://img.shields.io/badge/code%20style-pep8-green.svg)](https://www.python.org/dev/peps/pep-0008/)
===

## Features

- Auto complete the versions when typing `git flow release start` or `git flow hotfix start`
- Alias for `git flow feature start` → `gffs`

## Usage

Install
```sh
pip install auto-git-flow
```

Start a new minor release *X.X+1.X*
```sh
gfrs # instance for "git flow release start X.X+1.X"
```

Start a new major release *X+1.X.X*
```sh
gfrs m # instance for "git flow release start X+1.X.X"
gfrs -m
gfrs --major
```

Start a new hotfix *X.X.X+1*
```sh
gfhs # instance for "git flow hotfix start X.X.X+1"
```

Start a new feature "awesome"
```sh
gffs awesome # instance for "git flow feature start awesome"
```

## Note

- Expected (and supported) tag format is "X.X.X"
- Checkout [changelogfromtags](https://gitlab.com/cdlr75/changelogfromtags) to auto generate a changelog from tags
