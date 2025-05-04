# SimpleArgParser

## Installation

```
pip install simpleArgParser
```

## Introduction

This is a simple command line argument parser encapsulated based on Python dataclasses and type hints, supporting:
- Defining arguments using classes (required, optional, and arguments with default values)
- Nested dataclasses, with argument names separated by dots
- JSON configuration file loading (priority: command line > code input > JSON config > default value)
- List type arguments (supports comma separation)
- Enum types (pass in the name of the enum member, and display options in the help)
- Custom post-processing (post_process method)

Detailed introduction is coming soon. Please also refer to `examples/example.py`.