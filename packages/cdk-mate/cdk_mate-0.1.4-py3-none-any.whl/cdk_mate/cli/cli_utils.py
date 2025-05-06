# -*- coding: utf-8 -*-

"""
Utility Functions for AWS CDK CLI Command Processing

This module provides a set of utility classes and functions for handling AWS CDK CLI
command arguments, execution contexts, and environment management.
"""

import typing as T
import subprocess
import contextlib
from pathlib import Path

from func_args.api import OPT

from ..vendor.better_pathlib import temp_cwd


if T.TYPE_CHECKING:  # pragma: no cover
    from boto_session_manager import BotoSesManager
    from pathlib_mate import T_PATH_ARG


class BaseArgType:
    """
    Base class for CLI argument type processors.

    Defines the interface for processing different types of CLI arguments
    when building command lines for AWS CDK operations.
    """

    def process(
        self,
        name: str,
        value: T.Any,
        args: list[str],
    ):  # pragma: no cover
        """
        Process an argument for CLI commands.

        :param name: The name of the argument (without '--' prefix)
        :param value: The value of the argument, can be NOTHING or any value
        :param args: The list of arguments to append the processed argument to

        :return: None, modifies the args list in-place
        """
        raise NotImplementedError


class PositionalArg(BaseArgType):
    """
    Process a positional argument for CLI commands.

    Example::

        name = "id"
        value = "my-stack"
        # will be encoded as
        "my-stack"
    """

    def process(
        self,
        name: str,
        value: T.Any,
        args: list[str],
    ):
        if value is OPT:
            return
        if value:
            if isinstance(value, list):
                for item in value:
                    args.append(str(item))
            else:
                args.append(str(value))


class ValueArg(BaseArgType):
    """
    Process a standard value argument for CLI commands.

    Example::

        name = "stack"
        value = "my-stack"
        # will be encoded as
        "--stack my-stack"
    """

    def process(
        self,
        name: str,
        value: T.Any,
        args: list[str],
    ):
        if value is OPT:
            return
        if value:
            args.append(f"--{name}")
            args.append(str(value))


class BoolArg(BaseArgType):
    """
    Process a boolean argument for CLI commands.

    Example::

        name = "help"
        value = True
        # will be encoded as
        "--help"
    """

    def process(
        self,
        name: str,
        value: T.Union[T.Literal["OPT"], bool],
        args: list[str],
    ):
        if value is OPT:
            return
        if value:
            args.append(f"--{name}")


class KeyValueArg(BaseArgType):
    """
    Process a key-value pair argument for CLI commands.

    Example::

        name = "parameter"
        value = {"key1": "value1", "key2": "value2"}
        # will be encoded as
        "--parameter key1=value1 --parameter key2=value2"
    """

    def process(
        self,
        name: str,
        value: T.Union[T.Literal["OPT"], dict[str, str]],
        args: list[str],
    ):
        if value is OPT:
            return
        if value:
            for k, v in value.items():
                args.append(f"--{name}")
                args.append(f"{k}={v}")


class ArrayArg(BaseArgType):
    """
    Process array-type arguments for CLI commands.

    Example::

        name = "plugin"
        value = ["plugin1", "plugin2"]
        # will be encoded as
        "--plugin plugin1 --plugin plugin2"
    """

    def process(
        self,
        name: str,
        value: T.Union[T.Literal["OPT"], list[str]],
        args: list[str],
    ):
        if value is OPT:
            return
        if value:
            for item in value:
                args.append(f"--{name}")
                args.append(str(item))


class CountArg(BaseArgType):
    """
    Process count-based arguments for CLI commands.

    Example::

        name = "verbose"
        value = 2
        # will be encoded as
        "--verbose --verbose"
    """

    def process(
        self,
        name: str,
        value: T.Union[T.Literal["OPT"], int],
        args: list[str],
    ):
        if value is OPT:
            return
        if value:
            for _ in range(value):
                args.append(f"--{name}")


pos_arg = PositionalArg()
value_arg = ValueArg()
bool_arg = BoolArg()
kv_arg = KeyValueArg()
array_arg = ArrayArg()
count_arg = CountArg()


def run_cmd_v1(
    args: list[str],
) -> subprocess.CompletedProcess:  # pragma: no cover
    """
    Run a terminal command using subprocess with standard output.
    """
    cmd = " ".join(args)
    print(f"--- Run command ---")
    print(cmd)
    return subprocess.run(args, check=True)


def run_cmd_v2(
    args: list[str],
    show_output: bool = True,
) -> subprocess.CompletedProcess:  # pragma: no cover
    """
    Run a terminal command with advanced output handling.
    """
    try:
        result = subprocess.run(
            args,
            check=True,
            capture_output=True,
            encoding="utf-8",
        )
        if show_output:
            print(result.stdout)
            print(result.stderr)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error code: {e.returncode}")
        print(f"Error message:\n{e.stderr}")
        raise e


run_cmd = run_cmd_v1
# run_cmd = run_cmd_v2


def run_cdk_command(
    args: list[str],
    bsm: T.Optional["BotoSesManager"] = None,
    dir_cdk: T.Optional["T_PATH_ARG"] = None,
) -> subprocess.CompletedProcess:  # pragma: no cover
    """
    Execute an AWS CDK command with optional AWS session and directory context.

    :param args: List of CDK command arguments to execute
    :param bsm: Optional Boto Session Manager for AWS credentials and context
    :param dir_cdk: Optional directory path for executing the CDK command

    :raises subprocess.CalledProcessError: If the command execution fails

    :return: Completed process result from subprocess
    """
    with contextlib.ExitStack() as stack:
        bsm_tmp = None if bsm is None else stack.enter_context(bsm.awscli())
        if bsm is not None:
            print("--- Using boto session ---")
            bsm.print_who_am_i(masked=True)
        if dir_cdk is not None:
            print(f"---Using CDK directory ---")
            print(dir_cdk)
        if dir_cdk is None:
            tmp_cwd = None
        else:
            new_dir_cdk = Path(str(dir_cdk)).absolute()
            if new_dir_cdk.is_file():
                new_dir_cdk = new_dir_cdk.parent
            tmp_cdk = stack.enter_context(temp_cwd(new_dir_cdk))
        return run_cmd(args)
