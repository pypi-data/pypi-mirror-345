# Project: flake8-consistent-quotes

## Description

This project provides a plugin for Flake8 that checks for quote consistency at the file level. The plugin is intended for use in projects that do **not** have an established convention for single vs. double quotes.

If your project **does** follow a specific quote style convention, consider using the [flake8-quotes](https://pypi.org/project/flake8-quotes/) plugin instead.

## How the Plugin Works

The plugin counts the number of quote types used within a file and raises an error if the less frequently used quote appears.
In such cases, the plugin emits the error: `FCQ001`.

## Usage

To install the plugin, use the following command:

```bash
pip install flake8-consistent-quotes
```
