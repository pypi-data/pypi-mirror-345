from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from polars_cloud.exceptions import ComputeClusterMisspecified

if TYPE_CHECKING:
    import sys

    from polars_cloud import Workspace

    if sys.version_info >= (3, 11):
        pass
    else:
        pass


@dataclass
class ComputeContextSpecs:
    cpus: int | None = None
    memory: int | None = None
    instance_type: str | None = None
    storage: int | None = None
    cluster_size: int = 1


def resolve_compute_context_specs(
    workspace: Workspace,
    cpus: int | None = None,
    memory: int | None = None,
    instance_type: str | None = None,
    storage: int | None = None,
    cluster_size: int | None = None,
) -> ComputeContextSpecs:
    """Resolve all the compute context settings.

    Resolve all compute instance specs either they are fully specified or
    we need to get the defaults for the workspace.
    """
    if instance_type is not None and (cpus is not None or memory is not None):
        msg = "cannot specify both `instance_type` AND (`memory` or `cpus`)"
        raise ComputeClusterMisspecified(msg)

    if memory is not None and cpus is None:
        msg = "`cpus` is required when specifying `memory` in `ComputeContext`"
        raise ComputeClusterMisspecified(msg)

    if memory is None and cpus is not None:
        msg = "`memory` is required when specifying `cpus` in `ComputeContext`"
        raise ComputeClusterMisspecified(msg)

    if memory is None and cpus is None and instance_type is None:
        defaults = workspace.defaults
        if defaults is None:
            msg = (
                "Compute specification (memory & cpus or instance_type) not provided and no defaults available"
                "\n\nHint: Either pass them or set defaults for the workspace."
            )
            raise ComputeClusterMisspecified(msg)
        else:
            memory = defaults.memory
            cpus = defaults.cpus
            instance_type = defaults.instance_type

    storage_resolved = storage or getattr(workspace.defaults, "storage", None)
    cluster_size_resolved: int = cluster_size or getattr(
        workspace.defaults, "cluster_size", 1
    )  # type: ignore[assignment]

    specs = ComputeContextSpecs(
        cpus=cpus,
        memory=memory,
        instance_type=instance_type,
        storage=storage_resolved,
        cluster_size=cluster_size_resolved,
    )

    return specs
