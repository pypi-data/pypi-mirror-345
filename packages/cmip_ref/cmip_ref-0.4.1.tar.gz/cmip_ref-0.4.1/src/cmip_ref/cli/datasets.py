"""
View and ingest input datasets
"""

import errno
import os
import shutil
from collections.abc import Iterable
from pathlib import Path
from typing import Annotated

import typer
from loguru import logger
from rich.console import Console

from cmip_ref.cli._utils import pretty_print_df
from cmip_ref.datasets import get_dataset_adapter
from cmip_ref.models import Dataset
from cmip_ref.provider_registry import ProviderRegistry
from cmip_ref.solver import solve_metrics
from cmip_ref.testing import fetch_sample_data
from cmip_ref_core.dataset_registry import dataset_registry_manager, fetch_all_files
from cmip_ref_core.datasets import SourceDatasetType

app = typer.Typer(help=__doc__)
console = Console()


@app.command(name="list")
def list_(
    ctx: typer.Context,
    source_type: Annotated[
        SourceDatasetType, typer.Option(help="Type of source dataset")
    ] = SourceDatasetType.CMIP6.value,  # type: ignore
    column: Annotated[list[str] | None, typer.Option()] = None,
    include_files: bool = typer.Option(False, help="Include files in the output"),
    limit: int = typer.Option(100, help="Limit the number of rows to display"),
) -> None:
    """
    List the datasets that have been ingested

    The data catalog is sorted by the date that the dataset was ingested (first = newest).
    """
    database = ctx.obj.database

    adapter = get_dataset_adapter(source_type.value)
    data_catalog = adapter.load_catalog(database, include_files=include_files, limit=limit)

    if column:
        missing = set(column) - set(data_catalog.columns)
        if missing:

            def format_(columns: Iterable[str]) -> str:
                return ", ".join(f"'{c}'" for c in sorted(columns))

            logger.error(
                f"Column{'s' if len(missing) > 1 else ''} "
                f"{format_(missing)} not found in data catalog. "
                f"Choose from: {format_(data_catalog.columns)}"
            )
            raise typer.Exit(code=1)
        data_catalog = data_catalog[column].sort_values(by=column)

    pretty_print_df(data_catalog, console=console)


@app.command()
def list_columns(
    ctx: typer.Context,
    source_type: Annotated[
        SourceDatasetType, typer.Option(help="Type of source dataset")
    ] = SourceDatasetType.CMIP6.value,  # type: ignore
    include_files: bool = typer.Option(False, help="Include files in the output"),
) -> None:
    """
    Print the current cmip_ref configuration

    If a configuration directory is provided,
    the configuration will attempt to load from the specified directory.
    """
    database = ctx.obj.database

    adapter = get_dataset_adapter(source_type.value)
    data_catalog = adapter.load_catalog(database, include_files=include_files)

    for column in sorted(data_catalog.columns.to_list()):
        print(column)


@app.command()
def ingest(  # noqa: PLR0913
    ctx: typer.Context,
    file_or_directory: Path,
    source_type: Annotated[SourceDatasetType, typer.Option(help="Type of source dataset")],
    solve: Annotated[bool, typer.Option(help="Solve for new metric executions after ingestion")] = False,
    dry_run: Annotated[bool, typer.Option(help="Do not ingest datasets into the database")] = False,
    n_jobs: Annotated[int | None, typer.Option(help="Number of jobs to run in parallel")] = None,
    skip_invalid: Annotated[
        bool, typer.Option(help="Ignore (but log) any datasets that don't pass validation")
    ] = False,
) -> None:
    """
    Ingest a dataset

    This will register a dataset in the database to be used for metrics calculations.
    """
    config = ctx.obj.config
    db = ctx.obj.database

    file_or_directory = Path(file_or_directory).expanduser()
    logger.info(f"ingesting {file_or_directory}")

    kwargs = {}

    if n_jobs is not None:
        kwargs["n_jobs"] = n_jobs

    adapter = get_dataset_adapter(source_type.value, **kwargs)

    # Create a data catalog from the specified file or directory
    if not file_or_directory.exists():
        logger.error(f"File or directory {file_or_directory} does not exist")
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), file_or_directory)

    data_catalog = adapter.find_local_datasets(file_or_directory)
    data_catalog = adapter.validate_data_catalog(data_catalog, skip_invalid=skip_invalid)

    logger.info(
        f"Found {len(data_catalog)} files for {len(data_catalog[adapter.slug_column].unique())} datasets"
    )
    pretty_print_df(adapter.pretty_subset(data_catalog), console=console)

    for instance_id, data_catalog_dataset in data_catalog.groupby(adapter.slug_column):
        logger.info(f"Processing dataset {instance_id}")

        if dry_run:
            dataset = db.session.query(Dataset).filter_by(slug=instance_id, dataset_type=source_type).first()
            if not dataset:
                logger.info(f"Would save dataset {instance_id} to the database")
                continue
        else:
            with db.session.begin():
                adapter.register_dataset(config, db, data_catalog_dataset)

    if solve:
        solve_metrics(
            config=config,
            db=db,
            dry_run=dry_run,
        )


@app.command(name="fetch-sample-data")
def _fetch_sample_data(
    force_cleanup: Annotated[bool, typer.Option(help="If True, remove any existing files")] = False,
    symlink: Annotated[
        bool, typer.Option(help="If True, symlink files into the output directory, otherwise perform a copy")
    ] = False,
) -> None:
    """
    Fetch the sample data for the given version.

    These data will be written into the test data directory.
    This operation may fail if the test data directory does not exist,
    as is the case for non-source-based installations.
    """
    fetch_sample_data(force_cleanup=force_cleanup, symlink=symlink)


@app.command(name="fetch-data")
def fetch_data(
    ctx: typer.Context,
    registry: Annotated[str, typer.Option(help="Name of the data registry to use")],
    output_directory: Annotated[
        Path | None, typer.Option(help="Output directory where files will be saved")
    ] = None,
    force_cleanup: Annotated[bool, typer.Option(help="If True, remove any existing files")] = False,
    symlink: Annotated[
        bool, typer.Option(help="If True, symlink files into the output directory, otherwise perform a copy")
    ] = False,
) -> None:
    """
    Fetch REF-specific datasets

    These datasets have been verified to have open licenses
    and are in the process of being added to Obs4MIPs.
    """
    config = ctx.obj.config
    db = ctx.obj.database

    # Setup the provider registry to register any dataset registries in the configured providers
    ProviderRegistry.build_from_config(config, db)

    if output_directory and force_cleanup and output_directory.exists():
        logger.warning(f"Removing existing directory {output_directory}")
        shutil.rmtree(output_directory)

    try:
        _registry = dataset_registry_manager[registry]
    except KeyError:
        logger.error(f"Registry {registry} not found")
        logger.error(f"Available registries: {', '.join(dataset_registry_manager.keys())}")
        raise typer.Exit(code=1)

    fetch_all_files(_registry, registry, output_directory, symlink=symlink)
