import rich
import typer
import shutil
import subprocess

from rich.table import Table
from inferless_cli.utils.exceptions import InferlessCLIError, ServerError
from inferless_cli.utils.helpers import analytics_capture_event, log_exception
from inferless_cli.utils.services import (
    callback_with_auth_validation,
    create_presigned_download_url,
    get_explore_models_list,
    get_file_download,
    set_onboarding_status,
)

scaffold_app = typer.Typer(
    help="Scaffold existing model templates or explore available templates"
)


@scaffold_app.callback(invoke_without_command=True, no_args_is_help=True)
def scaffold_prompt(
    ctx: typer.Context,
    demo: bool = typer.Option(False, "--demo", "-d", help="Scaffold a demo project"),
):
    callback_with_auth_validation()
    if not ctx.invoked_subcommand:
        try:
            if demo:
                payload_apppy = {
                    "url_for": "ONBOARDING_FILE_DOWNLOAD",
                    "file_name": "app.py",
                }
                res = create_presigned_download_url(payload_apppy)
                response_apppy = get_file_download(res)
                if response_apppy.status_code == 200:
                    app_file_path = "app.py"
                    with open(app_file_path, "wb") as app_file:
                        app_file.write(response_apppy.content)

                payload_yaml = {
                    "url_for": "ONBOARDING_FILE_DOWNLOAD",
                    "file_name": "runtime.yaml",
                }
                res_yaml = create_presigned_download_url(payload_yaml)
                response_yaml = get_file_download(res_yaml)
                if response_yaml.status_code == 200:
                    yaml_file_path = "runtime.yaml"
                    with open(yaml_file_path, "wb") as yaml_file:
                        yaml_file.write(response_yaml.content)

                # config_file_path = "inferless.yaml"

                # with open(config_file_path, "w") as config_file:
                #     config_file.write(DEMO_INFERLESS_YAML_FILE)
                set_onboarding_status(
                    {"onboarding_type": "cli", "state": "files_downloaded"}
                )
                rich.print("Scaffolding demo project done")
                analytics_capture_event("cli_sample_model", payload={})
                analytics_capture_event(
                    "onbaording_cli_scaffold_complete",
                    payload={},
                )

            else:
                raise InferlessCLIError("Either specify a command or use --demo flag")

        except ServerError as error:
            rich.print(f"\n[red]Inferless Server Error: [/red] {error}")
            log_exception(error)
            raise typer.Exit()
        except InferlessCLIError as error:
            rich.print(f"\n[red]Inferless CLI Error: [/red] {error}")
            log_exception(error)
            raise typer.Exit()
        except Exception as error:
            rich.print(f"\n[red]Something went wrong {error}[/red]")
            log_exception(error)
            raise typer.Abort(1)


@scaffold_app.command(
    "use",
    help="Scaffold a specific model by name (git should be installed for this command to work)",
    no_args_is_help=True,
)
def scaffold_use(
    name: str = typer.Option(..., "--name", "-n", help="Name of the model to scaffold")
):
    try:
        if shutil.which("git") is None:
            raise InferlessCLIError(
                "Git is not installed. Please install Git and try again."
            )
        # Add logic to fetch and scaffold the specified model
        analytics_capture_event("cli_scaffold_use_model", payload={"model": name})
        if name:
            rich.print(
                f"\nScaffolding project using model: [green][bold]{name}[/bold][/green]\n"
            )
            res = get_explore_models_list({"search_term": name})
            selected_repo = None
            for repo in res:
                if repo["name"] == name:
                    selected_repo = repo
                    break
            if selected_repo is None:
                raise InferlessCLIError(f"Model with name {name} not found")

            clone_url = selected_repo.get("clone_url")
            if clone_url:
                result = subprocess.run(
                    ["git", "clone", "--depth", "1", clone_url],
                    capture_output=True,
                    text=True,
                )
                dir_name = clone_url.split("/")[-1].replace(".git", "")
                if result.returncode == 0:
                    rich.print(
                        f"Successfully cloned repository: [green]{clone_url}[/green]\n"
                    )

                    rich.print(
                        f"cd into the project directory [blue]`cd {dir_name}`[/blue] \n\n[green]You can now start working on the project.[/green]\n"
                    )
                else:
                    rich.print(
                        f"[bold][yellow]HINT:[/yellow][/bold] if you are trying to clone again, try deleting the directory [blue]`rm -rf {dir_name}`[/blue]\n"
                    )
                    raise InferlessCLIError(
                        f"Failed to clone repository: {result.stderr}"
                    )
            else:
                raise InferlessCLIError(f"Clone URL not found for model {name}")

    except ServerError as error:
        rich.print(f"\n[red]Inferless Server Error: [/red] {error}")
        log_exception(error)
        raise typer.Exit()
    except InferlessCLIError as error:
        rich.print(f"\n[red]Inferless CLI Error: [/red] {error}")
        log_exception(error)
        raise typer.Exit()
    except Exception as error:
        rich.print(f"\n[red]Something went wrong {error}[/red]")
        log_exception(error)
        raise typer.Abort(1)


@scaffold_app.command("explore", help="Explore available scaffold templates")
def scaffold_explore(
    search: str = typer.Option(None, "--search", "-s", help="Search keyword"),
):
    try:
        res = None
        if search:
            rich.print(
                f"\nExploring scaffold templates with search: [green][bold]{search}[/bold][/green]\n"
            )
            res = get_explore_models_list({"search_term": search})
        else:
            rich.print("\nExploring scaffold templates\n")
            rich.print(
                "\n Showing 30 most popular templates. use `--search` to search for specific templates. \n"
            )
            res = get_explore_models_list({})

        if res:
            table = Table(
                title="Model Templates",
                box=rich.box.ROUNDED,
                title_style="bold Black underline on white",
            )
            table.add_column("Name", style="cyan", no_wrap=True)
            table.add_column("Command", style="magenta", no_wrap=True)
            # table.add_column("Topics", style="green")
            # table.add_column("Github URL", style="green")

            for repo in res:
                command = f"inferless scaffold use --name '{repo['name']}'"
                table.add_row(repo["name"], command)
            rich.print("\n")
            rich.print(table)
            rich.print("\n")
            rich.print("\n")
        else:
            rich.print("\nNo results found.")

        analytics_capture_event(
            "cli_scaffold_explore_templates", payload={"search": search}
        )
    except ServerError as error:
        rich.print(f"\n[red]Inferless Server Error: [/red] {error}")
        log_exception(error)
        raise typer.Exit()
    except InferlessCLIError as error:
        rich.print(f"\n[red]Inferless CLI Error: [/red] {error}")
        log_exception(error)
        raise typer.Exit()
    except Exception as error:
        rich.print(f"\n[red]Something went wrong {error}[/red]")
        log_exception(error)
        raise typer.Abort(1)


if __name__ == "__main__":
    scaffold_app()
