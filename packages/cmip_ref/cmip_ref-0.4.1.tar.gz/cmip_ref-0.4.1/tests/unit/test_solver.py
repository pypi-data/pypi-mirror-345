from typing import Any
from unittest import mock

import pandas as pd
import pytest
from cmip_ref_metrics_example import provider

from cmip_ref.config import ExecutorConfig
from cmip_ref.models import MetricExecutionResult
from cmip_ref.provider_registry import ProviderRegistry
from cmip_ref.solver import (
    MetricExecution,
    MetricSolver,
    extract_covered_datasets,
    solve_metric_executions,
    solve_metrics,
)
from cmip_ref_core.constraints import AddSupplementaryDataset, RequireFacets, SelectParentExperiment
from cmip_ref_core.datasets import SourceDatasetType
from cmip_ref_core.metrics import DataRequirement, FacetFilter


@pytest.fixture
def solver(db_seeded, config) -> MetricSolver:
    registry = ProviderRegistry(providers=[provider])
    # Use a fixed set of providers for the test suite until we can pull from the DB
    with db_seeded.session.begin():
        metric_solver = MetricSolver.build_from_db(config, db_seeded)
    metric_solver.provider_registry = registry

    return metric_solver


@pytest.fixture
def mock_metric_execution(tmp_path, definition_factory) -> MetricExecution:
    mock_execution = mock.MagicMock(spec=MetricExecution)
    mock_execution.provider = provider
    mock_execution.metric = provider.metrics()[0]
    mock_execution.selectors = {"cmip6": (("source_id", "Test"),)}

    mock_metric_dataset = mock.Mock(hash="123456", items=mock.Mock(return_value=[]))

    mock_execution.build_metric_execution_info.return_value = definition_factory(
        metric_dataset=mock_metric_dataset
    )
    return mock_execution


class TestMetricSolver:
    def test_solver_build_from_db(self, solver):
        assert isinstance(solver, MetricSolver)
        assert isinstance(solver.provider_registry, ProviderRegistry)
        assert SourceDatasetType.CMIP6 in solver.data_catalog
        assert isinstance(solver.data_catalog[SourceDatasetType.CMIP6], pd.DataFrame)
        assert len(solver.data_catalog[SourceDatasetType.CMIP6])


@pytest.mark.parametrize(
    "requirement,data_catalog,expected",
    [
        pytest.param(
            DataRequirement(
                source_type=SourceDatasetType.CMIP6,
                filters=(),
                group_by=None,
            ),
            pd.DataFrame(
                {
                    "variable_id": ["tas", "tas", "pr"],
                    "experiment_id": ["ssp119", "ssp126", "ssp119"],
                    "variant_label": ["r1i1p1f1", "r1i1p1f1", "r1i1p1f1"],
                }
            ),
            {
                (): pd.DataFrame(
                    {
                        "variable_id": ["tas", "tas", "pr"],
                        "experiment_id": ["ssp119", "ssp126", "ssp119"],
                        "variant_label": ["r1i1p1f1", "r1i1p1f1", "r1i1p1f1"],
                    }
                )
            },
            id="group-by-none",
        ),
        pytest.param(
            DataRequirement(
                source_type=SourceDatasetType.CMIP6,
                filters=(FacetFilter(facets={"variable_id": "missing"}),),
                group_by=("variable_id", "experiment_id"),
            ),
            pd.DataFrame(
                {
                    "variable_id": ["tas", "tas", "pr"],
                    "experiment_id": ["ssp119", "ssp126", "ssp119"],
                    "variant_label": ["r1i1p1f1", "r1i1p1f1", "r1i1p1f1"],
                }
            ),
            {},
            id="empty",
        ),
        pytest.param(
            DataRequirement(
                source_type=SourceDatasetType.CMIP6,
                filters=(FacetFilter(facets={"variable_id": "tas"}),),
                group_by=("variable_id", "experiment_id"),
            ),
            pd.DataFrame(
                {
                    "variable_id": ["tas", "tas", "pr"],
                    "experiment_id": ["ssp119", "ssp126", "ssp119"],
                    "variant_label": ["r1i1p1f1", "r1i1p1f1", "r1i1p1f1"],
                }
            ),
            {
                (("variable_id", "tas"), ("experiment_id", "ssp119")): pd.DataFrame(
                    {
                        "variable_id": ["tas"],
                        "experiment_id": ["ssp119"],
                        "variant_label": ["r1i1p1f1"],
                    },
                    index=[0],
                ),
                (("variable_id", "tas"), ("experiment_id", "ssp126")): pd.DataFrame(
                    {
                        "variable_id": ["tas"],
                        "experiment_id": ["ssp126"],
                        "variant_label": ["r1i1p1f1"],
                    },
                    index=[1],
                ),
            },
            id="simple-filter",
        ),
        pytest.param(
            DataRequirement(
                source_type=SourceDatasetType.CMIP6,
                filters=(FacetFilter(facets={"variable_id": ("tas", "pr")}),),
                group_by=("experiment_id",),
            ),
            pd.DataFrame(
                {
                    "variable_id": ["tas", "tas", "pr"],
                    "experiment_id": ["ssp119", "ssp126", "ssp119"],
                }
            ),
            {
                (("experiment_id", "ssp119"),): pd.DataFrame(
                    {
                        "variable_id": ["tas", "pr"],
                        "experiment_id": ["ssp119", "ssp119"],
                    },
                    index=[0, 2],
                ),
                (("experiment_id", "ssp126"),): pd.DataFrame(
                    {
                        "variable_id": ["tas"],
                        "experiment_id": ["ssp126"],
                    },
                    index=[1],
                ),
            },
            id="simple-or",
        ),
        pytest.param(
            DataRequirement(
                source_type=SourceDatasetType.CMIP6,
                filters=(FacetFilter(facets={"variable_id": ("tas", "pr")}),),
                constraints=(SelectParentExperiment(),),
                group_by=("variable_id", "experiment_id"),
            ),
            pd.DataFrame(
                {
                    "variable_id": ["tas", "tas"],
                    "experiment_id": ["ssp119", "historical"],
                    "parent_experiment_id": ["historical", "none"],
                }
            ),
            {
                (("variable_id", "tas"), ("experiment_id", "ssp119")): pd.DataFrame(
                    {
                        "variable_id": ["tas", "tas"],
                        "experiment_id": ["historical", "ssp119"],
                    },
                    # The order of the rows is not guaranteed
                    index=[1, 0],
                ),
                (("variable_id", "tas"), ("experiment_id", "historical")): pd.DataFrame(
                    {
                        "variable_id": ["tas", "tas"],
                        "experiment_id": ["historical"],
                    },
                    # The order of the rows is not guaranteed
                    index=[1, 0],
                ),
            },
            marks=[pytest.mark.xfail(reason="Parent experiment not implemented")],
            id="parent",
        ),
        pytest.param(
            DataRequirement(
                source_type=SourceDatasetType.CMIP6,
                filters=(FacetFilter(facets={"variable_id": ("tas", "pr")}),),
                constraints=(RequireFacets(dimension="variable_id", required_facets=["tas", "pr"]),),
                group_by=("experiment_id",),
            ),
            pd.DataFrame(
                {
                    "variable_id": ["tas", "tas", "pr"],
                    "experiment_id": ["ssp119", "ssp126", "ssp119"],
                }
            ),
            {
                (("experiment_id", "ssp119"),): pd.DataFrame(
                    {
                        "variable_id": ["tas", "pr"],
                        "experiment_id": ["ssp119", "ssp119"],
                    },
                    index=[0, 2],
                ),
            },
            id="simple-validation",
        ),
        pytest.param(
            DataRequirement(
                source_type=SourceDatasetType.obs4MIPs,
                filters=(FacetFilter(facets={"variable_id": "tas"}),),
                group_by=("variable_id", "source_id"),
            ),
            pd.DataFrame(
                {
                    "variable_id": ["tas", "tas", "pr"],
                    "source_id": ["ERA-5", "AIRX3STM-006", "GPCPMON-3-1"],
                    "frequency": ["mon", "mon", "mon"],
                }
            ),
            {
                (("variable_id", "tas"), ("source_id", "AIRX3STM-006")): pd.DataFrame(
                    {
                        "variable_id": ["tas"],
                        "source_id": ["AIRX3STM-006"],
                        "frequency": ["mon"],
                    },
                    index=[1],
                ),
                (("variable_id", "tas"), ("source_id", "ERA-5")): pd.DataFrame(
                    {
                        "variable_id": ["tas"],
                        "source_id": ["ERA-5"],
                        "frequency": ["mon"],
                    },
                    index=[0],
                ),
            },
            id="simple-obs4MIPs",
        ),
    ],
)
def test_data_coverage(requirement, data_catalog, expected):
    result = extract_covered_datasets(data_catalog, requirement)

    for key, expected_value in expected.items():
        pd.testing.assert_frame_equal(result[key], expected_value)
    assert len(result) == len(expected)


def test_extract_no_groups():
    requirement = DataRequirement(
        source_type=SourceDatasetType.CMIP6,
        filters=(),
        group_by=(),
    )
    data_catalog = pd.DataFrame(
        {
            "variable_id": ["tas", "tas", "pr"],
        }
    )

    with pytest.raises(ValueError, match="No group keys passed!"):
        extract_covered_datasets(data_catalog, requirement)


def test_solve_metrics_default_solver(mocker, mock_metric_execution, db_seeded, solver):
    mock_executor = mocker.patch.object(ExecutorConfig, "build")
    mock_build_solver = mocker.patch.object(MetricSolver, "build_from_db")

    # Create a mock solver that "solves" to create a single execution
    solver = mock.MagicMock(spec=MetricSolver)
    solver.solve.return_value = [mock_metric_execution]
    mock_build_solver.return_value = solver

    # Run with no solver specified
    with db_seeded.session.begin():
        solve_metrics(db_seeded)

    # Check that a result is created
    assert db_seeded.session.query(MetricExecutionResult).count() == 1
    execution_result = db_seeded.session.query(MetricExecutionResult).first()
    assert execution_result.output_fragment == "output_fragment"
    assert execution_result.dataset_hash == "123456"
    assert execution_result.metric_execution_group.dataset_key == "key"
    # Nested tuples are converted into nested lists after going through the DB
    assert execution_result.metric_execution_group.selectors == {
        "cmip6": [
            ["source_id", "Test"],
        ]
    }

    # Solver should be created
    assert mock_build_solver.call_count == 1
    # A single run would have been run
    assert mock_executor.return_value.run_metric.call_count == 1
    mock_executor.return_value.run_metric.assert_called_with(
        provider=mock_metric_execution.provider,
        metric=mock_metric_execution.metric,
        definition=mock_metric_execution.build_metric_execution_info(),
        metric_execution_result=execution_result,
    )


def test_solve_metrics(mocker, db_seeded, solver, data_regression):
    mock_executor = mocker.patch.object(ExecutorConfig, "build")
    mock_build_solver = mocker.patch.object(MetricSolver, "build_from_db")

    with db_seeded.session.begin():
        solve_metrics(db_seeded, dry_run=False, solver=solver)

    assert mock_build_solver.call_count == 0

    definitions = [call.kwargs["definition"] for call in mock_executor.return_value.run_metric.mock_calls]

    # Create a dictionary of the metric key and the source datasets that were used
    output = {}
    for definition in definitions:
        output[definition.dataset_key] = {
            str(source_type): ds_collection.instance_id.unique().tolist()
            for source_type, ds_collection in definition.metric_dataset.items()
        }

    # Write to a file for regression testing
    data_regression.check(output)


def test_solve_metrics_dry_run(mocker, db_seeded, config, solver):
    mock_executor = mocker.patch.object(ExecutorConfig, "build")

    solve_metrics(config=config, db=db_seeded, dry_run=True, solver=solver)

    assert mock_executor.return_value.run_metric.call_count == 0

    # TODO: Check that no new metrics were added to the db


def test_solve_metric_executions_missing(mock_metric, provider):
    mock_metric.data_requirements = ()
    with pytest.raises(ValueError, match=f"Metric {mock_metric.slug} has no data requirements"):
        next(solve_metric_executions({}, mock_metric, provider))


def test_solve_metric_executions_mixed_data_requirements(mock_metric, provider):
    mock_metric.data_requirements = (
        DataRequirement(
            source_type=SourceDatasetType.CMIP6,
            filters=(),
            group_by=("variable_id", "source_id"),
        ),
        (
            DataRequirement(
                source_type=SourceDatasetType.CMIP6,
                filters=(),
                group_by=("variable_id", "experiment_id"),
            ),
        ),
    )
    data_catalog = {SourceDatasetType.CMIP6: pd.DataFrame()}

    with pytest.raises(TypeError, match="Expected a DataRequirement, got <class 'tuple'>"):
        next(solve_metric_executions(data_catalog, mock_metric, provider))

    mock_metric.data_requirements = mock_metric.data_requirements[::-1]
    with pytest.raises(
        TypeError,
        match="Expected a sequence of DataRequirement, got <class 'cmip_ref_core.metrics.DataRequirement'>",
    ):
        next(solve_metric_executions(data_catalog, mock_metric, provider))

    mock_metric.data_requirements = ("test",)
    with pytest.raises(TypeError, match="Expected a DataRequirement, got <class 'str'>"):
        next(solve_metric_executions(data_catalog, mock_metric, provider))

    mock_metric.data_requirements = (None,)
    with pytest.raises(TypeError, match="Expected a DataRequirement, got <class 'NoneType'>"):
        next(solve_metric_executions(data_catalog, mock_metric, provider))


@pytest.mark.parametrize("variable,expected", [("tas", 4), ("pr", 1), ("not_a_variable", 0)])
def test_solve_metric_executions(solver, mock_metric, provider, variable, expected):
    metric = mock_metric
    metric.data_requirements = (
        DataRequirement(
            source_type=SourceDatasetType.obs4MIPs,
            filters=(FacetFilter(facets={"variable_id": variable}),),
            group_by=("variable_id", "source_id"),
        ),
        DataRequirement(
            source_type=SourceDatasetType.CMIP6,
            filters=(FacetFilter(facets={"variable_id": variable}),),
            group_by=("variable_id", "experiment_id"),
        ),
    )

    data_catalog = {
        SourceDatasetType.obs4MIPs: pd.DataFrame(
            {
                "variable_id": ["tas", "tas", "pr"],
                "source_id": ["ERA-5", "AIRX3STM-006", "GPCPMON-3-1"],
                "frequency": ["mon", "mon", "mon"],
            }
        ),
        SourceDatasetType.CMIP6: pd.DataFrame(
            {
                "variable_id": ["tas", "tas", "pr"],
                "experiment_id": ["ssp119", "ssp126", "ssp119"],
                "variant_label": ["r1i1p1f1", "r1i1p1f1", "r1i1p1f1"],
            }
        ),
    }
    executions = solve_metric_executions(data_catalog, metric, provider)
    assert len(list(executions)) == expected


def test_solve_metric_executions_multiple_sets(solver, mock_metric, provider):
    metric = mock_metric
    metric.data_requirements = (
        (
            DataRequirement(
                source_type=SourceDatasetType.CMIP6,
                filters=(FacetFilter(facets={"variable_id": "tas"}),),
                group_by=("variable_id",),
            ),
        ),
        (
            DataRequirement(
                source_type=SourceDatasetType.CMIP6,
                filters=(FacetFilter(facets={"variable_id": "pr"}),),
                group_by=("variable_id", "experiment_id"),
            ),
        ),
    )

    data_catalog = {
        SourceDatasetType.CMIP6: pd.DataFrame(
            {
                "variable_id": ["tas", "tas", "pr"],
                "experiment_id": ["ssp119", "ssp126", "ssp119"],
                "variant_label": ["r1i1p1f1", "r1i1p1f1", "r1i1p1f1"],
            }
        ),
    }
    executions = list(solve_metric_executions(data_catalog, metric, provider))
    assert len(executions) == 2

    assert executions[0].metric_dataset[SourceDatasetType.CMIP6].selector == (("variable_id", "tas"),)

    assert executions[1].metric_dataset[SourceDatasetType.CMIP6].selector == (
        ("variable_id", "pr"),
        ("experiment_id", "ssp119"),
    )


def _prep_data_catalog(data_catalog: dict[str, Any]) -> pd.DataFrame:
    data_catalog_df = pd.DataFrame(data_catalog)
    data_catalog_df["instance_id"] = data_catalog_df.apply(
        lambda row: "CMIP6." + ".".join([row[item] for item in ["variable_id", "experiment_id"]]), axis=1
    )

    return data_catalog_df


def test_solve_with_new_datasets(obs4mips_data_catalog, mock_metric, provider):
    expected_dataset_key = "cmip6_ACCESS-ESM1-5_tas"
    mock_metric.data_requirements = (
        DataRequirement(
            source_type=SourceDatasetType.CMIP6,
            filters=(FacetFilter(facets={"variable_id": "tas"}),),
            group_by=("variable_id", "source_id"),
        ),
    )

    data_catalog = _prep_data_catalog(
        {
            "variable_id": ["tas", "pr"],
            "experiment_id": ["ssp119", "ssp119"],
            "source_id": "ACCESS-ESM1-5",
            "grid_label": "gn",
            "table_id": "AMon",
            "member_id": "r1i1pif1",
            "version": "v20210318",
        }
    )

    result_1 = next(
        solve_metric_executions(
            {SourceDatasetType.CMIP6: data_catalog},
            mock_metric,
            provider,
        )
    )
    assert result_1.dataset_key == expected_dataset_key

    data_catalog = _prep_data_catalog(
        {
            "variable_id": ["tas", "tas", "pr"],
            "experiment_id": ["ssp119", "ssp126", "ssp119"],
            "source_id": "ACCESS-ESM1-5",
            "grid_label": "gn",
            "table_id": "AMon",
            "member_id": "r1i1pif1",
            "version": "v20210318",
        }
    )

    result_2 = next(
        solve_metric_executions(
            {SourceDatasetType.CMIP6: data_catalog},
            mock_metric,
            provider,
        )
    )
    assert result_2.dataset_key == expected_dataset_key
    assert result_2.metric_dataset.hash != result_1.metric_dataset.hash


def test_solve_with_new_areacella(obs4mips_data_catalog, mock_metric, provider):
    expected_dataset_key = "cmip6_ssp126_ACCESS-ESM1-5_tas__obs4mips_HadISST-1-1_ts"
    mock_metric.data_requirements = (
        DataRequirement(
            source_type=SourceDatasetType.obs4MIPs,
            filters=(FacetFilter(facets={"variable_id": "ts"}),),
            group_by=("variable_id", "source_id"),
        ),
        DataRequirement(
            source_type=SourceDatasetType.CMIP6,
            filters=(FacetFilter(facets={"variable_id": "tas", "experiment_id": "ssp126"}),),
            group_by=("variable_id", "experiment_id", "source_id"),
            constraints=(AddSupplementaryDataset.from_defaults("areacella", SourceDatasetType.CMIP6),),
        ),
    )

    cmip_data_catalog = _prep_data_catalog(
        {
            "variable_id": ["tas", "tas", "pr"],
            "experiment_id": ["ssp119", "ssp126", "ssp119"],
            "source_id": "ACCESS-ESM1-5",
            "grid_label": "gn",
            "table_id": "AMon",
            "member_id": "r1i1pif1",
            "version": "v20210318",
        }
    )

    result_1 = next(
        solve_metric_executions(
            {
                SourceDatasetType.obs4MIPs: obs4mips_data_catalog,
                SourceDatasetType.CMIP6: cmip_data_catalog,
            },
            mock_metric,
            provider,
        )
    )
    assert result_1.dataset_key == expected_dataset_key

    # areacella added
    # dataset key should remain the same
    cmip_data_catalog = _prep_data_catalog(
        {
            "variable_id": ["tas", "tas", "areacella", "pr"],
            "experiment_id": ["ssp119", "ssp126", "ssp126", "ssp119"],
            "source_id": "ACCESS-ESM1-5",
            "grid_label": "gn",
            "table_id": ["AMon", "AMon", "fx", "AMon"],
            "member_id": "r1i1pif1",
            "version": "v20210318",
        }
    )
    result_2 = next(
        solve_metric_executions(
            {
                SourceDatasetType.obs4MIPs: obs4mips_data_catalog,
                SourceDatasetType.CMIP6: cmip_data_catalog,
            },
            mock_metric,
            provider,
        )
    )
    assert result_2.dataset_key == expected_dataset_key
    assert result_2.metric_dataset.hash != result_1.metric_dataset.hash
