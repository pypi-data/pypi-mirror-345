import shutil
from subprocess import CalledProcessError

import pandas as pd
import pytest
from cmip_ref_metrics_pmp.pmp_driver import _get_resource
from cmip_ref_metrics_pmp.variability_modes import ExtratropicalModesOfVariability

import cmip_ref_core.providers
from cmip_ref.solver import extract_covered_datasets
from cmip_ref_core.datasets import DatasetCollection
from cmip_ref_core.metrics import Metric


def get_first_metric_match(data_catalog: pd.DataFrame, metric: Metric) -> {pd.DataFrame}:
    # obs4mips requirement is first
    datasets = extract_covered_datasets(data_catalog, metric.data_requirements[1])
    assert len(datasets) > 0
    first_key = next(iter(datasets.keys()))

    return datasets[first_key]


@pytest.mark.xfail(reason="https://github.com/Climate-REF/climate-ref/issues/258")
def test_pdo_metric(
    cmip6_data_catalog, obs4mips_data_catalog, mocker, definition_factory, pdo_example_dir, provider
):
    metric = ExtratropicalModesOfVariability("PDO")
    metric._provider = provider
    metric_dataset = get_first_metric_match(cmip6_data_catalog, metric)

    expected_reference_filename = obs4mips_data_catalog["path"].iloc[0]

    definition = definition_factory(
        cmip6=DatasetCollection(metric_dataset, "instance_id"),
        obs4mips=DatasetCollection(
            pd.Series(
                {
                    "instance_id": "HadISST",
                    "source_id": "HadISST-1-1",
                    "variable_id": "ts",
                    "path": expected_reference_filename,
                }
            )
            .to_frame()
            .T,
            "instance_id",
        ),
    )

    def mock_run_fn(cmd, *args, **kwargs):
        # Copy the output from the test-data directory to the output directory
        output_path = definition.output_directory
        shutil.copytree(pdo_example_dir, output_path)

    # Mock the subprocess.run call to avoid running PMP
    # Instead the mock_run_call function will be called
    mock_run = mocker.patch.object(
        provider,
        "run",
        autospec=True,
        spec_set=True,
        side_effect=mock_run_fn,
    )
    result = metric.run(definition)

    mock_run.assert_called_with(
        [
            "python",
            _get_resource("pcmdi_metrics", "variability_mode/variability_modes_driver.py", False),
            "-p",
            _get_resource("cmip_ref_metrics_pmp.params", "pmp_param_MoV-ts.py", True),
            "--modnames",
            "ACCESS-ESM1-5",
            "--exp",
            "hist-GHG",
            "--realization",
            "r1i1p1f1",
            "--modpath",
            metric_dataset.path.to_list()[0],
            "--reference_data_path",
            expected_reference_filename,
            "--reference_data_name",
            "HadISST-1-1",
            "--results_dir",
            str(definition.output_directory),
            "--cmec",
            "--no_provenance",
            "--variability_mode",
            "PDO",
        ],
    )

    assert result.successful

    assert str(result.output_bundle_filename) == "output.json"

    output_bundle_path = definition.output_directory / result.output_bundle_filename

    assert output_bundle_path.exists()
    assert output_bundle_path.is_file()

    assert str(result.metric_bundle_filename) == "metric.json"

    metric_bundle_path = definition.output_directory / result.metric_bundle_filename

    assert result.successful
    assert metric_bundle_path.exists()
    assert metric_bundle_path.is_file()


def test_pdo_metric_failed(cmip6_data_catalog, mocker, definition_factory, pdo_example_dir, provider):
    metric = ExtratropicalModesOfVariability("PDO")
    metric._provider = provider
    metric_dataset = get_first_metric_match(cmip6_data_catalog, metric)

    definition = definition_factory(
        cmip6=DatasetCollection(metric_dataset, "instance_id"),
        obs4mips=DatasetCollection(
            pd.Series(
                {
                    "instance_id": "HadISST",
                    "source_id": "HadISST-1-1",
                    "variable_id": "ts",
                    "path": "not_a_file",
                }
            )
            .to_frame()
            .T,
            "instance_id",
        ),
    )

    # Mock the subprocess.run call to avoid running PMP
    # Instead the mock_run_call function will be called
    mocker.patch.object(
        cmip_ref_core.providers.subprocess,
        "run",
        autospec=True,
        spec_set=True,
        side_effect=CalledProcessError(1, ["cmd"], "output", "stderr"),
    )

    with pytest.raises(CalledProcessError):
        metric.run(definition)


def test_mode_id_valid():
    # Test valid mode_ids and their corresponding parameter files
    valid_modes = {
        "PDO": "pmp_param_MoV-ts.py",
        "NPGO": "pmp_param_MoV-ts.py",
        "AMO": "pmp_param_MoV-ts.py",
        "NAO": "pmp_param_MoV-psl.py",
        "NAM": "pmp_param_MoV-psl.py",
        "PNA": "pmp_param_MoV-psl.py",
        "NPO": "pmp_param_MoV-psl.py",
        "SAM": "pmp_param_MoV-psl.py",
    }

    for mode_id, expected_file in valid_modes.items():
        obj = ExtratropicalModesOfVariability(mode_id)
        assert obj.parameter_file == expected_file


def test_mode_id_invalid():
    # Test an invalid mode_id
    with pytest.raises(ValueError) as excinfo:
        ExtratropicalModesOfVariability("INVALID")
    assert "Unknown mode_id 'INVALID'" in str(excinfo.value)
