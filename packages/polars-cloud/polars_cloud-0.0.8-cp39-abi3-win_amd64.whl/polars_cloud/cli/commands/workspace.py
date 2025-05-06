from __future__ import annotations

from polars_cloud.cli.commands._utils import handle_errors
from polars_cloud.workspace import Workspace


def list_workspaces() -> None:
    """List all accessible workspaces."""
    with handle_errors():
        workspaces = Workspace.list()

    _print_workspace_list(workspaces)


def _print_workspace_list(workspaces: list[Workspace]) -> None:
    """Pretty print the list of workspaces to the console."""
    if not workspaces:
        print("No workspaces found.")
        return

    print(f"{'NAME':<15}\t{'ID':<38}STATUS")
    for workspace in workspaces:
        name = workspace.name
        name = (name[:14] + "…") if len(name) > 15 else name
        status = workspace.status
        print(f"{name:<15}\t{workspace.id!s:<38}{status!r}")


def set_up_workspace(
    workspace_name: str | None, organization_name: str | None, *, verify: bool = True
) -> None:
    """Set up a workspace in AWS.

    Parameters
    ----------
    workspace_name
        The desired name of the workspace.
    organization_name
        The name of the organization.
    verify
        Verify that the workspace was set up successfully before returning.
    """
    with handle_errors():
        if workspace_name is None:
            workspace_name = input("Workspace name: ")
        if organization_name is None:
            organization_name = input("Organization name: ")
        Workspace.setup(workspace_name, organization_name, verify=verify)


def verify_workspace(
    name: str,
    *,
    interval: None | int = None,
    timeout: None | int = None,
) -> None:
    """Verify that a workspace was created correctly."""
    with handle_errors():
        args = {}
        if interval is not None:
            args["interval"] = interval
        if timeout is not None:
            args["timeout"] = timeout
        Workspace(name=name).verify(**args)


def delete_workspace(name: str) -> None:
    """Delete a workspace."""
    with handle_errors():
        Workspace(name=name).delete()


def get_workspace_details(name: str) -> None:
    """Get the details of a workspace."""
    with handle_errors():
        workspace = Workspace(name=name)
        workspace.load()
    print(workspace)
