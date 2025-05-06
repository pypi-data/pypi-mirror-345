from __future__ import annotations

import json
import sys
from typing import TYPE_CHECKING, Callable

import polars as pl

# needed for eval
from polars.exceptions import (  # noqa: F401
    ColumnNotFoundError,
    ComputeError,
    DuplicateError,
    InvalidOperationError,
    NoDataError,
    PolarsError,
    SchemaError,
    SchemaFieldNotFoundError,
    ShapeError,
    SQLSyntaxError,
    StringCacheMismatchError,
    StructFieldNotFoundError,
)

from polars_cloud.query.query_status import QueryStatus

if TYPE_CHECKING:
    from pathlib import Path

    from polars import DataFrame, LazyFrame

    from polars_cloud._typing import FileType, PlanType
    from polars_cloud.query.query_info import QueryInfo


def format_result(
    finished_task_info: QueryInfo,
    repr_f: Callable[[pl.DataFrame], str],
) -> str:
    assert finished_task_info.head is not None
    return f"""
total_stages: {finished_task_info.total_stages}
finished_stages: {finished_task_info.finished_stages}
total_rows: {finished_task_info.n_rows_result}
location: {finished_task_info.sink_dst}
head:
{repr_f(finished_task_info.head)}
"""


class QueryResult:
    """The result of a Polars Cloud query."""

    def __init__(self, result: QueryInfo, status: QueryStatus):
        self.finished_task_info = result
        self.status = status

    @property
    def head(self) -> DataFrame | None:
        """The first n rows of the result."""
        return self.finished_task_info.head

    @property
    def n_rows_total(self) -> int | None:
        """Total rows that are outputted by the result."""
        return self.finished_task_info.n_rows_result

    @property
    def failed_stages(self) -> int:
        """Total failed stages."""
        return self.finished_task_info.failed_stages

    @property
    def finished_stages(self) -> int:
        """Total executed stages.

        This can be more than total stages, as failed stages can be rescheduled.
        """
        return self.finished_task_info.finished_stages

    @property
    def location(self) -> list[str] | None:
        """Location where the result is written."""
        return self.finished_task_info.sink_dst

    @property
    def file_type(self) -> FileType:
        """The file type where the result is written to."""
        return self.finished_task_info.sink_type

    def graph(
        self,
        *,
        show: bool = True,
        output_path: str | Path | None = None,
        raw_output: bool = False,
        figsize: tuple[float, float] = (16.0, 12.0),
    ) -> str | None:
        """Return the query plan as dot diagram.

        Parameters
        ----------
        show
            Show the figure.
        output_path
            Write the figure to disk.
        raw_output
            Return dot syntax. This cannot be combined with `show` and/or `output_path`.
        figsize
            Passed to matplotlib if `show == True`.
        """
        if self.finished_task_info.ir_plan_dot is None:
            msg = "no dot diagram created for this query.\n\nConsider setting 'plan_type' to 'dot'"
            raise NoDataError(msg)
        return pl._utils.various.display_dot_graph(
            dot=self.finished_task_info.ir_plan_dot,
            show=show,
            output_path=output_path,
            raw_output=raw_output,
            figsize=figsize,
        )

    def plan(
        self,
        plan_type: PlanType = "physical",
    ) -> str:
        """Return the executed plan in string format.

        Parameters
        ----------
        plan_type: {'physical', 'ir'}
            Plan visualization to return.

            * physical: The executed physical plan/stages.
            * ir: The optimized query plan before execution.

        """
        if plan_type == "physical":
            if self.finished_task_info.phys_plan_explain is None:
                return ""
            return self.finished_task_info.phys_plan_explain
        elif plan_type == "ir":
            if self.finished_task_info.ir_plan_explain is None:
                return ""

            return self.finished_task_info.ir_plan_explain
        else:
            msg = "expected either one of {'physical', 'ir'}"
            raise ValueError(msg)

    def lazy(self) -> LazyFrame:
        """Convert the `QueryResult` into a `LazyFrame`."""
        if self.status != QueryStatus.SUCCESS:
            msg = "a query must be successful to convert it to a 'LazyFrame'"
            raise InvalidOperationError(msg)

        file_type = self.file_type
        location = self.location

        if location is None or len(location) == 0:
            msg = "cannot create a 'LazyFrame', the result location is unknown"
            raise InvalidOperationError(msg)

        if file_type == "parquet":
            return pl.scan_parquet(location)
        elif file_type == "csv":
            return pl.scan_csv(location)
        elif file_type == "ipc":
            return pl.scan_ipc(location)
        elif file_type == "ndjson":
            return pl.scan_ndjson(location)
        elif file_type == "json":
            msg = "JSON not yet supported"
            raise InvalidOperationError(msg)
        else:
            msg = f"{file_type} not yet supported"
            raise InvalidOperationError(msg)

    def __repr__(self) -> str:
        if self.finished_task_info.head is not None:
            # If the query is successful, just show the (truncated) result
            with pl.Config(tbl_hide_dataframe_shape=True):
                return format_result(self.finished_task_info, repr)
        else:
            return f"""
            status: {self.status}
            {self.finished_task_info.__repr__()}"""

    def _repr_html_(self) -> str:
        """Format output data in HTML for display in Jupyter Notebooks."""
        if self.finished_task_info.head is not None:
            # If the query is successful, just show the (truncated) result
            with pl.Config(tbl_hide_dataframe_shape=True):
                return format_result(
                    self.finished_task_info, lambda df: df._repr_html_()
                )
        else:
            return repr(self)

    def raise_err(self) -> None:
        errors = {}  # type: ignore[var-annotated]
        assert self.finished_task_info.errors is not None

        # Deduplicate the errors, by converting to set.
        for err in set(self.finished_task_info.errors):
            # We expect {"worker/scheduler", "error: msg"}
            payload = json.loads(err)
            for key, value in payload.items():
                # Example data
                # key: "worker_id" or "scheduler"
                # value: ValueError: msg

                # Split off the error type e.g. 'ValueError'
                # from the message
                split = value.split(":", 1)
                # Evaluate the string to get the class of the error type
                try:
                    error_type = eval(split[0])
                    msg = split[1]

                    # Recreate the instance e.g. `ValueError(msg)`
                    error_value = error_type(msg)
                    assert isinstance(error_value, BaseException)
                # Fallback if we cannot restore the message
                except SyntaxError:
                    error_value = pl.exceptions.ComputeError(
                        f"spawn failed with: {value}"
                    )

                # Store the errors per worker/scheduler
                if key not in errors:
                    errors[key] = []
                errors[key].append(error_value)

        # Remove the scheduler
        scheduler_err = errors.pop("scheduler")[0]
        worker_errors = {}

        for worker, err_list in errors.items():
            worker_errors[worker] = err_list

        try:
            first_error = next(iter(worker_errors.values()))[0]
            msg = f"scheduler failed with:\n{scheduler_err}"
            exc = type(first_error)(msg)
            if sys.version_info >= (3, 11):
                exc.__cause__ = QueryError(
                    "Workers failed",
                    [error for errors in worker_errors.values() for error in errors],
                )
            else:
                msg = f"workers failed with: {errors}"
                exc.__cause__ = PolarsError(msg)
            raise exc

        except StopIteration:
            raise scheduler_err from None


if sys.version_info >= (3, 11):

    def is_ipython() -> bool:
        try:
            get_ipython()  # type: ignore[name-defined]
        except NameError:
            return False
        else:
            return True

    class QueryError(BaseExceptionGroup[PolarsError]):  # noqa: F821
        def __str__(self) -> str:
            if is_ipython() and not getattr(self, "_is_recursive", False):
                import traceback

                self._is_recursive = True
                return "\n".join(traceback.format_exception(self))
            return super().__str__()
