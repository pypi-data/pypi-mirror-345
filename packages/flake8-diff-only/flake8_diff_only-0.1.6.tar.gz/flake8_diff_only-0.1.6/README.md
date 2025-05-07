# Project: flake8-diff-only

## Description

This project provides a plugin for **Flake8** that checks only the modified lines of files for style violations.

> ⚠️ **Please note:**
>
> * The [current implementation of `--diff` is fundamentally flawed by design](https://github.com/pycqa/flake8/issues/1389).
> * The [`--diff` option was deprecated in Flake8 5.0.0](https://flake8.pycqa.org/en/latest/release-notes/5.0.0.html#deprecations).
> * The [`--diff` option was removed entirely in Flake8 6.0.0](https://flake8.pycqa.org/en/latest/release-notes/6.0.0.html#backwards-incompatible-changes).

This project replicates that deprecated functionality but as a plugin, and naturally inherits the same limitations.
However, it has distinct advantages — particularly in **legacy codebases**, where running full Flake8 checks may produce excessive noise.
That's why I decided to recreate this feature in the form of a plugin.

## Usage

To install the plugin, run:

```bash
pip install flake8-diff-only
```
