import os
from pathlib import Path
from typing import Optional, List

import typer

from bigeye_cli.functions import cli_client_factory
from bigeye_cli import global_options
from bigeye_cli.bigconfig import bigconfig_options
from bigeye_cli.model.github_report import GitHubReport
from bigeye_sdk.bigconfig_validation.big_config_reports import all_reports
from bigeye_sdk.controller.metric_controller import MetricController
from bigeye_sdk.controller.metric_suite_controller import MetricSuiteController
from bigeye_sdk.generated.com.bigeye.models.generated import MetricInfoList
from bigeye_sdk.model.protobuf_message_facade import SimpleCollection
from bigeye_sdk.log import get_logger

log = get_logger(__file__)

app = typer.Typer(no_args_is_help=True, help="Bigconfig Commands for Bigeye CLI")

"""
File should contain commands relating to deploying Bigconfig files.
"""


@app.command()
def plan(
    bigeye_conf: str = global_options.bigeye_conf,
    config_file: str = global_options.config_file,
    workspace: str = global_options.workspace,
    input_path: Optional[List[str]] = bigconfig_options.input_path,
    output_path: str = bigconfig_options.output_path,
    purge_source_names: Optional[List[str]] = bigconfig_options.purge_source_names,
    purge_all_sources: bool = bigconfig_options.purge_all_sources,
    no_queue: bool = bigconfig_options.no_queue,
    recursive: bool = bigconfig_options.recursive,
    strict_mode: bool = bigconfig_options.strict_mode,
    cicd: bool = typer.Option(
        False,
        "--cicd_report",
        "-cicd",
        help="Add the report to a pull request. (Github only)",
    ),
):
    """Executes a plan for purging sources or processing bigconfig files in the input path/current
    working directory."""

    client = cli_client_factory(bigeye_conf, config_file, workspace)
    mc = MetricSuiteController(client=client)

    # Resolve args to first true or first non None values
    if not input_path:
        input_path = client.config.bigconfig_input_path or [Path.cwd()]
    if not output_path:
        output_path = client.config.bigconfig_output_path or Path.cwd()
    strict_mode = strict_mode or client.config.bigconfig_strict_mode

    if purge_source_names or purge_all_sources:
        report = mc.execute_purge(
            purge_source_names=purge_source_names,
            purge_all_sources=purge_all_sources,
            output_path=output_path,
            apply=False,
        )
    else:
        if no_queue:
            log.warning(
                "The --no_queue flag is deprecated. The option will be ignored now and removed in a later version."
            )
        report = mc.execute_bigconfig(
            input_path=input_path,
            output_path=output_path,
            apply=False,
            recursive=recursive,
            strict_mode=strict_mode,
        )
    if cicd:
        gh_report = GitHubReport(github_token=os.environ["GITHUB_TOKEN"])
        gh_report.publish_bigconfig(console_report=report, file_reports=all_reports())


@app.command()
def apply(
    bigeye_conf: str = global_options.bigeye_conf,
    config_file: str = global_options.config_file,
    workspace: str = global_options.workspace,
    input_path: Optional[List[str]] = bigconfig_options.input_path,
    output_path: str = bigconfig_options.output_path,
    purge_source_names: Optional[List[str]] = bigconfig_options.purge_source_names,
    purge_all_sources: bool = bigconfig_options.purge_all_sources,
    no_queue: bool = bigconfig_options.no_queue,
    recursive: bool = bigconfig_options.recursive,
    strict_mode: bool = bigconfig_options.strict_mode,
    auto_approve: bool = bigconfig_options.auto_approve,
):
    """Applies a purge of deployed metrics or applies Bigconfig files from the input path/current working directory to
    the Bigeye workspace."""

    client = cli_client_factory(bigeye_conf, config_file, workspace)
    mc = MetricSuiteController(client=client)

    # Resolve args to first true or first non None values
    if not input_path:
        input_path = client.config.bigconfig_input_path or [Path.cwd()]
    if not output_path:
        output_path = client.config.bigconfig_output_path or Path.cwd()
    strict_mode = strict_mode or client.config.bigconfig_strict_mode
    auto_approve = auto_approve or client.config.bigconfig_auto_approve

    if purge_source_names or purge_all_sources:
        mc.execute_purge(
            purge_source_names=purge_source_names,
            purge_all_sources=purge_all_sources,
            output_path=output_path,
            apply=True,
        )
    else:
        if no_queue:
            log.warning(
                "The --no_queue flag is deprecated. The option will be ignored now and removed in a later version."
            )
        mc.execute_bigconfig(
            input_path=input_path,
            output_path=output_path,
            apply=True,
            recursive=recursive,
            strict_mode=strict_mode,
            auto_approve=auto_approve,
        )


@app.command()
def export(
    bigeye_conf: str = global_options.bigeye_conf,
    config_file: str = global_options.config_file,
    workspace: str = global_options.workspace,
    output_path: str = bigconfig_options.output_path,
    collection_id: int = typer.Option(
        None, "--collection_id", "-cid", help="Collection ID of metrics to be exported."
    ),
    table_id: int = typer.Option(
        None, "--table_id", "-tid", help="Table ID of metrics to be exported."
    ),
    metric_ids: List[int] = typer.Option(
        None, "--metric_id", "-mid", help="Metric ID of metrics to be exported."
    ),
):
    """Exports existing metrics into a valid Bigconfig file."""

    client = cli_client_factory(bigeye_conf, config_file, workspace)
    mc = MetricController(client=client)
    collection: SimpleCollection = SimpleCollection(
        name="Sample", description="SDK Generated"
    )

    final_metric_ids: List[int] = []

    # Require at least 1 option to be specified
    if not collection_id and not table_id and not metric_ids:
        raise typer.BadParameter(
            "At least 1 option must be provided for bigconfig export. Please provide the "
            "collection id (-cid), table id (-tid), or list of metric ids (-mid). "
        )

    # Add metric ids if passed
    if metric_ids:
        final_metric_ids.extend(metric_ids)

    # Get existing collection if passed
    if collection_id:
        collection: SimpleCollection = SimpleCollection.from_datawatch_object(
            client.get_collection(collection_id=collection_id).collection
        )
        final_metric_ids.extend(collection.metric_ids)

    # Get metrics from table if passed
    if table_id:
        metrics_from_table = client.get_metric_info_batch_post(
            table_ids=[table_id]
        ).metrics
        final_metric_ids.extend([m.metric_configuration.id for m in metrics_from_table])
        if not metrics_from_table:
            raise typer.BadParameter(
                f"No metrics found for given table id. Please check arguments and try again."
            )
        if not collection_id:
            collection.name = metrics_from_table[0].metric_metadata.dataset_name

    # Pull metric information
    metrics: MetricInfoList = client.get_metric_info_batch_post(metric_ids=final_metric_ids)

    if not output_path:
        output_path = client.config.bigconfig_output_path or Path.cwd()

    if not metrics.metrics:
        raise typer.BadParameter(
            "No metrics found for given arguments. Please check again."
        )

    bigconfig = mc.metric_info_to_bigconfig(metric_info=metrics, collection=collection)

    file_name = collection.name.lower().replace(" ", "_")
    output = bigconfig.save(
        output_path=output_path,
        default_file_name=f"{file_name}.bigconfig",
        custom_formatter=bigconfig.format_bigconfig_export,
    )
    typer.secho(
        f"\nSample bigconfig file generated at: {output}\n", fg="green", bold=True
    )
