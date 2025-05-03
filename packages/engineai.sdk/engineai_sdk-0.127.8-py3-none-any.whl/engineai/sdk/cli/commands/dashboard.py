"""dashboard command for engineai CLI."""

from typing import Generator
from typing import List
from typing import Optional
from urllib.parse import urlparse

import click
from rich.console import Console
from rich.table import Table

from engineai.sdk.cli.utils import get_env_var
from engineai.sdk.cli.utils import write_console
from engineai.sdk.dashboard.clients.api import DashboardAPI
from engineai.sdk.internal.clients.exceptions import APIServerError
from engineai.sdk.internal.exceptions import UnauthenticatedError
from engineai.sdk.internal.url_config import PLATFORM_URL

DASHBOARD_CREATED_MSG = (
    "\nDashboard created! To publish your dashboard, navigate to "
    "`{}` folder and run `engineai dashboard publish` to publish.\n"
)

API_USER_ERRORS = ("NOT_FOUND", "FORBIDDEN")


def _show_dashboards(dashboards: List) -> None:
    """Show table for dashboards.

    Args:
        dashboards: dashboards object list.
    """
    if dashboards:
        console = Console()
        table = Table(
            title="Dashboards",
            show_header=True,
            show_edge=True,
        )
        table.add_column("Name")
        table.add_column("Slug")
        for dash in dashboards:
            table.add_row(dash.get("name"), dash.get("slug"))
        with console.pager():
            console.print(table)
    else:
        write_console("No dashboards found.\n", 0)


def _show_versions(version_list: Generator) -> None:
    """Show table for versions.

    Args:
        version_list: versions object generator.
        slug: dashboard slug.
    """
    console = Console()
    table = Table(
        title="Versions",
        show_header=True,
        show_edge=True,
    )
    table.add_column("Version")
    table.add_column("Active")
    for version in version_list:
        table.add_row(version.get("version"), str(version.get("active")))

    if len(table.rows) > 0:
        console.print(table)


def _validate_app_slug(app_slug: Optional[str] = None) -> None:
    app_slug_var = get_env_var("APP_SLUG")
    if not app_slug_var and app_slug is None:
        write_console(
            "Please set an app. `engineai app ls` and `engineai app set`\n", 1
        )
    return app_slug or app_slug_var


def _validate_workspace_slug(workspace_slug: Optional[str] = None) -> None:
    workspace_slug_var = get_env_var("WORKSPACE_SLUG")
    if not workspace_slug_var and workspace_slug is None:
        write_console("Please set an workspace slug where the app belong\n", 1)
    return workspace_slug or workspace_slug_var


@click.group(name="dashboard", invoke_without_command=False)
@click.option("-s", "--slug", type=str, default=None, help="Dashboard slug.")
@click.pass_context
def dashboard(ctx: click.Context, slug: str) -> None:
    """Dashboard commands."""
    ctx.ensure_object(dict)
    ctx.obj["SLUG"] = slug


@dashboard.command()
@click.argument("workspace_slug", required=True, type=str)
@click.argument("app_slug", required=True, type=str)
def ls(workspace_slug: str, app_slug: str) -> None:
    """List all dashboards."""
    api = DashboardAPI()
    try:
        dashboards = api.list_user_dashboards(
            app_slug=app_slug, workspace_slug=workspace_slug
        )
        _show_dashboards(dashboards)
    except (APIServerError, UnauthenticatedError) as e:
        if e.args[-1] in API_USER_ERRORS:
            write_console(f"Invalid app slug `{app_slug}`\n", 1)
        write_console(f"{e}\n", 1)


@dashboard.group()
@click.option("-v", "--version", type=str, default=None, help="Dashboard version.")
@click.pass_context
def versions(ctx: click.Context, version: str) -> None:
    # pylint: disable=unused-argument
    """Dashboard versions subgroup commands."""
    ctx.obj["VERSION"] = version


@versions.command("ls")
@click.pass_context
def list_versions(ctx: click.Context) -> None:
    """List all versions for a given dashboard slug."""
    app_slug = _validate_app_slug()
    workspace_slug = _validate_workspace_slug()
    if not ctx.obj["SLUG"]:
        write_console(
            "Please provide a dashboard slug. "
            "Example: `engineai dashboard -s some-dashboard versions ls`\n",
            1,
        )
    api = DashboardAPI()
    try:
        version_list = api.list_dashboard_versions(
            workspace_slug, app_slug, ctx.obj["SLUG"]
        )
        _show_versions(version_list)
    except (APIServerError, UnauthenticatedError) as e:
        if e.args[-1] in API_USER_ERRORS:
            write_console(f"Invalid dashboard slug `{ctx.obj['SLUG']}`\n", 1)
        write_console(f"{e}\n", 1)


@dashboard.command(
    "create",
    help="""Create a dashboard.


            \b
            WORKSPACE_SLUG: workspace slug where dashboard will be created.
            APP_SLUG: app slug where dashboard will be created.
            """,
)
@click.argument("workspace_slug", required=True, type=str)
@click.argument("app_slug", required=True, type=str)
def create(workspace_slug: str, app_slug: str) -> None:
    """Create a dashboard with a given name."""

    try:
        dashboard_slug = click.prompt(
            "What is the dashboard slug?",
            type=str,
        )

        dashboard_name = click.prompt(
            "What is the dashboard name?",
            default=dashboard_slug.replace("-", " ").replace("_", " ").title(),
            type=str,
            show_default=True,
        )

        api = DashboardAPI()

        create_dashboard_response = api.create_dashboard(
            workspace_slug=workspace_slug,
            app_slug=app_slug,
            slug=dashboard_slug,
            name=dashboard_name,
        )
        write_console(
            "Created dashboard with name: "
            f"{create_dashboard_response.get('dashboard_name')}\n",
            0,
        )

    except (APIServerError, UnauthenticatedError) as e:
        write_console(f"\n{e}\n", 1)
        raise click.ClickException(str(e), exit_code=1) from e


@dashboard.command(
    "activate",
    help="""Activate a dashboard Version.

    \b
    WORKSPACE_SLUG: workspace slug where dashboard will be activated.
    APP_SLUG: app slug where dashboard will be activated.
    DASHBOARD_SLUG: dashboard slug.
    VERSION: dashboard version.""",
)
@click.argument("workspace_slug", required=True, type=str)
@click.argument("app_slug", required=True, type=str)
@click.argument("dashboard_slug", required=True, type=str)
@click.argument("version", required=True, type=str)
def activate_dashboard_version(
    workspace_slug: str, app_slug: str, dashboard_slug: str, version: str
) -> None:
    """Activate a dashboard version."""
    api = DashboardAPI()
    try:
        api.activate_dashboard_version(
            app_slug=app_slug,
            workspace_slug=workspace_slug,
            dashboard_slug=dashboard_slug,
            version=version,
        )

        platform_url = PLATFORM_URL.get(urlparse(api.url).netloc)

        write_console(
            f"Dashboard `{dashboard_slug}` successfully activated 🚀\n"
            "You can access it at: "
            f"{platform_url}/"
            f"workspaces/{workspace_slug}"
            f"/apps/{app_slug}/dashboards/{dashboard_slug}\n",
            0,
        )
    except (APIServerError, UnauthenticatedError) as e:
        write_console(f"{e}\n", 1)
        raise click.ClickException(str(e), exit_code=1) from e


@dashboard.command(
    "deactivate",
    help="""Deactivate a dashboard Version.

    \b
    WORKSPACE_SLUG: workspace slug where dashboard will be deactivated.
    APP_SLUG: app slug where dashboard will be deactivated.
    DASHBOARD_SLUG: dashboard slug.
    VERSION: dashboard version.""",
)
@click.argument("workspace_slug", required=True, type=str)
@click.argument("app_slug", required=True, type=str)
@click.argument("dashboard_slug", required=True, type=str)
@click.argument("version", required=True, type=str)
def deactivate_dashboard_version(
    workspace_slug: str, app_slug: str, dashboard_slug: str, version: str
) -> None:
    """Deactivate a dashboard version."""
    api = DashboardAPI()
    try:
        api.deactivate_dashboard_version(
            app_slug=app_slug,
            workspace_slug=workspace_slug,
            dashboard_slug=dashboard_slug,
            version=version,
        )

        write_console(f"Dashboard `{dashboard_slug}` successfully deactivated \n", 0)
    except (APIServerError, UnauthenticatedError) as e:
        write_console(f"{e}\n", 1)
        raise click.ClickException(str(e), exit_code=1) from e
