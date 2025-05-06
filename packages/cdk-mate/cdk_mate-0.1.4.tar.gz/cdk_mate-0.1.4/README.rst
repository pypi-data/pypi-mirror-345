
.. image:: https://readthedocs.org/projects/cdk-mate/badge/?version=latest
    :target: https://cdk-mate.readthedocs.io/en/latest/
    :alt: Documentation Status

.. image:: https://github.com/MacHu-GWU/cdk_mate-project/actions/workflows/main.yml/badge.svg
    :target: https://github.com/MacHu-GWU/cdk_mate-project/actions?query=workflow:CI

.. image:: https://codecov.io/gh/MacHu-GWU/cdk_mate-project/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/MacHu-GWU/cdk_mate-project

.. image:: https://img.shields.io/pypi/v/cdk-mate.svg
    :target: https://pypi.python.org/pypi/cdk-mate

.. image:: https://img.shields.io/pypi/l/cdk-mate.svg
    :target: https://pypi.python.org/pypi/cdk-mate

.. image:: https://img.shields.io/pypi/pyversions/cdk-mate.svg
    :target: https://pypi.python.org/pypi/cdk-mate

.. image:: https://img.shields.io/badge/✍️_Release_History!--None.svg?style=social&logo=github
    :target: https://github.com/MacHu-GWU/cdk_mate-project/blob/main/release-history.rst

.. image:: https://img.shields.io/badge/⭐_Star_me_on_GitHub!--None.svg?style=social&logo=github
    :target: https://github.com/MacHu-GWU/cdk_mate-project

------

.. image:: https://img.shields.io/badge/Link-API-blue.svg
    :target: https://cdk-mate.readthedocs.io/en/latest/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Install-blue.svg
    :target: `install`_

.. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
    :target: https://github.com/MacHu-GWU/cdk_mate-project

.. image:: https://img.shields.io/badge/Link-Submit_Issue-blue.svg
    :target: https://github.com/MacHu-GWU/cdk_mate-project/issues

.. image:: https://img.shields.io/badge/Link-Request_Feature-blue.svg
    :target: https://github.com/MacHu-GWU/cdk_mate-project/issues

.. image:: https://img.shields.io/badge/Link-Download-blue.svg
    :target: https://pypi.org/pypi/cdk-mate#files


Welcome to ``cdk_mate`` Documentation
==============================================================================
.. image:: https://cdk-mate.readthedocs.io/en/latest/_static/cdk_mate-logo.png
    :target: https://cdk-mate.readthedocs.io/en/latest/

CDK Mate is a comprehensive toolkit for managing AWS CDK deployments across multiple stacks and environments with minimal boilerplate code. It provides a flexible framework for organizing CDK stacks with clear separation between stack definition and deployment concerns. Key features include a powerful stack context management system for handling different environments (dev, test, prod), Python wrappers around CDK CLI commands for automated deployments, utilities for credential management, and best practices for multi-stack project organization. The library simplifies complex infrastructure deployments by enabling consistent configuration across environments while supporting both individual stack development and full environment deployments. CDK Mate helps development teams scale their infrastructure as code implementations while maintaining clean, testable, and maintainable code architecture.


.. _install:

Install
------------------------------------------------------------------------------

``cdk_mate`` is released on PyPI, so all you need is to:

.. code-block:: console

    $ pip install cdk-mate

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade cdk-mate
