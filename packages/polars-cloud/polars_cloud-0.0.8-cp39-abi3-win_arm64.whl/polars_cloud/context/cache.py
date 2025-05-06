"""Contains global variable for caching the active compute context."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from polars_cloud.context.compute import ComputeContext

cached_context: ComputeContext | None = None


def set_compute_context(context: ComputeContext) -> None:
    """Set a compute context as the default during this session.

    Setting a compute context allows spawning queries without explicitly passing a
    compute context.

    See Also
    --------
    ComputeContext

    Examples
    --------
    >>> ctx = pc.ComputeContext(workspace="workspace-name", cpus=24, memory=24)
    >>> pc.set_compute_context(context=ctx)
    >>> query.remote().show()
    """
    global cached_context
    cached_context = context
