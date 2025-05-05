from datetime import datetime, timedelta
import rich
import typer
import time
from rich.progress import Progress, SpinnerColumn, TextColumn
from inferless_cli.utils.exceptions import InferlessCLIError, ServerError
from inferless_cli.utils.helpers import (
    analytics_capture_event,
    decrypt_tokens,
    log_exception,
)
from inferless_cli.utils.services import get_build_logs, get_call_logs
import dateutil.parser


def log_prompt(
    model_id: str,
    logs_type: str = "BUILD",
    import_logs: bool = False,
    tail: bool = False,
):
    try:
        _, _, _, workspace_id, workspace_name = decrypt_tokens()
        if not model_id:
            raise InferlessCLIError(
                "[red]Please provide a model id or model import id[/red]"
            )
        if logs_type == "BUILD":
            handle_build_logs(import_logs, model_id, tail)
            analytics_capture_event(
                "cli_model_logs",
                payload={
                    "model_id": model_id,
                    "workspace_id": workspace_id,
                    "workspace_name": workspace_name,
                    "logs_type": logs_type,
                    "tail": tail,
                },
            )
        elif logs_type == "CALL":
            handle_call_logs(model_id, tail)
            analytics_capture_event(
                "cli_model_logs",
                payload={
                    "model_id": model_id,
                    "workspace_id": workspace_id,
                    "workspace_name": workspace_name,
                    "logs_type": logs_type,
                    "tail": tail,
                },
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
        log_exception(error)
        rich.print("\n[red]Something went wrong[/red]")
        raise typer.Abort(1)


def handle_call_logs(model_id, tail=False):
    try:
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
        payload = {
            "model_id": model_id,
            "time_from": start_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "time_to": end_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        }
        token = None
        last_log_time = None

        # Initial log fetch
        while True:
            # Fetch logs based on the build_id and token
            if token:
                payload["next_token"] = token
            try:
                logs = get_call_logs(payload)
            except Exception as e:
                raise InferlessCLIError(e)

            if len(logs["details"]) == 0 and not token:
                rich.print("\nNo Logs found\n")
                if not tail:
                    return

            # Reverse the logs before printing
            logs["details"].reverse()
            print_logs(logs)

            # Update last log time if we have logs
            if logs["details"]:
                try:
                    last_log_time = dateutil.parser.isoparse(
                        logs["details"][-1]["time"]
                    )
                except Exception:
                    pass

            # Check if there is a next_token
            next_token = logs.get("next_token")
            if not next_token:
                break

            # Update the token for the next iteration
            token = next_token

        # If tail flag is not set, we're done
        if not tail:
            return

        # Continue streaming logs
        with Progress(
            SpinnerColumn(),
            TextColumn("[yellow]Tailing logs... Press Ctrl+C to exit[/yellow]"),
            transient=False,
            refresh_per_second=4,
        ) as progress:
            progress_task = progress.add_task("", total=None)
            while True:
                try:
                    time.sleep(10)  # Wait for 10 seconds before fetching new logs

                    # Update time_from to the last log time + 1 microsecond
                    if last_log_time:
                        # Add 1 microsecond to last log time
                        last_log_time_plus = last_log_time + timedelta(milliseconds=1)
                        payload["time_from"] = last_log_time_plus.strftime(
                            "%Y-%m-%dT%H:%M:%S.%fZ"
                        )

                    # Update time_to to current time
                    payload["time_to"] = datetime.now().strftime(
                        "%Y-%m-%dT%H:%M:%S.%fZ"
                    )

                    # Reset token for new streaming request
                    if "next_token" in payload:
                        del payload["next_token"]

                    logs = get_call_logs(payload)

                    if logs["details"]:
                        # Temporarily stop the progress bar while printing logs
                        progress.remove_task(progress_task)
                        # Reverse the logs before printing
                        logs["details"].reverse()
                        print_logs(logs)
                        try:
                            last_log_time = dateutil.parser.isoparse(
                                logs["details"][-1]["time"]
                            )
                        except Exception:
                            # Silently continue if timestamp parsing fails
                            pass
                        # Resume the progress bar
                        progress_task = progress.add_task("", total=None)

                except KeyboardInterrupt:
                    progress.remove_task(progress_task)
                    rich.print("[yellow]Stopping log stream.[/yellow]")
                    return
                except Exception as e:
                    progress.remove_task(progress_task)
                    error_msg = str(e) if str(e) else "Unknown error occurred"
                    rich.print(f"[red]Error fetching logs: {error_msg}[/red]")
                    progress_task = progress.add_task("", total=None)
                    time.sleep(10)  # Wait before retrying

    except Exception as e:
        error_msg = str(e) if str(e) else "Unknown error occurred"
        raise InferlessCLIError(
            f"[red]Error while fetching call logs: {error_msg}[/red]"
        )


def handle_build_logs(import_logs, model_id, tail=False):
    try:
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
        _type = "MODELIMPORT" if import_logs else "MODEL"
        payload = {
            "model_id": model_id,
            "time_from": start_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "time_to": end_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "type": _type,
        }
        token = None
        last_log_time = None

        # Initial log fetch
        while True:
            # Fetch logs based on the build_id and token
            if token:
                payload["next_token"] = token
            try:
                logs = get_build_logs(payload)
            except Exception as e:
                raise InferlessCLIError(e)

            if len(logs["details"]) == 0 and not token:
                rich.print("\nNo Logs found\n")
                if not tail:
                    return

            # Reverse the logs before printing
            logs["details"].reverse()
            print_logs(logs)

            # Update last log time if we have logs
            if logs["details"]:
                try:
                    last_log_time = dateutil.parser.isoparse(
                        logs["details"][-1]["time"]
                    )
                except Exception:
                    pass

            # Check if there is a next_token
            next_token = logs.get("next_token")

            if not next_token:
                break

            # Update the token for the next iteration
            token = next_token

        # If tail flag is not set, we're done
        if not tail:
            return

        # Continue streaming logs
        with Progress(
            SpinnerColumn(),
            TextColumn("[yellow]Tailing logs... Press Ctrl+C to exit[/yellow]"),
            transient=False,
            refresh_per_second=4,
        ) as progress:
            progress_task = progress.add_task("", total=None)
            while True:
                try:
                    time.sleep(10)  # Wait for 10 seconds before fetching new logs

                    # Update time_from to the last log time + 1 microsecond
                    if last_log_time:
                        # Add 1 microsecond to last log time
                        last_log_time_plus = last_log_time + timedelta(milliseconds=1)
                        payload["time_from"] = last_log_time_plus.strftime(
                            "%Y-%m-%dT%H:%M:%S.%fZ"
                        )

                    # Update time_to to current time
                    payload["time_to"] = datetime.now().strftime(
                        "%Y-%m-%dT%H:%M:%S.%fZ"
                    )

                    # Reset token for new streaming request
                    if "next_token" in payload:
                        del payload["next_token"]

                    logs = get_build_logs(payload)

                    if logs["details"]:
                        # Temporarily stop the progress bar while printing logs
                        progress.remove_task(progress_task)
                        # Reverse the logs before printing
                        logs["details"].reverse()
                        print_logs(logs)
                        try:
                            last_log_time = dateutil.parser.isoparse(
                                logs["details"][-1]["time"]
                            )
                        except Exception:
                            # Silently continue if timestamp parsing fails
                            pass
                        # Resume the progress bar
                        progress_task = progress.add_task("", total=None)

                except KeyboardInterrupt:
                    progress.remove_task(progress_task)
                    rich.print("[yellow]Stopping log stream.[/yellow]")
                    return
                except Exception as e:
                    progress.remove_task(progress_task)
                    error_msg = str(e) if str(e) else "Unknown error occurred"
                    rich.print(f"[red]Error fetching logs: {error_msg}[/red]")
                    progress_task = progress.add_task("", total=None)
                    time.sleep(10)  # Wait before retrying

    except Exception as e:
        error_msg = str(e) if str(e) else "Unknown error occurred"
        raise InferlessCLIError(
            f"[red]Error while fetching build logs: {error_msg}[/red]"
        )


def print_logs(logs):
    for log_entry in logs["details"]:
        timestamp = "-"
        try:
            timestamp = dateutil.parser.isoparse(log_entry["time"])
        except Exception as e:
            timestamp = "-"
            log_exception(e)

        log_line = log_entry["log"]

        rich.print(f"[green]{timestamp}[/green]: {log_line}")
