import typing
from datetime import datetime
from enum import Enum
from pathlib import Path
from uuid import UUID

from polars_cloud._typing import FileType

def get_auth_header() -> str: ...
def authenticate(interactive: bool = True) -> None:
    """Authenticate with Polars Cloud.

    This will attempt to authenticate with Polars Cloud or redirect to `login`
    if no valid token is found. If the `interactive` flag is set to false
    the function will fail if no valid token was found without redirecting to `login`.

    See Also
    --------
    login: Login will force a new interactive login without using cached tokens

    Examples
    --------
    >>> pc.authenticate()  # doctest: +SKIP

    Automatically logging in with service accounts::

        .. code-block:: bash

        export POLARS_CLOUD_CLIENT_ID="CLIENT_ID_HERE"
        export POLARS_CLOUD_CLIENT_SECRET="CLIENT_SECRET_HERE"

    """

def login() -> None:
    """Login interactively to Polars Cloud.

    This will open up a browser window where you can login
    and grant Polars Cloud the needed access rights.

    If you want to get machine access to Polars Cloud,
    you must set up service accounts.
    See: `Polars Cloud Service Accounts <https://docs.pola.rs/polars-cloud/run/service-accounts/>`.

    See Also
    --------
    authenticate: Authenticate with existing token

    Examples
    --------
    >>> pc.login()  # doctest: +SKIP

    """

def serialize_query_settings(
    *,
    dst: str | Path | None,
    max_threads: int | None,
    engine: str,
    partition_by: list[str] | None = ...,
    broadcast_over: list[list[list[Path]]] | None = ...,
    distributed: bool | None = ...,
    prefer_dot: bool = ...,
    shuffle_compression: str = ...,
    n_retries: int = ...,
) -> bytes: ...

class WorkspaceStateSchema(Enum):
    """Represents the state of a workspace."""

    Uninitialized: int
    Pending: int
    Active: int
    Failed: int
    Deleted: int

class WorkspaceSchema:
    """Represents a workspace schema."""

    id: UUID
    """Workspace ID (UUID v7)."""

    organization_id: UUID
    """Organization ID (UUID v7)."""

    name: str
    """Workspace Name."""

    description: str
    """Workspace Description."""

    owner_id: UUID
    """User who owns the Workspace."""

    status: WorkspaceStateSchema
    """Status of the Workspace."""

    created_at: datetime
    """Creation timestamp."""

    updated_at: datetime
    """Last update timestamp."""

    deleted_at: datetime | None
    """Timestamp of the last deletion."""

    def __init__(self, id: UUID, name: str, status: WorkspaceStateSchema) -> None: ...

class DefaultComputeSpecs:
    """Represents the default compute specifications."""

    instance_type: str | None
    """The type of instance (e.g., t3.micro)."""

    cpus: int | None
    """Number of CPUs."""

    ram_gb: int | None
    """Amount of RAM in GiB."""

    storage: int | None
    """Amount of disk storage in GiB."""

    cluster_size: int
    """Number of compute nodes."""

def list_workspaces(
    name: str | None = None, organization_id: UUID | None = None
) -> list[WorkspaceSchema]: ...
def get_workspace_details(workspace_id: UUID) -> WorkspaceSchema: ...
def get_workspace_default_compute_specs(workspace_id: UUID) -> DefaultComputeSpecs: ...
def set_workspace_cluster_defaults(
    workspace_id: UUID,
    cluster_size: int,
    cpus: int | None,
    memory: int | None,
    instance_type: str | None,
    storage: int | None,
) -> None: ...
def delete_workspace_cluster_defaults(workspace_id: UUID) -> None: ...

class QuerySchema:
    """Represents the schema for a query."""

    id: UUID
    """Query ID."""

    workspace_id: UUID
    """The workspace the query is being run in."""

    cluster_id: UUID
    """The virtual machine it is sent to."""

    user_id: UUID
    """The user account that started the instance."""

    request_time: datetime
    """The time the query was requested."""

    created_at: datetime
    """Creation timestamp."""

    updated_at: datetime
    """Last update timestamp."""

    deleted_at: datetime | None
    """Timestamp of the last deletion."""

class QueryStatusCodeSchema(Enum):
    """Represents the status codes for a query."""

    Queued: int
    Scheduled: int
    InProgress: int
    Success: int
    Failed: int
    Canceled: int

class TaskStatusType(Enum):
    Waiting: int
    InProgress: int
    Success: int
    Failed: int
    Canceled: int

class StatusSchema:
    """Represents the status information for a query."""

    status_time: datetime
    """Start time for the status."""

    code: QueryStatusCodeSchema
    """Status code."""

class QueryWithStatusSchema:
    """Represents a query with its associated status."""

    query: QuerySchema
    """Details of the query."""

    status: StatusSchema
    """Current status of the query"""

class QueryStateTimingSchema:
    final_known_state: QueryStatusCodeSchema | None
    """Last known state for this query"""
    final_status_time: datetime | None
    """Time for the final state for this query"""
    last_known_state: QueryStatusCodeSchema
    """The last known state that this query has"""
    last_known_status_time: datetime
    """Last known status time for this query, belongs to last_known_state"""
    last_progress_time: datetime | None
    """Time for the last InProgress time"""

class QueryWithStateTimingSchema:
    query: QuerySchema
    """Details of the query."""
    state_timing: QueryStateTimingSchema
    """Details about the state of the query"""

class FileTypeSchema(Enum):
    Parquet: int
    IPC: int
    Csv: int
    NDJSON: int
    JSON: int

class ResultSchema:
    total_stages: int
    finished_stages: int
    failed_stages: int
    n_rows_result: int | None
    file_type_sink: FileTypeSchema | None
    errors: list[str]
    ir_plan_explain: str | None
    ir_plan_dot: str | None
    phys_plan_explain: str | None

class QueryWithStateTimingAndResultSchema:
    query: QuerySchema
    """Details of the query."""
    state_timing: QueryStateTimingSchema
    """Details about the state of the query"""
    result: ResultSchema | None

def list_queries(workspace_id: UUID) -> list[QueryWithStateTimingSchema]: ...
def get_query(
    workspace_id: UUID, query_id: UUID
) -> QueryWithStateTimingAndResultSchema: ...

class TerminationReasonSchema(Enum):
    """Enum representing the reasons for termination."""

    StoppedByUser: int
    """The instance was stopped by the user."""

    StoppedInactive: int
    """The instance was stopped due to inactivity."""

    Failed: int
    """The instance failed."""

class TerminationSchema:
    """Represents the termination details of a compute instance."""

    termination_reason: TerminationReasonSchema
    """Reason for termination."""

    termination_time: datetime
    """Timestamp when termination occurred."""

    termination_message: str | None
    """Optional message providing details about the termination."""

class DBClusterModeSchema(Enum):
    Batch: int
    Interactive: int

class ComputeSchema:
    """Represents the schema for a compute instance."""

    id: UUID
    """Unique identifier for the compute instance."""

    user_id: UUID
    """ID of the user associated with the compute instance."""

    workspace_id: UUID
    """ID of the workspace the compute instance belongs to."""

    instance_type: str | None
    """Type of instance (e.g., instance type string)."""

    req_ram_gb: int | None
    """Requested RAM in GiB."""

    req_cpu_cores: int | None
    """Requested number of CPU cores."""

    req_storage: int | None
    """Requested disk storage in GiB."""

    cluster_size: int
    """Number of compute nodes in the cluster."""

    termination: TerminationSchema | None
    """Termination settings, if applicable."""

    gc_inactive_hours: int
    """Number of hours before garbage collection of inactive instances."""

    request_time: datetime
    """Timestamp when the compute instance was requested."""

    mode: DBClusterModeSchema
    """Mode of the database cluster."""

    created_at: datetime
    """Timestamp when the compute instance was created."""

    updated_at: datetime
    """Timestamp when the compute instance was last updated."""

    deleted_at: datetime | None
    """Timestamp when the compute instance was deleted, if applicable."""

class LogLevelSchema(Enum):
    """Log level for a compute cluster."""

    Info: int
    Debug: int
    Trace: int

class ComputeClusterPublicInfoSchema:
    cluster_id: UUID
    public_address: str
    public_server_key: str

class ComputeStatusSchema(Enum):
    Starting: int
    Running: int
    Stopping: int
    Stopped: int
    FailedInfra: int
    FailedBoot: int
    Failed: int

def list_compute(workspace_id: UUID) -> list[ComputeSchema]: ...
def get_compute_details(workspace_id: UUID, compute_id: UUID) -> ComputeSchema: ...
def get_compute_server_info(
    workspace_id: UUID, compute_id: UUID
) -> ComputeClusterPublicInfoSchema: ...
def start_compute(
    workspace_id: UUID,
    cluster_size: int,
    mode: DBClusterModeSchema,
    cpus: int | None,
    ram_gb: int | None,
    instance_type: str | None,
    storage: int | None,
    requirements_txt: str | None,
    labels: list[str] | None,
    log_level: LogLevelSchema | None,
) -> str: ...
def stop_compute(
    workspace_id: UUID,
    compute_id: UUID,
) -> None: ...
def get_compute_status(
    workspace_id: UUID,
    compute_id: UUID,
) -> ComputeStatusSchema: ...

class WorkspaceWithUrlSchema:
    workspace: WorkspaceSchema
    url: str

class WorkspaceSetupUrlSchema:
    setup_url: str
    template_url: str

class DeleteWorkspaceSchema:
    stack_name: str
    url: str

def create_workspace(
    name: str,
    organization_id: UUID,
) -> WorkspaceWithUrlSchema: ...
def get_workspace_setup_url(workspace_id: UUID) -> WorkspaceSetupUrlSchema: ...
def delete_workspace(workspace_id: UUID) -> DeleteWorkspaceSchema | None: ...
def get_user() -> UserSchema: ...

class UserSchema:
    id: UUID
    """User id."""
    first_name: str | None
    """First name."""
    last_name: str | None
    """Last name."""
    avatar_url: str | None
    """Avatar url."""
    default_workspace_id: UUID | None
    """The default workspace id (if None specified)."""
    newsletter_updates: bool
    """Whether to receive newsletter updates."""
    personal_emails: bool
    """Whether to receive personal updates."""

class NotFoundError(Exception):
    """Exception raised when a resource is not found."""

class AuthLoadError(Exception):
    """Exception raised when no authentication could be loaded."""

class QueryInfoPy:
    total_stages: int
    finished_stages: int
    failed_stages: int
    head: bytes | None
    n_rows_result: int | None
    errors: list[str]
    sink_dst: list[str]
    file_type_sink: FileType
    ir_plan_explain: str | None
    ir_plan_dot: str | None
    phys_plan_explain: str | None

def deserialize_query_result(
    payload: typing.Any,
) -> QueryInfoPy: ...
def get_query_result(query_id: UUID) -> QueryInfoPy: ...
def submit_query(
    compute_id: UUID, plan: bytes, settings: bytes, labels: list[str] | None
) -> str: ...
def cancel_interactive_query(
    address: str,
    query_id: UUID,
    public_server_cert: bytes,
) -> None: ...
def cancel_batch_query(
    workspace_id: UUID,
    query_id: UUID,
) -> None: ...
def get_interactive_query_result(
    address: str,
    query_id: UUID,
    public_server_cert: bytes,
) -> QueryInfoPy: ...
def get_interactive_query_status(
    address: str,
    query_id: UUID,
    public_server_cert: bytes,
) -> TaskStatusType: ...
def do_query(
    address: str,
    plan: bytes,
    settings: bytes,
    public_server_cert: bytes,
) -> str: ...

class OrganizationSchema:
    """Represents an organization schema."""

    id: UUID
    """Organization ID (UUID v7)."""

    name: str
    """Organization Name."""

    description: str
    """Organization Description."""

    avatar_url: str
    """Organization avatar."""

    owner_id: UUID
    """User who owns the Organization."""

    status: WorkspaceStateSchema
    """Status of the Workspace."""

    created_at: datetime
    """Creation timestamp."""

    updated_at: datetime
    """Last update timestamp."""

    deleted_at: datetime | None
    """Timestamp of the last deletion."""

def create_organization(
    name: str,
) -> OrganizationSchema: ...
def get_organizations(name: str | None = None) -> list[OrganizationSchema]: ...
def get_organization(organization_id: UUID) -> OrganizationSchema: ...
def delete_organization(organization_id: UUID) -> None: ...
