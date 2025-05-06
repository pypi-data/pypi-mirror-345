import typer
import enum
from rich.console import Console
from typing_extensions import Annotated
from pathlib import Path

from kudaflib.logic.process import metadata_process
from kudaflib.logic.utils import (
    check_filepaths_validity,
)


class TargetEnv(str, enum.Enum):
    """
    Target Environment Enum
    """
    DEV = "DEV"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"


console = Console()


app = typer.Typer(
    pretty_exceptions_enable=True,
    pretty_exceptions_short=False,
    pretty_exceptions_show_locals=True,
)


@app.callback()
def callback():
    """
    Kudaf Metadata CLI Tools
    """
    ...


@app.command(name='upload')
def create_metadata(
    config_yaml_path: Annotated[Path, typer.Option(
        help="Absolute path to the YAML configuration file"
    )] = Path.cwd() / 'config.yaml',
    output_metadata_dir: Annotated[Path, typer.Option(
        help="Absolute path to directory where the Metadata files are to be written to" 
    )] = Path.cwd(),
    target_environment: Annotated[str, typer.Option(
        prompt=True,
        show_choices=True,
        help="Please enter Kudaf-Metadata's Target Environment (DEV, STAGING, PRODUCTION)",
    )] = "DEV",
    api_key: Annotated[str, typer.Option(
        prompt=True,
        help="Kudaf Metadata API Key"
    )] = None,
):
    """
    Upload metadata to the KUDAF Metadata Backend (Catalogs, Datasets, UnitTypes and Variables)  

    If any of the optional directories is not specified, the current directory is used as default.

    """
    if target_environment not in TargetEnv.__members__:
        console.rule("[bold red]:poop: Invalid Target Environment :confused:", style="red")
        console.print(f"[bold blue]Please enter a valid Target Environment (DEV, STAGING, PRODUCTION)[/bold blue]")
        raise typer.Exit()

    try:
        check_filepaths_validity([config_yaml_path, output_metadata_dir])

        console.rule("[bold bright_yellow]:zap: Starting KUDAF Metadata upload... :person_juggling:")

        variables = metadata_process.create(
            config_yaml_path, 
            target_environment, 
            api_key, 
            output_metadata_dir,
        )
    except Exception as e:
        console.rule("[bold red]:poop: An Exception occurred :confused:", style="red")
        console.print(e)
        raise typer.Exit()

    if "errors" in variables:
        console.rule("[bold red]:poop: An Error occurred :confused:", style="red")
        console.print(f"[red]Error: {variables['errors']}[/red]")
        console.rule(style="red")
        raise typer.Exit()
    
    console.rule("[bold green]:zap: Success! :partying_face:")

    return variables


@app.command(name='metadata')
def gen_metadata(
    config_yaml_path: Annotated[Path, typer.Option(
        help="Absolute path to the YAML configuration file"
    )] = Path.cwd() / 'config.yaml',
    output_metadata_dir: Annotated[Path, typer.Option(
        help="Absolute path to directory where the Metadata files are to be written to" 
    )] = Path.cwd(),
):
    """
    Generate Variables/UnitTypes Metadata  

    JSON metadata files ('variables.json' and maybe 'unit_types.json') will be written to the \n
    (optionally) given output directory. \n

    If any of the optional directories is not specified, the current directory is used as default.

    """
    try:
        check_filepaths_validity([config_yaml_path, output_metadata_dir])

        variables = metadata_process.generate(
            config_yaml_path, output_metadata_dir,
        )
    except Exception as e:
        console.rule("[bold red]:poop: An Exception occurred :confused:", style="red")
        console.print(f"[red] {e}")
        console.rule()
        raise typer.Exit()

    console.rule("[bold green]:zap: Success! :partying_face:")
    console.print(f"[bold blue]Generated Metadata (Variables and UnitTypes) available at :point_right: [italic]{output_metadata_dir}[/italic][/bold blue]")
    console.rule()

    return variables
