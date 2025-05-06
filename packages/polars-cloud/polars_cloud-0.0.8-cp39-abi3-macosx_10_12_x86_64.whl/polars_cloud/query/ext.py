from __future__ import annotations

import copy
from typing import TYPE_CHECKING, Any

from polars import LazyFrame

from polars_cloud.query.broadcast import Broadcast
from polars_cloud.query.dst import CsvDst, IpcDst, ParquetDst, TmpDst
from polars_cloud.query.query import spawn

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Literal

    from polars import DataFrame
    from polars._typing import (
        CsvQuoteStyle,
        IpcCompression,
        ParquetCompression,
    )
    from polars.interchange import CompatLevel
    from polars.io.cloud import CredentialProviderFunction

    from polars_cloud._typing import Engine, PlanTypePreference, ShuffleCompression
    from polars_cloud.context import ComputeContext
    from polars_cloud.query.query import BatchQuery, InteractiveQuery


class LazyFrameExt:
    def __init__(
        self,
        lf: LazyFrame,
        context: ComputeContext | None = None,
        plan_type: PlanTypePreference = "dot",
        n_retries: int = 0,
        engine: Engine = "auto",
    ) -> None:
        self.lf: LazyFrame = lf
        self.context: ComputeContext | None = context
        self._partition_by: None | str | list[str] = None
        self._broadcast_over: None | list[list[list[Path]]] = None
        self._distributed: None | bool = None
        self._engine: Engine = engine
        self._shuffle_compression: ShuffleCompression = "auto"
        self._labels: None | list[str] = None
        self._n_retries = n_retries
        self.plan_type: PlanTypePreference = plan_type

    def __check_partition_by_broadcast_over(self) -> None:
        if self._broadcast_over is not None and self._partition_by is not None:
            msg = "only 1 of 'partition_by' or 'broadcast_over' can be set"
            raise ValueError(msg)

    def distributed(
        self, *, shuffle_compression: ShuffleCompression = "auto"
    ) -> LazyFrameExt:
        """Whether the query should run in a distributed fashion.

        Parameters
        ----------
        shuffle_compression : {'auto', 'lz4', 'zstd', 'uncompressed'}
            Compress files before shuffling them. Compression reduces disk and network
            IO, but disables memory mapping.
            Choose "zstd" for good compression performance.
            Choose "lz4" for fast compression/decompression.
            Choose "uncompressed" for memory mapped access at the expense of file size.

        """
        self._distributed = True
        self._shuffle_compression = shuffle_compression
        return self

    def labels(self, labels: list[str] | str) -> LazyFrameExt:
        """Add labels to the query.

        Parameters
        ----------
        labels
            Labels to add to the query (will be implicitly created)
        """
        self._labels = [labels] if isinstance(labels, str) else labels
        return self

    def partition_by(
        self, key: str | list[str], *, shuffle_compression: ShuffleCompression = "auto"
    ) -> LazyFrameExt:
        """Partition this query by the given key.

        This first partitions the data by the key and then runs this query
        per unique key. This will lead to ``N`` output results, where ``N``
        is equal to the number of unique values in ``key``

        This will run on multiple workers.

        Parameters
        ----------
        key
            Key/keys to partition over.
        shuffle_compression : {'auto', 'lz4', 'zstd', 'uncompressed'}
            Compress files before shuffling them. Compression reduces disk and network
            IO, but disables memory mapping.
            Choose "zstd" for good compression performance.
            Choose "lz4" for fast compression/decompression.
            Choose "uncompressed" for memory mapped access at the expense of file size.

        """
        self._partition_by = key
        self.__check_partition_by_broadcast_over()
        self._shuffle_compression = shuffle_compression
        return self

    def broadcast_over(self, over: Broadcast | list[list[list[Path]]]) -> LazyFrameExt:
        """Run this queries in parallel over the given source paths.

        This will run on multiple workers.

        Parameters
        ----------
        over
            Run this queries in parallel over the given source paths.

            Levels from outer to inner:
            1 -> partition paths
            2 -> src in DSL
            3 -> paths (plural) in a single DSL source.

        """
        if isinstance(over, Broadcast):
            self._broadcast_over = over.finish()  # type: ignore[assignment]
        else:
            self._broadcast_over = over
        self.__check_partition_by_broadcast_over()
        return self

    def execute(self) -> InteractiveQuery | BatchQuery:
        """Start executing the query and store a temporary result.

        This is useful for interactive workloads.

        """
        return spawn(
            lf=self.lf,
            dst=TmpDst(),
            context=self.context,
            partitioned_by=self._partition_by,
            broadcast_over=self._broadcast_over,
            engine=self._engine,
            plan_type=self.plan_type,
            distributed=self._distributed,
            labels=self._labels,
            shuffle_compression=self._shuffle_compression,
            n_retries=self._n_retries,
        )

    def collect(self) -> LazyFrame:
        """Start executing the query and store a temporary result.

        Collect will immediately block this thread and wait for
        a successful result. It will immediately turn the result
        into a `LazyFrame`.

        This is syntactic sugar for:

        ``.execute().await_result().lazy()``

        """
        return self.execute().await_result().lazy()

    def show(self, n: int = 10) -> DataFrame:
        """Start executing the query return the first `n` rows.

        Show will immediately block this thread and wait for
        a successful result. It will immediately turn the result
        into a `DataFrame`.

        Parameters
        ----------
        n
            Number of rows to return

        Examples
        --------
        >>> pl.scan_parquet("s3://..").select(
        ...     pl.len()
        ... ).remote().show()  # doctest: +SKIP
        shape: (1, 1)
        ┌───────┐
        │ count │
        │ ---   │
        │ u32   │
        ╞═══════╡
        │ 1000  │
        └───────┘

        """
        this = copy.copy(self)
        this.lf = this.lf.limit(n)
        return this.collect().collect()

    def sink_parquet(
        self,
        uri: str,
        *,
        compression: ParquetCompression = "zstd",
        compression_level: int | None = None,
        statistics: bool | str | dict[str, bool] = True,
        row_group_size: int | None = None,
        data_page_size: int | None = None,
        storage_options: dict[str, Any] | None = None,
        credential_provider: CredentialProviderFunction
        | Literal["auto"]
        | None = "auto",
    ) -> InteractiveQuery | BatchQuery:
        """Start executing the query and write the result to parquet.

        Parameters
        ----------
        uri
            Path to which the output should be written.
            Must be a URI to an accessible object store location.

            It is recommended to write to a directory path
            for example `"my-location/"`, instead of as single file
            as a single file can only be written from a single
            node.

            If set to `"local"`, the query is executed locally.
        compression : {'lz4', 'uncompressed', 'snappy', 'gzip', 'lzo', 'brotli', 'zstd'}
            Choose "zstd" for good compression performance.
            Choose "lz4" for fast compression/decompression.
            Choose "snappy" for more backwards compatibility guarantees
            when you deal with older parquet readers.
        compression_level
            The level of compression to use. Higher compression means smaller files on
            disk.

            - "gzip" : min-level: 0, max-level: 10.
            - "brotli" : min-level: 0, max-level: 11.
            - "zstd" : min-level: 1, max-level: 22.

        statistics
            Write statistics to the parquet headers. This is the default behavior.

            Possible values:

            - `True`: enable default set of statistics (default). Some
              statistics may be disabled.
            - `False`: disable all statistics
            - "full": calculate and write all available statistics. Cannot be
              combined with `use_pyarrow`.
            - `{ "statistic-key": True / False, ... }`. Cannot be combined with
              `use_pyarrow`. Available keys:

              - "min": column minimum value (default: `True`)
              - "max": column maximum value (default: `True`)
              - "distinct_count": number of unique column values (default: `False`)
              - "null_count": number of null values in column (default: `True`)
        row_group_size
            Size of the row groups in number of rows. Defaults to 512^2 rows.
        data_page_size
            Size of the data page in bytes. Defaults to 1024^2 bytes.
        storage_options
            Options that indicate how to connect to a cloud provider.

            The cloud providers currently supported are AWS, GCP, and Azure.
            See supported keys here:

            * `aws <https://docs.rs/object_store/latest/object_store/aws/enum.AmazonS3ConfigKey.html>`_
            * `gcp <https://docs.rs/object_store/latest/object_store/gcp/enum.GoogleConfigKey.html>`_
            * `azure <https://docs.rs/object_store/latest/object_store/azure/enum.AzureConfigKey.html>`_
            * Hugging Face (`hf://`): Accepts an API key under the `token` parameter: \
            `{'token': '...'}`, or by setting the `HF_TOKEN` environment variable.

            If `storage_options` is not provided, Polars will try to infer the
            information from environment variables.
        credential_provider
            Provide a function that can be called to provide cloud storage
            credentials. The function is expected to return a dictionary of
            credential keys along with an optional credential expiry time.

            .. warning::
                This functionality is considered **unstable**. It may be changed
                at any point without it being considered a breaking change.

        """
        dst = ParquetDst(
            uri=uri,
            compression=compression,
            compression_level=compression_level,
            statistics=statistics,
            row_group_size=row_group_size,
            data_page_size=data_page_size,
            storage_options=storage_options,
            credential_provider=credential_provider,
        )

        return spawn(
            lf=self.lf,
            dst=dst,
            context=self.context,
            partitioned_by=self._partition_by,
            broadcast_over=self._broadcast_over,
            engine=self._engine,
            plan_type=self.plan_type,
            distributed=self._distributed,
            labels=self._labels,
            shuffle_compression=self._shuffle_compression,
            n_retries=self._n_retries,
        )

    def sink_csv(
        self,
        uri: str,
        *,
        include_bom: bool = False,
        include_header: bool = True,
        separator: str = ",",
        line_terminator: str = "\n",
        quote_char: str = '"',
        batch_size: int = 1024,
        datetime_format: str | None = None,
        date_format: str | None = None,
        time_format: str | None = None,
        float_scientific: bool | None = None,
        float_precision: int | None = None,
        null_value: str | None = None,
        quote_style: CsvQuoteStyle | None = None,
        storage_options: dict[str, Any] | None = None,
        credential_provider: CredentialProviderFunction
        | Literal["auto"]
        | None = "auto",
    ) -> InteractiveQuery | BatchQuery:
        """Start executing the query and write the result to csv.

        Parameters
        ----------
        uri
            Path to which the output should be written.
            Must be a URI to an accessible object store location.

            It is recommended to write to a directory path
            for example `"my-location/"`, instead of as single file
            as a single file can only be written from a single
            node.

            If set to `"local"`, the query is executed locally.
        include_bom
            Whether to include UTF-8 BOM in the CSV output.
        include_header
            Whether to include header in the CSV output.
        separator
            Separate CSV fields with this symbol.
        line_terminator
            String used to end each row.
        quote_char
            Byte to use as quoting character.
        batch_size
            Number of rows that will be processed per thread.
        datetime_format
            A format string, with the specifiers defined by the
            `chrono <https://docs.rs/chrono/latest/chrono/format/strftime/index.html>`_
            Rust crate. If no format specified, the default fractional-second
            precision is inferred from the maximum timeunit found in the frame's
            Datetime cols (if any).
        date_format
            A format string, with the specifiers defined by the
            `chrono <https://docs.rs/chrono/latest/chrono/format/strftime/index.html>`_
            Rust crate.
        time_format
            A format string, with the specifiers defined by the
            `chrono <https://docs.rs/chrono/latest/chrono/format/strftime/index.html>`_
            Rust crate.
        float_scientific
            Whether to use scientific form always (true), never (false), or
            automatically (None) for `Float32` and `Float64` datatypes.
        float_precision
            Number of decimal places to write, applied to both `Float32` and
            `Float64` datatypes.
        null_value
            A string representing null values (defaulting to the empty string).
        quote_style : {'necessary', 'always', 'non_numeric', 'never'}
            Determines the quoting strategy used.

            - necessary (default): This puts quotes around fields only when necessary.
              They are necessary when fields contain a quote,
              delimiter or record terminator.
              Quotes are also necessary when writing an empty record
              (which is indistinguishable from a record with one empty field).
              This is the default.
            - always: This puts quotes around every field. Always.
            - never: This never puts quotes around fields, even if that results in
              invalid CSV data (e.g.: by not quoting strings containing the
              separator).
            - non_numeric: This puts quotes around all fields that are non-numeric.
              Namely, when writing a field that does not parse as a valid float
              or integer, then quotes will be used even if they aren`t strictly
              necessary.
        storage_options
            Options that indicate how to connect to a cloud provider.

            The cloud providers currently supported are AWS, GCP, and Azure.
            See supported keys here:

            * `aws <https://docs.rs/object_store/latest/object_store/aws/enum.AmazonS3ConfigKey.html>`_
            * `gcp <https://docs.rs/object_store/latest/object_store/gcp/enum.GoogleConfigKey.html>`_
            * `azure <https://docs.rs/object_store/latest/object_store/azure/enum.AzureConfigKey.html>`_
            * Hugging Face (`hf://`): Accepts an API key under the `token` parameter: \
            `{'token': '...'}`, or by setting the `HF_TOKEN` environment variable.

            If `storage_options` is not provided, Polars will try to infer the
            information from environment variables.
        credential_provider
            Provide a function that can be called to provide cloud storage
            credentials. The function is expected to return a dictionary of
            credential keys along with an optional credential expiry time.

            .. warning::
                This functionality is considered **unstable**. It may be changed
                at any point without it being considered a breaking change.
        """
        dst = CsvDst(
            uri,
            include_bom=include_bom,
            include_header=include_header,
            separator=separator,
            line_terminator=line_terminator,
            quote_char=quote_char,
            batch_size=batch_size,
            datetime_format=datetime_format,
            date_format=date_format,
            time_format=time_format,
            float_scientific=float_scientific,
            float_precision=float_precision,
            null_value=null_value,
            quote_style=quote_style,
            storage_options=storage_options,
            credential_provider=credential_provider,
        )
        return spawn(
            lf=self.lf,
            dst=dst,
            context=self.context,
            partitioned_by=self._partition_by,
            broadcast_over=self._broadcast_over,
            engine=self._engine,
            plan_type=self.plan_type,
            distributed=self._distributed,
            labels=self._labels,
            shuffle_compression=self._shuffle_compression,
            n_retries=self._n_retries,
        )

    def sink_ipc(
        self,
        uri: str,
        *,
        compression: IpcCompression | None = "zstd",
        compat_level: CompatLevel | None = None,
        storage_options: dict[str, Any] | None = None,
        credential_provider: CredentialProviderFunction
        | Literal["auto"]
        | None = "auto",
    ) -> InteractiveQuery | BatchQuery:
        """Start executing the query and write the result to ipc.

        Parameters
        ----------
        uri
            Path to which the output should be written.
            Must be a URI to an accessible object store location.

            It is recommended to write to a directory path
            for example `"my-location/"`, instead of as single file
            as a single file can only be written from a single
            node.

            If set to `"local"`, the query is executed locally.
        compression : {'uncompressed', 'lz4', 'zstd'}
            Choose "zstd" for good compression performance.
            Choose "lz4" for fast compression/decompression.
        compat_level
            Use a specific compatibility level
            when exporting Polars' internal data structures.
        storage_options
            Options that indicate how to connect to a cloud provider.

            The cloud providers currently supported are AWS, GCP, and Azure.
            See supported keys here:

            * `aws <https://docs.rs/object_store/latest/object_store/aws/enum.AmazonS3ConfigKey.html>`_
            * `gcp <https://docs.rs/object_store/latest/object_store/gcp/enum.GoogleConfigKey.html>`_
            * `azure <https://docs.rs/object_store/latest/object_store/azure/enum.AzureConfigKey.html>`_
            * Hugging Face (`hf://`): Accepts an API key under the `token` parameter: \
            `{'token': '...'}`, or by setting the `HF_TOKEN` environment variable.

            If `storage_options` is not provided, Polars will try to infer the
            information from environment variables.
        credential_provider
            Provide a function that can be called to provide cloud storage
            credentials. The function is expected to return a dictionary of
            credential keys along with an optional credential expiry time.

            .. warning::
                This functionality is considered **unstable**. It may be changed
                at any point without it being considered a breaking change.
        """
        dst = IpcDst(
            uri,
            compression=compression,
            compat_level=compat_level,
            storage_options=storage_options,
            credential_provider=credential_provider,
        )
        return spawn(
            lf=self.lf,
            dst=dst,
            context=self.context,
            partitioned_by=self._partition_by,
            broadcast_over=self._broadcast_over,
            engine=self._engine,
            plan_type=self.plan_type,
            distributed=self._distributed,
            labels=self._labels,
            shuffle_compression=self._shuffle_compression,
            n_retries=self._n_retries,
        )


def _lf_remote(
    lf: LazyFrame,
    context: ComputeContext | None = None,
    *,
    plan_type: PlanTypePreference = "dot",
    n_retries: int = 0,
    engine: Engine = "auto",
) -> LazyFrameExt:
    return LazyFrameExt(
        lf, context=context, plan_type=plan_type, n_retries=n_retries, engine=engine
    )


# Overwrite the remote method, so that we are sure we already expose
# the latest arguments.
LazyFrame.remote = _lf_remote  # type: ignore[method-assign, assignment]
