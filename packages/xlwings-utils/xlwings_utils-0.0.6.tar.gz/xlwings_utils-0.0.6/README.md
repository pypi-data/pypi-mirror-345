 <img src="https://www.salabim.org/xlwings_utils_logo1.png"> 

## Introduction

This module provides some useful functions to be used in xlwings lite.

The xlwings lite system does not provide access to the local file system. With this
module, files can be copied between dropbox and the local pyodide file systen. And
therefore, it is possible to indirectly use the local file system.

The module contains support for a useful 2 dimensional data structure: block.
Thjs can be useful to manipulate a range without accessing the range directly,
which is expensive in terms of memory and execution time.

On top of that, this module makes it possible to capture stdout writes, which
can then be copied to a worksheet in a later stage.

## Installation

Just add xlwings-utils to the requirement tab. It might be required to add ssl.

## Dropbox support

xlwings_lite only works with full access dropbox apps.

In order to use dropbox functionality, is is necessary to initialize the module with credentials.

```xwu.dropbox_init()```
If called without parameters, the refresh_token is

## Capture stdout support

 Badges

![PyPI](https://img.shields.io/pypi/v/xlwings-utils) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/xlwings-utils) ![PyPI - Implementation](https://img.shields.io/pypi/implementation/xlwings-utils)
![PyPI - License](https://img.shields.io/pypi/l/xlwings-utils) ![ruff](https://img.shields.io/badge/style-ruff-41B5BE?style=flat) 
![GitHub last commit](https://img.shields.io/github/last-commit/salabim/peek)

