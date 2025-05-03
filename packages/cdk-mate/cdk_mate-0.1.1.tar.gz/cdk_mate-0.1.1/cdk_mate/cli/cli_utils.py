# -*- coding: utf-8 -*-

"""
Utility Functions for AWS CDK CLI Command Processing

This module provides a set of utility functions to streamline and standardize
the processing of AWS CDK CLI command arguments, command execution, and
environment management.
"""

import typing as T
import subprocess
import contextlib
from pathlib import Path

from func_args import NOTHING

from ..vendor.better_pathlib import temp_cwd


if T.TYPE_CHECKING:  # pragma: no cover
    from boto_session_manager import BotoSesManager
    from pathlib_mate import T_PATH_ARG


T_NOTHING = T.Literal[NOTHING]


def process_value_arg(
    name: str,
    value: T.Union[T_NOTHING, T.Any],
    args: list[str],
):
    """
    Process a standard value argument for CLI commands.

    Example::

        name = "stack"
        value = "my-stack"
        # will be encoded as
        "--stack my-stack"

    :param name: The name of the argument (without '--' prefix)
    :param value: The value of the argument, can be NOTHING or any value
    :param args: The list of arguments to append the processed argument to

    :return: None, modifies the args list in-place
    """
    if value is NOTHING:
        return
    if value:
        args.append(f"--{name}")
        args.append(str(value))


def process_bool_arg(
    name: str,
    value: T.Union[T_NOTHING, bool],
    args: list[str],
):
    """
    Process a boolean argument for CLI commands.

    Example::

        name = "help"
        value = True
        # will be encoded as
        "--help"
    """
    if value is NOTHING:
        return
    if value:
        args.append(f"--{name}")


def process_key_value_arg(
    name: str,
    value: T.Union[T_NOTHING, dict[str, str]],
    args: list[str],
):
    """
    Process key-value pair arguments for CLI commands.

    Example::

        name = "parameter"
        value = {"key1": "value1", "key2": "value2"}
        # will be encoded as
        "--parameter key1=value1 --parameter key2=value2"
    """
    if value is NOTHING:
        return
    if value:
        for k, v in value.items():
            args.append(f"--{name}")
            args.append(f"{k}={v}")


def process_array_arg(
    name: str,
    value: T.Union[T_NOTHING, list[str]],
    args: list[str],
):
    """
    Process array-type arguments for CLI commands.

    Example::

        name = "plugin"
        value = ["plugin1", "plugin1"]
        # will be encoded as
        "--plugin plugin1 --plugin plugin2"
    """
    if value is NOTHING:
        return
    if value:
        for item in value:
            args.append(f"--{name}")
            args.append(str(item))


def process_count_arg(
    name: str,
    value: T.Union[T_NOTHING, int],
    args: list[str],
):
    """
    Process count-based arguments for CLI commands.

    Example::

        name = "verbose"
        value = 2
        # will be encoded as
        "--verbose --verbose"
    """
    if value is NOTHING:
        return
    if value:
        for _ in range(value):
            args.append(f"--{name}")


def process_global_options(
    args: list[str],
    app: str = NOTHING,
    asset_metadata: bool = NOTHING,
    builder: str = NOTHING,
    ca_bundle_path: str = NOTHING,
    ci: bool = NOTHING,
    context: dict[str, str] = NOTHING,
    debug: bool = NOTHING,
    ec2creds: bool = NOTHING,
    help: bool = NOTHING,
    ignore_errors: bool = NOTHING,
    json: bool = NOTHING,
    lookups: bool = NOTHING,
    no_color: bool = NOTHING,
    notices: bool = NOTHING,
    output: str = NOTHING,
    path_metadata: bool = NOTHING,
    plugin: list[str] = NOTHING,
    profile: str = NOTHING,
    proxy: str = NOTHING,
    role_arn: str = NOTHING,
    staging: bool = NOTHING,
    strict: bool = NOTHING,
    trace: bool = NOTHING,
    verbose: int = NOTHING,
    version: bool = NOTHING,
    version_reporting: bool = NOTHING,
):
    """
    Process global options for AWS CDK CLI commands.

    Applies a comprehensive set of global options to the CDK command arguments.
    Handles various configuration and runtime options for CDK commands.

    Ref: https://docs.aws.amazon.com/cdk/v2/guide/ref-cli-cmd.html
    """
    process_value_arg("app", app, args)
    process_bool_arg("asset-metadata", asset_metadata, args)
    process_value_arg("builder", builder, args)
    process_value_arg("ca-bundle-path", ca_bundle_path, args)
    process_bool_arg("ci", ci, args)
    process_key_value_arg("context", context, args)
    process_bool_arg("debug", debug, args)
    process_bool_arg("ec2creds", ec2creds, args)
    process_bool_arg("help", help, args)
    process_bool_arg("ignore-errors", ignore_errors, args)
    process_bool_arg("json", json, args)
    process_bool_arg("lookups", lookups, args)
    process_bool_arg("no-color", no_color, args)
    process_bool_arg("notices", notices, args)
    process_value_arg("output", output, args)
    process_bool_arg("path-metadata", path_metadata, args)
    process_array_arg("plugin", plugin, args)
    process_value_arg("profile", profile, args)
    process_value_arg("proxy", proxy, args)
    process_value_arg("role-arn", role_arn, args)
    process_bool_arg("staging", staging, args)
    process_bool_arg("strict", strict, args)
    process_bool_arg("trace", trace, args)
    process_count_arg("verbose", verbose, args)
    process_bool_arg("version", version, args)
    process_bool_arg("version-reporting", version_reporting, args)
    return args


def run_cmd_v1(
    args: list[str],
) -> subprocess.CompletedProcess:
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
) -> subprocess.CompletedProcess:
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
) -> subprocess.CompletedProcess:
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
