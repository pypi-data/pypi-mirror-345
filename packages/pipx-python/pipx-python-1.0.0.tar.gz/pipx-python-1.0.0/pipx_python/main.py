import argparse
import json
import subprocess
from pathlib import Path

PARSER = argparse.ArgumentParser(description='Run the python associated with a venv')
PARSER.add_argument('executable')
PARSER.add_argument('arguments', nargs="*")
PARSER.add_argument('--venv', action='store_true', default=False, help="Output path to venv")
PARSER.add_argument('--mod-path', help="Output path to module.")



def main():
    args = PARSER.parse_args()
    venv_path = get_venv_path()

    data = json.loads(subprocess.check_output(["pipx", "list", "--json"]))
    venv_for_app = {}
    for k, v in data["venvs"].items():
        for app in v["metadata"]["main_package"]["apps"]:
            if app in venv_for_app:
                raise Exception(f'Multiple pipx venvs for app: {app}')

            venv_for_app[app] = k

    python_path = venv_path / venv_for_app[args.executable] / "bin" / "python"

    if args.venv:
        print(venv_path / venv_for_app[args.executable])
        return

    if args.mod_path:
        module_path = subprocess.check_output([python_path, "-c", f'import importlib; print(importlib.import_module({args.mod_path!r}).__file__)']).decode('utf8').strip()
        module_path = Path(module_path)

        if module_path.name == "__init__.py":
            module_path = str(module_path.parent) + "/"
        print(module_path)
        return



    subprocess.call([python_path] + args.arguments )

def get_venv_path():
    environment = subprocess.check_output(["pipx", "environment"]).decode('utf8')
    for line in environment.splitlines():
        if "=" not in line:
            continue

        name, value = line.split("=")
        if name == "PIPX_LOCAL_VENVS":
            return Path(value)
    else:
        raise Exception('Could not find PIPX_LOCAL_VENVS in pipx enviornment')
