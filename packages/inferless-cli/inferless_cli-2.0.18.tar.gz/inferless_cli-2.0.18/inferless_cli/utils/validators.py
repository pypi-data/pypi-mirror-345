import os
import sys

import requests
from ruamel import yaml


def validate_remote_run(file_path, config_path):
    # check if file exists
    if not os.path.exists(file_path):
        raise Exception("File does not exist")

    if not is_python_310():
        raise Exception(
            "Currently only Python 3.10 is supported. Please switch to Python 3.10 to use this feature."
        )

    validate_remote_run_code(file_path)
    validate_remote_run_config(config_path)


def is_python_310():
    return sys.version_info.major == 3 and sys.version_info.minor == 10


def validate_remote_run_code(file_path):
    # check if file is a python file
    if not file_path.endswith(".py"):
        raise Exception("File must be a python file")

    # check for syntax errors using ast
    try:
        with open(file_path) as f:
            code = f.read()
            if code == "":
                raise Exception("File is empty")
            compile(code, file_path, "exec")

    except SyntaxError as e:
        raise Exception(f"Syntax error in file: {e}")
    except Exception as e:
        raise Exception(f"Error in file: {e}")


def validate_remote_run_config(config_path):
    # check if file exists
    if not os.path.exists(config_path):
        raise Exception("Config file does not exist")

    # check if file is a yaml file
    if not config_path.endswith(".yaml"):
        raise Exception("Config file must be a yaml file")

    # the yaml should have the following structure
    # build:
    #   system_packages:
    #     - libgl1-mesa-glx
    #     - ...etc.,
    #   python_packages
    #     - numpy
    #     - ...etc., pip packages
    #   run_commands
    #     - python3 main.py
    #     - ...etc., shell to run

    # check if the yaml file has the correct structure and validate the values
    # validate_remote_run_config_yaml(config_path)


def validate_remote_run_config_yaml(config_yaml):
    try:
        safe_yaml = yaml.YAML(typ="safe", pure=True)
        config = safe_yaml.load(open(config_yaml))
    except yaml.YAMLError as e:
        raise Exception(f"Error in config file: {e}")

    if config is None:
        raise Exception("Config file is empty")

    if "build" in config:
        build = config["build"]
        if "python_packages" in build:
            validate_python_packages(build["python_packages"])


def check_pypi_package(package_name, version=None):
    if version:
        url = f"https://pypi.org/pypi/{package_name}/{version}/json"
    else:
        url = f"https://pypi.org/pypi/{package_name}/json"
    response = requests.get(url)
    return response.status_code == 200


def parse_package_string(package_string):
    if "==" in package_string:
        package_name, version = package_string.split("==")
    else:
        package_name = package_string
        version = None
    return package_name, version


def validate_python_packages(package_list):
    for package_string in package_list:
        package_name, version = parse_package_string(package_string)
        if not check_pypi_package(package_name, version):
            raise Exception(f"Package {package_name} not found on PyPI")
