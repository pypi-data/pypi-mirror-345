import os
import sys
import rich
from inferless_cli.utils.helpers import decrypt_tokens, get_current_mode
from inferless_cli.utils.validators import validate_remote_run
import subprocess
import importlib
import inspect
import shlex


def remote_run_prompt(
    file_path, config_path, exclude_file, dynamic_params, gpu, timeout
):
    validate_remote_run(file_path, config_path)
    access_token, _, _, _, _ = decrypt_tokens()
    command = f"INFERLESS_ACCESS_TOKEN={access_token}"
    if timeout is not None:
        command = f"{command} INFERLESS_TIMEOUT={timeout}"
    if get_current_mode() == "DEV":
        command = f"INFERLESS_ENV=DEV {command}"
    if exclude_file:
        command = f"{command} {exclude_file}"
    if gpu:
        command = f"{command} INFERLESS_GPU={gpu}"
    command = f"IS_REMOTE_RUN=True {command}"

    # Get the absolute and relative paths
    abs_path = os.path.abspath(file_path)
    rel_path = os.path.relpath(abs_path, os.getcwd())
    _, file_name = os.path.split(abs_path)
    module_name = os.path.splitext(file_name)[0]  # Remove `.py` extension

    # If the relative path points to a file in a nested structure
    package_path = rel_path.replace(os.sep, ".").rsplit(".", 1)[0]

    # Create the dotted module path
    if package_path:
        dotted_module_path = f"{package_path}"
    else:
        dotted_module_path = module_name

    sys.path.insert(0, os.getcwd())

    app_module = None
    try:
        app_module = importlib.import_module(dotted_module_path)
    except ModuleNotFoundError:
        raise Exception(f"Module '{dotted_module_path}' not found")

    model_class = None

    local_entry_point_function = None
    for name, func in inspect.getmembers(app_module, inspect.isfunction):
        if getattr(func, "_is_local_entry_point", False):
            local_entry_point_function = name
            break

    if app_module:
        for _, obj in inspect.getmembers(app_module, inspect.isclass):
            for _, func in inspect.getmembers(obj, inspect.isfunction):
                if (hasattr(func, "_is_loader") and func._is_loader) or (
                    hasattr(func, "_is_infer") and func._is_infer
                ):
                    model_class = obj.__name__
                    break

            if model_class:
                break

    if model_class:
        inline_code = ""
        if local_entry_point_function:
            inline_code = f"""
import os
from {dotted_module_path} import {local_entry_point_function}

dynamic_params = {dynamic_params}  # Pass dynamic parameters as a dictionary
output = {local_entry_point_function}(dynamic_params)
print(output)
"""
        else:
            inline_code = f"""
import os
from {dotted_module_path} import {model_class}

model_instance = {model_class}()
dynamic_params = {dynamic_params}  # Pass dynamic parameters as a dictionary
output = model_instance.infer(dynamic_params)
print(output)
"""
        command = f"{command} python3 -c {shlex.quote(inline_code)} {config_path}"
        try:
            subprocess.run(command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            rich.print(f"\n[red]Command failed with error: {e}[/red]")
        except Exception as e:
            rich.print(f"\n[red]Unexpected Error: {e}[/red]")
    else:
        command = f"{command} python3 {file_path} {config_path}"

        try:
            subprocess.run(command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            rich.print(f"\n[red]Command failed with error: {e}[/red]")
        except Exception as e:
            rich.print(f"\n[red]Unexpected Error: {e}[/red]")

    if os.getcwd() in sys.path:
        sys.path.remove(os.getcwd())
