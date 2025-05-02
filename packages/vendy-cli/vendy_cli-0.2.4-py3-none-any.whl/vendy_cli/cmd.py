import typer
from typing import Optional
import yaml
import git
import shutil
import tempfile
import os
from pathlib import Path
from cookiecutter.main import cookiecutter
from rich.console import Console
from rich.table import Table
import pkg_resources

app = typer.Typer(
    help="Friendly Code Vending Machine",
)
home = Path.home()
console = Console()


def get_template_type(name: str) -> str:
    with open(f"{home}/.vendy/config.yaml") as stream:
        try:
            templates = yaml.safe_load(stream)
            for template in templates["templates"]:
                if name == template["name"]:
                    return template["type"]
            return None
        except yaml.YAMLError as exc:
            print(exc)


def get_template_loc(name: str) -> str:
    with open(f"{home}/.vendy/config.yaml") as stream:
        try:
            templates = yaml.safe_load(stream)
            for template in templates["templates"]:
                if name == template["name"]:
                    return template["path"], template["version"]
            return None
        except yaml.YAMLError as exc:
            print(exc)


def deploy_cc_template(name: str, dir: str):
    if dir:
        path, version = get_template_loc(name)
        cookiecutter(path, checkout=version, directory=dir)
    else:
        path, version = get_template_loc(name)
        cookiecutter(path, checkout=version)


def deploy_file(name: str, file_path: str):
    path, version = get_template_loc(name)
    t = tempfile.mkdtemp()
    git.Repo.clone_from(path, t, branch=version, depth=1)
    shutil.move(os.path.join(t, file_path), ".")


@app.command("version")
def version():
    print(f"Vendy CLI Version: {pkg_resources.get_distribution('vendy-cli').version}")
    raise typer.Exit()


@app.command("list", help="List install templates.(also 'ls')")
@app.command("ls", hidden=True)
def list():
    table = Table(title="Configured Templates")
    table.add_column("Name")
    table.add_column("Type")
    table.add_column("Version")
    table.add_column("Path")
    with open(f"{home}/.vendy/config.yaml") as stream:
        try:
            templates = yaml.safe_load(stream)
            for template in templates["templates"]:
                table.add_row(
                    template["name"],
                    template["type"],
                    template["version"],
                    template["path"],
                )
        except yaml.YAMLError as exc:
            print(exc)

    console.print(table)


@app.command("add", help="Add a new template")
def add(
    name: str,
    path: str,
    version: Optional[str] = "main",
    type: Optional[str] = "cookiecutter",
):
    config_file = Path(f"{home}/.vendy/config.yaml")
    entry = {"name": name, "type": type, "path": path, "version": version}

    if config_file.exists():
        with open(f"{home}/.vendy/config.yaml") as conf_file:
            config = yaml.safe_load(conf_file)
            if entry not in config["templates"]:
                config["templates"].append(entry)
                with open(f"{home}/.vendy/config.yaml", "w") as conf_file_new:
                    yaml.dump(config, conf_file_new)
            else:
                print("Item Already Configured")
    else:
        config = {"templates": []}
        config["templates"].append(entry)
        Path(f"{home}/.vendy").mkdir(parents=True, exist_ok=True)
        with open(f"{home}/.vendy/config.yaml", "w") as conf_file:
            yaml.dump(config, conf_file)

    table = Table(title="Added Template")
    table.add_column("Name")
    table.add_column("Type")
    table.add_column("Version")
    table.add_column("Path")
    table.add_row(entry["name"], entry["type"], entry["version"], entry["path"])
    console.print(table)


@app.command("remove", help="Remove a template. (also 'rm')")
@app.command("rm", hidden=True)
def remove(name: str):
    config_file = Path(f"{home}/.vendy/config.yaml")
    if config_file.exists():
        with open(f"{home}/.vendy/config.yaml") as conf_file:
            config = yaml.safe_load(conf_file)
            conf_file.close()
            config["templates"] = [
                template
                for template in config["templates"]
                if template.get("name") != name
            ]
            with open(f"{home}/.vendy/config.yaml", "w") as conf_file:
                yaml.dump(config, conf_file)


@app.command(
    "deploy",
    help="Deploy a new instance of a given template",
)
def deploy(name: str, dir: Optional[str] = None, file_path: Optional[str] = None):
    print(f"Deploying {name}: ")
    if get_template_type(name).lower() == "cookiecutter":
        deploy_cc_template(name, dir)
    elif get_template_type(name).lower() == "file":
        deploy_file(name, file_path)
    else:
        print(f"Type {get_template_type(name)} not supported")


def main():
    app()


if __name__ == "__main__":
    main()
