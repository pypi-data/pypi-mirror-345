from __future__ import annotations

import logging
import pathlib
import re
from dataclasses import dataclass
from typing import List

import pytest

import great_expectations.exceptions as ge_exceptions
from great_expectations.alias_types import PathStr
from great_expectations.experimental.datasources.interfaces import (
    BatchSortersDefinition,
    TestConnectionError,
)
from great_expectations.experimental.datasources.spark_datasource import (
    CSVSparkAsset,
    SparkFilesystemDatasource,
)

logger = logging.getLogger(__name__)


@pytest.fixture
def spark_filesystem_datasource(test_backends) -> SparkFilesystemDatasource:
    if "SparkDFDataset" not in test_backends:
        pytest.skip("No spark backend selected.")

    base_directory_rel_path = pathlib.Path(
        "..", "..", "test_sets", "taxi_yellow_tripdata_samples"
    )
    base_directory_abs_path = (
        pathlib.Path(__file__)
        .parent.joinpath(base_directory_rel_path)
        .resolve(strict=True)
    )
    return SparkFilesystemDatasource(
        name="spark_filesystem_datasource",
        base_directory=base_directory_abs_path,
    )


@pytest.fixture
def csv_path() -> pathlib.Path:
    relative_path = pathlib.Path(
        "..", "..", "test_sets", "taxi_yellow_tripdata_samples"
    )
    abs_csv_path = (
        pathlib.Path(__file__).parent.joinpath(relative_path).resolve(strict=True)
    )
    return abs_csv_path


@pytest.mark.unit
def test_construct_spark_filesystem_datasource(
    spark_filesystem_datasource: SparkFilesystemDatasource,
):
    assert spark_filesystem_datasource.name == "spark_filesystem_datasource"


@pytest.mark.unit
def test_add_csv_asset_to_datasource(
    spark_filesystem_datasource: SparkFilesystemDatasource,
):
    asset = spark_filesystem_datasource.add_csv_asset(
        name="csv_asset",
    )
    assert asset.name == "csv_asset"
    m1 = asset.batching_regex.match("this_can_be_named_anything.csv")
    assert m1 is not None


@pytest.mark.unit
def test_add_csv_asset_with_batching_regex_to_datasource(
    spark_filesystem_datasource: SparkFilesystemDatasource,
):
    asset = spark_filesystem_datasource.add_csv_asset(
        name="csv_asset",
        batching_regex=r"yellow_tripdata_sample_(\d{4})-(\d{2})\.csv",
        header=True,
        infer_schema=True,
    )
    assert asset.name == "csv_asset"
    assert asset.batching_regex.match("random string") is None
    assert asset.batching_regex.match("yellow_tripdata_sample_11D1-22.csv") is None
    m1 = asset.batching_regex.match("yellow_tripdata_sample_1111-22.csv")
    assert m1 is not None


@pytest.mark.unit
def test_construct_csv_asset_directly():
    # noinspection PyTypeChecker
    asset = CSVSparkAsset(
        name="csv_asset",
        batching_regex=r"yellow_tripdata_sample_(\d{4})-(\d{2})\.csv",  # Ignoring IDE warning (type declarations are consistent).
    )
    assert asset.name == "csv_asset"
    assert asset.batching_regex.match("random string") is None
    assert asset.batching_regex.match("yellow_tripdata_sample_11D1-22.csv") is None
    m1 = asset.batching_regex.match("yellow_tripdata_sample_1111-22.csv")
    assert m1 is not None


@pytest.mark.unit
def test_csv_asset_with_batching_regex_unnamed_parameters(
    spark_filesystem_datasource: SparkFilesystemDatasource,
):
    asset = spark_filesystem_datasource.add_csv_asset(
        name="csv_asset",
        batching_regex=r"yellow_tripdata_sample_(\d{4})-(\d{2})\.csv",
        header=True,
        infer_schema=True,
    )
    options = asset.batch_request_options_template()
    assert options == {
        "batch_request_param_1": None,
        "batch_request_param_2": None,
        "path": None,
    }


@pytest.mark.unit
def test_csv_asset_with_batching_regex_named_parameters(
    spark_filesystem_datasource: SparkFilesystemDatasource,
):
    asset = spark_filesystem_datasource.add_csv_asset(
        name="csv_asset",
        batching_regex=r"yellow_tripdata_sample_(?P<year>\d{4})-(?P<month>\d{2})\.csv",
        header=True,
        infer_schema=True,
    )
    options = asset.batch_request_options_template()
    assert options == {"year": None, "month": None, "path": None}


@pytest.mark.unit
def test_csv_asset_with_some_batching_regex_named_parameters(
    spark_filesystem_datasource: SparkFilesystemDatasource,
):
    asset = spark_filesystem_datasource.add_csv_asset(
        name="csv_asset",
        batching_regex=r"yellow_tripdata_sample_(\d{4})-(?P<month>\d{2})\.csv",
        header=True,
        infer_schema=True,
    )
    options = asset.batch_request_options_template()
    assert options == {"batch_request_param_1": None, "month": None, "path": None}


@pytest.mark.unit
def test_csv_asset_with_non_string_batching_regex_named_parameters(
    spark_filesystem_datasource: SparkFilesystemDatasource,
):
    asset = spark_filesystem_datasource.add_csv_asset(
        name="csv_asset",
        batching_regex=r"yellow_tripdata_sample_(\d{4})-(?P<month>\d{2})\.csv",
        header=True,
        infer_schema=True,
    )
    with pytest.raises(ge_exceptions.InvalidBatchRequestError):
        # year is an int which will raise an error
        asset.build_batch_request({"year": 2018, "month": "04"})


@pytest.mark.unit
def test_get_batch_list_from_fully_specified_batch_request(
    spark_filesystem_datasource: SparkFilesystemDatasource,
):
    asset = spark_filesystem_datasource.add_csv_asset(
        name="csv_asset",
        batching_regex=r"yellow_tripdata_sample_(?P<year>\d{4})-(?P<month>\d{2})\.csv",
        header=True,
        infer_schema=True,
    )
    path = "yellow_tripdata_sample_2018-04.csv"
    request = asset.build_batch_request({"year": "2018", "month": "04", "path": path})
    batches = asset.get_batch_list_from_batch_request(request)
    assert len(batches) == 1
    batch = batches[0]
    assert batch.batch_request.datasource_name == spark_filesystem_datasource.name
    assert batch.batch_request.data_asset_name == asset.name
    assert batch.batch_request.options == {
        "year": "2018",
        "month": "04",
        "path": pathlib.Path(path),
    }
    assert batch.metadata == {
        "year": "2018",
        "month": "04",
        "base_directory": spark_filesystem_datasource.base_directory,
        "path": pathlib.Path(path),
    }
    assert batch.id == "spark_filesystem_datasource-csv_asset-year_2018-month_04"


@pytest.mark.unit
def test_get_batch_list_from_partially_specified_batch_request(
    spark_filesystem_datasource: SparkFilesystemDatasource,
):
    # Verify test directory has files that don't match what we will query for
    file_name: PathStr
    all_files: List[str] = [
        file_name.stem
        for file_name in list(
            pathlib.Path(spark_filesystem_datasource.base_directory).iterdir()
        )
    ]
    # assert there are files that are not csv files
    assert any([not file_name.endswith("csv") for file_name in all_files])
    # assert there are 12 files from 2018
    files_for_2018 = [
        file_name for file_name in all_files if file_name.find("2018") >= 0
    ]
    assert len(files_for_2018) == 12

    asset = spark_filesystem_datasource.add_csv_asset(
        name="csv_asset",
        batching_regex=r"yellow_tripdata_sample_(?P<year>\d{4})-(?P<month>\d{2})\.csv",
        header=True,
        infer_schema=True,
    )
    request = asset.build_batch_request({"year": "2018"})
    batches = asset.get_batch_list_from_batch_request(request)
    assert (len(batches)) == 12
    batch_filenames = [batch.metadata["path"].stem for batch in batches]
    assert set(files_for_2018) == set(batch_filenames)

    @dataclass(frozen=True)
    class YearMonth:
        year: str
        month: str

    expected_year_month = {
        YearMonth(year="2018", month=format(m, "02d")) for m in range(1, 13)
    }
    batch_year_month = {
        YearMonth(year=batch.metadata["year"], month=batch.metadata["month"])
        for batch in batches
    }
    assert expected_year_month == batch_year_month


@pytest.mark.unit
@pytest.mark.parametrize(
    "order_by",
    [
        ["+year", "month"],
        ["+year", "+month"],
        ["+year", "-month"],
        ["year", "month"],
        ["year", "+month"],
        ["year", "-month"],
        ["-year", "month"],
        ["-year", "+month"],
        ["-year", "-month"],
        ["month", "+year"],
        ["+month", "+year"],
        ["-month", "+year"],
        ["month", "year"],
        ["+month", "year"],
        ["-month", "year"],
        ["month", "-year"],
        ["+month", "-year"],
        ["-month", "-year"],
    ],
)
def test_spark_sorter(
    spark_filesystem_datasource: SparkFilesystemDatasource,
    order_by: BatchSortersDefinition,
):
    # Verify test directory has files we expect
    years = ["2018", "2019", "2020"]
    months = [format(m, "02d") for m in range(1, 13)]
    file_name: PathStr
    all_files: List[str] = [
        file_name.stem
        for file_name in list(
            pathlib.Path(spark_filesystem_datasource.base_directory).iterdir()
        )
    ]
    # assert there are 12 files for each year
    for year in years:
        files_for_year = [
            file_name
            for file_name in all_files
            if file_name.find(f"yellow_tripdata_sample_{year}") == 0
        ]
        assert len(files_for_year) == 12

    asset = spark_filesystem_datasource.add_csv_asset(
        name="csv_asset",
        batching_regex=r"yellow_tripdata_sample_(?P<year>\d{4})-(?P<month>\d{2})\.csv",
        order_by=order_by,
    )
    batches = asset.get_batch_list_from_batch_request(asset.build_batch_request())
    assert (len(batches)) == 36

    @dataclass(frozen=True)
    class TimeRange:
        key: str
        range: List[str]

    ordered_years = reversed(years) if "-year" in order_by else years
    ordered_months = reversed(months) if "-month" in order_by else months
    if "year" in order_by[0]:
        ordered = [
            TimeRange(key="year", range=ordered_years),
            TimeRange(key="month", range=ordered_months),
        ]
    else:
        ordered = [
            TimeRange(key="month", range=ordered_months),
            TimeRange(key="year", range=ordered_years),
        ]

    batch_index = -1
    for range1 in ordered[0].range:
        key1 = ordered[0].key
        for range2 in ordered[1].range:
            key2 = ordered[1].key
            batch_index += 1
            metadata = batches[batch_index].metadata
            assert metadata[key1] == range1
            assert metadata[key2] == range2


def bad_batching_regex_config(
    csv_path: pathlib.Path,
) -> tuple[re.Pattern, TestConnectionError]:
    batching_regex = re.compile(
        r"green_tripdata_sample_(?P<year>\d{4})-(?P<month>\d{2})\.csv"
    )
    test_connection_error = TestConnectionError(
        f"""No file at base_directory path "{csv_path.resolve()}" matched regular expressions pattern "{batching_regex.pattern}" and/or glob_directive "**/*" for DataAsset "csv_spark_asset"."""
    )
    return batching_regex, test_connection_error


@pytest.fixture(params=[bad_batching_regex_config])
def datasource_test_connection_error_messages(
    csv_path: pathlib.Path,
    spark_filesystem_datasource: SparkFilesystemDatasource,
    request,
) -> tuple[SparkFilesystemDatasource, TestConnectionError]:
    batching_regex, test_connection_error = request.param(csv_path=csv_path)
    csv_spark_asset = CSVSparkAsset(
        name="csv_spark_asset",
        batching_regex=batching_regex,
    )
    csv_spark_asset._datasource = spark_filesystem_datasource
    spark_filesystem_datasource.assets = {"csv_spark_asset": csv_spark_asset}
    return spark_filesystem_datasource, test_connection_error


@pytest.mark.unit
def test_test_connection_failures(
    datasource_test_connection_error_messages: tuple[
        SparkFilesystemDatasource, TestConnectionError
    ]
):
    (
        spark_filesystem_datasource,
        test_connection_error,
    ) = datasource_test_connection_error_messages

    with pytest.raises(type(test_connection_error)) as e:
        spark_filesystem_datasource.test_connection()

    assert str(e.value) == str(test_connection_error)
