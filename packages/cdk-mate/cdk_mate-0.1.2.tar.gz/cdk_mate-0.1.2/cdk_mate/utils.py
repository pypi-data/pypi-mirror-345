# -*- coding: utf-8 -*-

"""
Utility functions.
"""


def to_camel(s: str) -> str:
    """
    Converts a string to camelcased. Useful for turning a function name into a class name.

    Example:

    >>> to_camel('Hello_world')
    'HelloWorld'
    >>> to_camel('hello-World')
    'HelloWorld'
    >>> to_camel('HELLO WORLD')
    'HelloWorld'
    """
    s = "_".join([w.strip() for w in s.split() if w.strip()])
    s = s.replace("-", "_")
    return "".join(w.capitalize() or "_" for w in s.split("_"))


def to_slug(s: str) -> str:
    """
    Converts a string to slug. Useful for turning a name to CloudFormation stack name.

    assert to_slug("Hello_world") == "Hello-world"
    assert to_slug("hello-World") == "hello-World"
    assert to_slug("HELLO WORLD") == "HELLO-WORLD"
    assert to_slug("hello world") == "hello-world"
    assert to_slug("HELLO  WORLD") == "HELLO-WORLD"
    assert to_slug("hello  world") == "hello-world"

    Example:

    >>> to_slug('Hello_World')
    'Hello-World'

    >>> to_slug('hello world')
    'hello world'
    """
    s = "-".join([w.strip() for w in s.split() if w.strip()])
    s = s.replace("_", "-")
    return s
