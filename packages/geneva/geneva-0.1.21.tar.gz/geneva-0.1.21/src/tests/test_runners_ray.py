# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

import itertools
import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any, NamedTuple, cast

import lance
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import pytest
from lance.blob import BlobFile

import geneva
from geneva import LanceCheckpointStore, connect, udf
from geneva.apply.multiprocess import MultiProcessBatchApplier
from geneva.apply.simple import SimpleApplier
from geneva.packager import DockerUDFPackager
from geneva.table import TableReference
from geneva.transformer import UDF

_LOG = logging.getLogger(__name__)
_LOG.setLevel(logging.DEBUG)

SIZE = 5  # was 256

try:
    import ray

    from geneva.runners.ray.pipeline import (
        _simulate_write_failure,
        run_ray_add_column,
        run_ray_copy_table,
    )
except ImportError:
    import pytest

    pytest.skip("failed to import geneva.runners.ray", allow_module_level=True)


def make_new_ds(tbl_path: Path, fn) -> None:
    # create initial dataset with only column 'a'
    data = {"a": pa.array(range(SIZE))}
    tbl = pa.Table.from_pydict(data)
    ds = lance.write_dataset(tbl, tbl_path, max_rows_per_file=32)

    # then add column 'b' using merge.  This is a separate commit from data
    # commits to keep column 'a' as a separate set of physical files from 'b'
    # which enables a separate commit from distributed execution to only
    # update 'b' with an efficient file replacement operation.
    new_frags = []
    new_schema = None
    for frag in ds.get_fragments():
        new_fragment, new_schema = frag.merge_columns(fn, columns=["a"])
        new_frags.append(new_fragment)

    assert new_schema is not None
    merge = lance.LanceOperation.Merge(new_frags, new_schema)
    lance.LanceDataset.commit(tbl_path, merge, read_version=ds.version)


class UDFTestConfig(NamedTuple):
    udf_fn: UDF
    recordbatch_schema_fn: Callable[[pa.RecordBatch], pa.RecordBatch]
    expected_recordbatch: dict[Any, Any]


def add_one_return_none(batch: pa.RecordBatch) -> pa.RecordBatch:
    return pa.RecordBatch.from_pydict(
        {"b": pa.array([None] * batch.num_rows, pa.int32())}
    )


# 0.1 cpu so we don't wait for provisioning in the tests
@udf(data_type=pa.int32(), batch_size=8, num_cpus=1)
def add_one(a) -> int:
    return a + 1


add_one_udftest = UDFTestConfig(
    add_one,
    add_one_return_none,
    {
        "a": list(range(SIZE)),
        "b": [x + 1 for x in range(SIZE)],
    },
)


def verify_run_ray_add_udf_column(
    tmp_path: Path,
    shuffle_config,
    udf: UDFTestConfig,
    batch_applier=None,
    where=None,
) -> None:
    tbl_path = tmp_path / "foo.lance"
    make_new_ds(tbl_path, udf.recordbatch_schema_fn)
    tbl_ref = TableReference(db_uri=str(tmp_path), table_name="foo", version=None)

    ckp_store = LanceCheckpointStore(str(tmp_path / "ckp"))
    run_ray_add_column(
        tbl_ref,
        ["a"],
        {"b": udf.udf_fn},
        checkpoint_store=ckp_store,
        batch_applier=batch_applier,
        where=where,
        **shuffle_config,
    )

    ds = lance.dataset(tbl_path)
    _LOG.info(
        f"ds.to_table().to_pydict()={ds.to_table().to_pydict()} "
        f"expected_recordbatch={udf.expected_recordbatch}"
    )
    _LOG.info(f"checkpoint store dump: {ckp_store.root}")
    ckp_keys = list(ckp_store.list_keys())
    for key in ckp_keys:
        try:
            _LOG.info(f"  {key}: {ckp_store[key].to_pydict()}")
        except Exception:  # noqa: PERF203
            _LOG.warning(f"  {key}: ")

    assert ds.to_table().to_pydict() == udf.expected_recordbatch


@pytest.mark.parametrize(
    ("shuffle_config", "batch_applier"),
    [
        (
            {
                "batch_size": batch_size,
                "shuffle_buffer_size": shuffle_buffer_size,
                "task_shuffle_diversity": task_shuffle_diversity,
            },
            batch_applier,
        )
        for (
            batch_size,
            shuffle_buffer_size,
            task_shuffle_diversity,
            batch_applier,
        ) in itertools.product(
            [4, 16],
            [7],
            [3],
            [SimpleApplier(), MultiProcessBatchApplier(num_processes=4)],
        )
    ],
)
def test_run_ray_add_column(tmp_path: Path, shuffle_config, batch_applier) -> None:
    verify_run_ray_add_udf_column(
        tmp_path, shuffle_config, add_one_udftest, batch_applier
    )


@pytest.mark.parametrize("batch_applier", [SimpleApplier()])
def test_run_ray_add_column_write_fault(tmp_path: Path, batch_applier) -> None:  # noqa: PT019
    tbl_path = tmp_path / "foo.lance"
    make_new_ds(tbl_path, add_one_return_none)
    tbl_ref = TableReference(db_uri=str(tmp_path), table_name="foo", version=None)

    ckp_store = LanceCheckpointStore(str(tmp_path / "ckp"))

    with _simulate_write_failure(True):
        run_ray_add_column(
            tbl_ref,
            ["a"],
            {"b": add_one},
            checkpoint_store=ckp_store,
            batch_applier=batch_applier,
        )

    ds = lance.dataset(tbl_path)
    assert ds.to_table().to_pydict() == {
        "a": list(range(SIZE)),
        "b": [x + 1 for x in range(SIZE)],
    }


def test_run_ray_add_column_with_deletes(tmp_path: Path) -> None:  # noqa: PT019
    tbl_path = tmp_path / "foo.lance"
    make_new_ds(tbl_path, add_one_return_none)
    tbl_ref = TableReference(db_uri=str(tmp_path), table_name="foo", version=None)

    ds = lance.dataset(tbl_path)
    ds.delete("a % 2 == 1")

    ckp_store = LanceCheckpointStore(str(tmp_path / "ckp"))

    run_ray_add_column(tbl_ref, ["a"], {"b": add_one}, checkpoint_store=ckp_store)

    ds = lance.dataset(tbl_path)
    assert ds.to_table().to_pydict() == {
        "a": list(range(0, SIZE, 2)),
        "b": [x + 1 for x in range(0, SIZE, 2)],
    }


struct_type = pa.struct([("rpad", pa.string()), ("lpad", pa.string())])


def struct_udf_return_none(batch: pa.RecordBatch) -> pa.RecordBatch:
    return pa.RecordBatch.from_pydict(
        {"b": pa.array([None] * batch.num_rows, struct_type)}
    )


@udf(data_type=struct_type, batch_size=8, num_cpus=0.1)
def struct_udf(a: int) -> dict:  # is the output type correct?
    return {"lpad": f"{a:04d}", "rpad": f"{a}0000"[:4]}


@udf(data_type=struct_type, batch_size=8, num_cpus=0.1)
def struct_udf_batch(a: pa.Array) -> pa.Array:  # is the output type correct?
    rpad = pc.ascii_rpad(pc.cast(a, target_type="string"), 4, padding="0")
    lpad = pc.ascii_lpad(pc.cast(a, target_type="string"), 4, padding="0")
    return pc.make_struct(rpad, lpad, field_names=["rpad", "lpad"])


ret_struct_udftest = UDFTestConfig(
    struct_udf,
    struct_udf_return_none,
    {
        "a": list(range(SIZE)),
        "b": [{"lpad": f"{x:04d}", "rpad": f"{x}0000"[:4]} for x in range(SIZE)],
    },
)

default_shuffle_config = {
    "batch_size": 1,
    "shuffle_buffer_size": 3,
    "task_shuffle_diversity": None,
}


def test_run_ray_add_column_ret_struct(tmp_path: Path) -> None:
    verify_run_ray_add_udf_column(tmp_path, default_shuffle_config, ret_struct_udftest)


ret_struct_udftest_filtered = UDFTestConfig(
    struct_udf,
    struct_udf_return_none,
    {
        "a": list(range(SIZE)),
        "b": [
            {"lpad": f"{x:04d}", "rpad": f"{x}0000"[:4]}
            if x % 2 == 0
            else {"lpad": "", "rpad": ""}
            for x in range(SIZE)
        ],
    },
)


@pytest.mark.timeout(30)  # seconds
def test_run_ray_add_column_ret_struct_filtered(tmp_path: Path) -> None:
    verify_run_ray_add_udf_column(
        tmp_path, default_shuffle_config, ret_struct_udftest_filtered, where="a % 2 = 0"
    )


vararray_type = pa.list_(pa.int64())


def vararray_udf_return_none(batch: pa.RecordBatch) -> pa.RecordBatch:
    return pa.RecordBatch.from_pydict(
        {"b": pa.array([[]] * batch.num_rows, vararray_type)}
    )


@udf(data_type=vararray_type, batch_size=8, num_cpus=0.1)
def vararray_udf(a: pa.Array) -> pa.Array:  # is the output type correct?
    # [ [], [1], [2,2], [3,3,3] ... ]
    arr = [[val] * val for val in a.to_pylist()]
    b = pa.array(arr, type=pa.list_(pa.int64()))
    return b


ret_vararray_udftest = UDFTestConfig(
    vararray_udf,
    vararray_udf_return_none,
    {
        "a": list(range(SIZE)),
        "b": [[x] * x for x in range(SIZE)],
    },
)


def test_run_ray_add_column_ret_vararray(tmp_path: Path) -> None:
    verify_run_ray_add_udf_column(
        tmp_path, default_shuffle_config, ret_vararray_udftest
    )


@udf(data_type=vararray_type, batch_size=8, num_cpus=0.1)
class StatefulVararrayUDF(Callable):
    def __init__(self) -> None:
        self.state = 0

    def __call__(self, a: pa.Array) -> pa.Array:  # is the output type correct?
        # [ [], [1], [2,2], [3,3,3] ... ]
        arr = [[val] * val for val in a.to_pylist()]
        b = pa.array(arr, type=pa.list_(pa.int64()))
        return b


ret_vararray_stateful_udftest = UDFTestConfig(
    StatefulVararrayUDF,
    vararray_udf_return_none,
    {
        "a": list(range(SIZE)),
        "b": [[x] * x for x in range(SIZE)],
    },
)


def test_run_ray_add_column_ret_vararray_stateful(tmp_path: Path) -> None:
    verify_run_ray_add_udf_column(
        tmp_path, default_shuffle_config, ret_vararray_stateful_udftest
    )


nested_type = pa.struct([("lpad", pa.string()), ("array", pa.list_(pa.int64()))])


def nested_udf_return_none(batch: pa.RecordBatch) -> pa.RecordBatch:
    return pa.RecordBatch.from_pydict(
        {"b": pa.array([{"lpad": "", "array": []}] * batch.num_rows, nested_type)}
    )


@udf(data_type=nested_type, batch_size=8, num_cpus=0.1)
def nested_udf(a: pa.Array) -> pa.Array:
    # [ { lpad:"0000", array:[] } , {lpad:"0001", array:[1]},
    #   { lpad:"0002", array:[2,2]}, ... ]

    lpad = pc.ascii_lpad(pc.cast(a, target_type="string"), 4, padding="0")
    arr = [[val] * val for val in a.to_pylist()]
    array = pa.array(arr, type=pa.list_(pa.int64()))

    return pc.make_struct(lpad, array, field_names=["lpad", "array"])


ret_nested_udftest = UDFTestConfig(
    nested_udf,
    nested_udf_return_none,
    {
        "a": list(range(SIZE)),
        "b": [{"lpad": f"{val:04d}", "array": [val] * val} for val in range(SIZE)],
    },
)


def test_run_ray_add_column_ret_nested(tmp_path: Path) -> None:
    verify_run_ray_add_udf_column(tmp_path, default_shuffle_config, ret_nested_udftest)


@pytest.mark.skip(reason="do we need to support relative paths?")
def test_relative_path(tmp_path: Path, monkeypatch) -> None:
    # Make sure this ray instance uses the tmp_path as CURDIR
    ray.shutdown()
    monkeypatch.chdir(tmp_path)

    packager = DockerUDFPackager(
        # use prebuilt image tag so we don't have to build the image
        prebuilt_docker_img="test-image:latest"
    )
    db = geneva.connect("./db", packager=packager)

    # create a basic table
    tbl = pa.Table.from_pydict({"id": [1, 2, 3, 4, 5, 6]})
    table = db.create_table("table1", tbl)

    @udf(data_type=pa.int64())
    def double_id(id: int):  # noqa A002
        return id * 2

    table.add_columns(
        {"id2": double_id},
    )

    schema = table.schema
    field = schema.field("id2")
    assert field.metadata[b"virtual_column.udf_name"] == b"double_id"

    # At this time, "id2" is a null column
    assert table.to_arrow().combine_chunks() == pa.Table.from_pydict(
        {"id": [1, 2, 3, 4, 5, 6], "id2": [None] * 6},
        schema=pa.schema(
            [
                pa.field("id", pa.int64()),
                pa.field("id2", pa.int64(), True),
            ]
        ),
    )

    # uses local ray to execute UDF and populate "id2"
    table.backfill("id2")

    df = table.to_arrow().to_pandas()
    assert df.equals(
        pd.DataFrame({"id": [1, 2, 3, 4, 5, 6], "id2": [2, 4, 6, 8, 10, 12]})
    )


def test_ray_materialized_view(tmp_path: Path) -> None:
    packager = DockerUDFPackager(prebuilt_docker_img="test-image:latest")
    db = connect(tmp_path, packager=packager)
    tbl = pa.Table.from_pydict({"video_uri": ["a", "b", "c", "d", "e", "f"]})
    table = db.create_table("table", tbl)

    @udf(data_type=pa.binary())
    def load_video(video_uri: pa.Array) -> pa.Array:
        videos = [str(i).encode("utf-8") for i in video_uri]
        return cast("pa.Array", pa.array(videos))

    load_video = cast("UDF", load_video)

    view_table = (
        table.search(None)
        .shuffle(seed=42)
        .select(
            {
                "video_uri": "video_uri",
                "video": load_video,
            }
        )
        .create_materialized_view(db, "table_view")
    )

    ckp_store = LanceCheckpointStore(str(tmp_path / "ckp"))

    run_ray_copy_table(view_table.get_reference(), packager, ckp_store)

    view_table.checkout_latest()
    assert view_table.to_arrow() == pa.Table.from_pydict(
        {
            "__source_row_id": [3, 2, 5, 4, 1, 0],
            "__is_set": [False] * 6,
            "video_uri": ["d", "c", "f", "e", "b", "a"],
            "video": [b"d", b"c", b"f", b"e", b"b", b"a"],
        }
    )


def test_udf_with_blob_column(tmp_path: Path) -> None:
    db = connect(tmp_path)
    schema = pa.schema(
        [pa.field("blobs", pa.large_binary(), metadata={"lance-encoding:blob": "true"})]
    )
    tbl = pa.Table.from_pydict({"blobs": [b"hello", b"the world"]}, schema=schema)
    tbl = db.create_table("t", tbl)

    @udf
    def work_on_udf(blob: BlobFile) -> int:
        assert isinstance(blob, BlobFile)
        return len(blob.read())

    tbl.add_columns({"len": work_on_udf})
    tbl.backfill("len", input_columns=["blobs"])

    t2 = db.open_table("t")
    tbl = t2.to_arrow()
    assert tbl["len"].to_pylist() == [5, 9]
