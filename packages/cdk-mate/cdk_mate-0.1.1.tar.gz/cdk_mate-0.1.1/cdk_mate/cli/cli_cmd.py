# -*- coding: utf-8 -*-

"""
AWS CDK CLI Command Wrapper

Provides convenient Python wrappers for AWS CDK CLI commands (synth, deploy, destroy, etc ...)
with comprehensive option handling and flexible execution support.

.. code-block:: python

    deploy(
        stacks=["MyStack"],
        profile="my_aws_profile",
        require_approval="never"
    )
"""

import typing as T

from func_args import NOTHING

from .cli_utils import (
    process_value_arg,
    process_bool_arg,
    process_key_value_arg,
    process_array_arg,
    process_global_options,
    run_cdk_command,
)

if T.TYPE_CHECKING:  # pragma: no cover
    from pathlib_mate import T_PATH_ARG
    from boto_session_manager import BotoSesManager


def synth(
    bsm: T.Optional["BotoSesManager"] = None,
    dir_cdk: T.Optional["T_PATH_ARG"] = None,
    # --- command options ---
    exclusively: bool = NOTHING,
    quiet: bool = NOTHING,
    validation: bool = NOTHING,
    # --- global options ---
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
    Synthesize AWS CDK stacks into CloudFormation templates with comprehensive configuration options.

    Ref: https://docs.aws.amazon.com/cdk/v2/guide/ref-cli-cmd-synth.html
    """
    args = ["cdk", "synth"]
    # Process command options
    process_bool_arg("exclusively", exclusively, args)
    process_bool_arg("quiet", quiet, args)
    process_bool_arg("validation", validation, args)
    # Process global options
    process_global_options(
        args=args,
        app=app,
        asset_metadata=asset_metadata,
        builder=builder,
        ca_bundle_path=ca_bundle_path,
        ci=ci,
        context=context,
        debug=debug,
        ec2creds=ec2creds,
        help=help,
        ignore_errors=ignore_errors,
        json=json,
        lookups=lookups,
        no_color=no_color,
        notices=notices,
        output=output,
        path_metadata=path_metadata,
        plugin=plugin,
        profile=profile,
        proxy=proxy,
        role_arn=role_arn,
        staging=staging,
        strict=strict,
        trace=trace,
        verbose=verbose,
        version=version,
        version_reporting=version_reporting,
    )
    return run_cdk_command(bsm=bsm, dir_cdk=dir_cdk, args=args)


def deploy(
    bsm: T.Optional["BotoSesManager"] = None,
    dir_cdk: T.Optional["T_PATH_ARG"] = None,
    stacks: list[str] = NOTHING,
    # --- command options ---
    all: bool = NOTHING,
    asset_parallelism: bool = NOTHING,
    asset_prebuild: bool = NOTHING,
    build_exclude: list[str] = NOTHING,
    change_set_name: str = NOTHING,
    concurrency: int = NOTHING,
    exclusively: bool = NOTHING,
    force: bool = NOTHING,
    hotswap: bool = NOTHING,
    hotswap_fallback: bool = NOTHING,
    ignore_no_stacks: bool = NOTHING,
    import_existing_resources: bool = NOTHING,
    logs: bool = NOTHING,
    method: str = NOTHING,
    notification_arns: list[str] = NOTHING,
    outputs_file: str = NOTHING,
    parameters: dict[str, str] = NOTHING,
    previous_parameters: bool = NOTHING,
    progress: str = NOTHING,
    require_approval: str = NOTHING,
    rollback: bool = NOTHING,
    toolkit_stack_name: str = NOTHING,
    watch: bool = NOTHING,
    # --- global options ---
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
    Deploy AWS CDK stacks to AWS infrastructure with granular control over deployment parameters.

    Ref: https://docs.aws.amazon.com/cdk/v2/guide/ref-cli-cmd-deploy.html
    """
    args = ["cdk", "deploy"]

    # Add stack IDs if provided
    if stacks is not NOTHING and stacks:
        args.extend(stacks)

    # Process command options
    process_bool_arg("all", all, args)
    process_bool_arg("asset-parallelism", asset_parallelism, args)
    process_bool_arg("asset-prebuild", asset_prebuild, args)
    process_array_arg("build-exclude", build_exclude, args)
    process_value_arg("change-set-name", change_set_name, args)
    process_value_arg("concurrency", concurrency, args)
    process_bool_arg("exclusively", exclusively, args)
    process_bool_arg("force", force, args)
    process_bool_arg("hotswap", hotswap, args)
    process_bool_arg("hotswap-fallback", hotswap_fallback, args)
    process_bool_arg("ignore-no-stacks", ignore_no_stacks, args)
    process_bool_arg("import-existing-resources", import_existing_resources, args)
    process_bool_arg("logs", logs, args)
    process_value_arg("method", method, args)
    process_array_arg("notification-arns", notification_arns, args)
    process_value_arg("outputs-file", outputs_file, args)
    process_key_value_arg("parameters", parameters, args)
    process_bool_arg("previous-parameters", previous_parameters, args)
    process_value_arg("progress", progress, args)
    process_value_arg("require-approval", require_approval, args)

    # Special handling for rollback (can be --rollback or --no-rollback)
    if rollback is not NOTHING:
        if rollback:
            args.append("--rollback")
        else:
            args.append("--no-rollback")

    process_value_arg("toolkit-stack-name", toolkit_stack_name, args)
    process_bool_arg("watch", watch, args)

    # Process global options
    process_global_options(
        args=args,
        app=app,
        asset_metadata=asset_metadata,
        builder=builder,
        ca_bundle_path=ca_bundle_path,
        ci=ci,
        context=context,
        debug=debug,
        ec2creds=ec2creds,
        help=help,
        ignore_errors=ignore_errors,
        json=json,
        lookups=lookups,
        no_color=no_color,
        notices=notices,
        output=output,
        path_metadata=path_metadata,
        plugin=plugin,
        profile=profile,
        proxy=proxy,
        role_arn=role_arn,
        staging=staging,
        strict=strict,
        trace=trace,
        verbose=verbose,
        version=version,
        version_reporting=version_reporting,
    )

    return run_cdk_command(bsm=bsm, dir_cdk=dir_cdk, args=args)


def destroy(
    bsm: T.Optional["BotoSesManager"] = None,
    dir_cdk: T.Optional["T_PATH_ARG"] = None,
    stacks: list[str] = NOTHING,
    # --- command options ---
    all: bool = NOTHING,
    exclusively: bool = NOTHING,
    force: bool = NOTHING,
    # --- global options ---
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
    Safely remove AWS CDK stacks from infrastructure with flexible destruction options.

    Ref: https://docs.aws.amazon.com/cdk/v2/guide/ref-cli-cmd-deploy.html
    """
    args = ["cdk", "destroy"]

    # Add stack IDs if provided
    if stacks is not NOTHING and stacks:
        args.extend(stacks)

    # Process command options
    process_bool_arg("all", all, args)
    process_bool_arg("exclusively", exclusively, args)
    process_bool_arg("force", force, args)

    # Process global options
    process_global_options(
        args=args,
        app=app,
        asset_metadata=asset_metadata,
        builder=builder,
        ca_bundle_path=ca_bundle_path,
        ci=ci,
        context=context,
        debug=debug,
        ec2creds=ec2creds,
        help=help,
        ignore_errors=ignore_errors,
        json=json,
        lookups=lookups,
        no_color=no_color,
        notices=notices,
        output=output,
        path_metadata=path_metadata,
        plugin=plugin,
        profile=profile,
        proxy=proxy,
        role_arn=role_arn,
        staging=staging,
        strict=strict,
        trace=trace,
        verbose=verbose,
        version=version,
        version_reporting=version_reporting,
    )
    return run_cdk_command(bsm=bsm, dir_cdk=dir_cdk, args=args)
