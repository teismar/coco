#!/usr/bin/env python
"""
CoCo: Your Container Companion

Commands:
    extract-images: Extract Docker image names from a Docker Compose file.
    pull-images:    Pull Docker images concurrently and display their status.
"""

import typer
import subprocess
import time
from pathlib import Path
import concurrent.futures
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.traceback import install
from typer import Context
from coco.utils import display_logo, load_fun_facts, display_random_fun_fact, find_compose_file

# Install Rich tracebacks for prettier error messages.
install()

app = typer.Typer()
console = Console()


def pull_image(image: str) -> subprocess.CompletedProcess:
    """
    Pull a Docker image using 'docker pull <image>'.

    Args:
        image (str): The Docker image to pull.

    Returns:
        subprocess.CompletedProcess: The result of running the docker pull command.
    """
    result = subprocess.run(
        ["docker", "pull", image],
        capture_output=True,
        text=True,
    )
    return result


@app.callback(invoke_without_command=True)
def main(ctx: Context):
    """
    Main callback for the CoCo CLI.

    Displays the logo and help text if no subcommand is invoked.

    Args:
        ctx (Context): Typer context.
    """
    if ctx.invoked_subcommand is None:
        display_logo()
        typer.echo(ctx.get_help())


@app.command("pull-images")
def pull_images(
        images_file: Path = typer.Argument(
            "images.txt", help="File containing list of images to pull"
        )
):
    """
    Pull Docker images concurrently and display a live overview of their statuses.

    The overview table updates frequently to show which images are still running
    (displayed in orange) and which have finished (Success in green, Failed in red).

    Args:
        images_file (Path): Path to the file containing a list of Docker images.
    """
    if not images_file.exists():
        console.print(f"[bold red]The file {images_file} does not exist.[/bold red]")
        raise typer.Exit(code=1)

    with images_file.open("r") as file:
        images = [line.strip() for line in file if line.strip()]
    if not images:
        console.print("[bold yellow]No images to pull.[/bold yellow]")
        raise typer.Exit()

    # Dictionary to store each image's future and its current status.
    tasks = {}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for image in images:
            future = executor.submit(pull_image, image)
            tasks[image] = {"future": future, "status": "Running"}

        with Live(refresh_per_second=5, console=console) as live:
            while not all(data["future"].done() for data in tasks.values()):
                # Update statuses for tasks that have finished.
                for image, data in tasks.items():
                    if data["future"].done() and data["status"] == "Running":
                        ret = data["future"].result().returncode
                        data["status"] = "Success" if ret == 0 else "Failed"
                # Build the overview table.
                table = Table(title="Docker Pull Overview")
                table.add_column("Index", justify="right")
                table.add_column("Image")
                table.add_column("Status")
                for i, (img, data) in enumerate(tasks.items(), start=1):
                    status = data["status"]
                    if status == "Running":
                        status_colored = "[bold orange1]Running[/bold orange1]"
                    elif status == "Success":
                        status_colored = "[green]Success[/green]"
                    else:
                        status_colored = "[red]Failed[/red]"
                    table.add_row(str(i), img, status_colored)
                running = sum(1 for data in tasks.values() if data["status"] == "Running")
                header = (
                    f"[bold orange1]{running} image(s) still running[/bold orange1]"
                    if running
                    else "[bold green]All pulls finished[/bold green]"
                )
                live.update(Panel.fit(table, title=header))
                time.sleep(0.2)
            # Final update for any remaining tasks.
            for image, data in tasks.items():
                if data["status"] == "Running":
                    ret = data["future"].result().returncode
                    data["status"] = "Success" if ret == 0 else "Failed"
            table = Table(title="Docker Pull Overview")
            table.add_column("Index", justify="right")
            table.add_column("Image")
            table.add_column("Status")
            for i, (img, data) in enumerate(tasks.items(), start=1):
                status = data["status"]
                if status == "Running":
                    status_colored = "[bold orange1]Running[/bold orange1]"
                elif status == "Success":
                    status_colored = "[green]Success[/green]"
                else:
                    status_colored = "[red]Failed[/red]"
                table.add_row(str(i), img, status_colored)
            live.update(Panel.fit(table, title="[bold green]All pulls finished[/bold green]"))
            time.sleep(1)


@app.command("extract-images")
def extract_images(
        compose_file: Path = typer.Argument(
            None, help="Path to the Docker Compose file"
        ),
        output_file: Path = typer.Argument(
            "images.txt", help="Output file to save image names"
        )
):
    """
    Extract Docker image names from a Docker Compose file.

    Reads a Docker Compose file (YAML) and extracts the image names defined in the
    'services' section, then writes them to an output file.

    Args:
        compose_file (Path): Path to the Docker Compose file.
        output_file (Path): Path to the output file to save extracted image names.
    """
    facts = load_fun_facts()
    if facts:
        display_random_fun_fact(facts)

    if compose_file is None:
        # Attempt to locate a standard Docker Compose file in the current directory.
        from coco.utils import find_compose_file  # Import here if not globally available
        compose_file = find_compose_file()
        if compose_file is None:
            console.print("[bold red]No Docker Compose file found in the current directory.[/bold red]")
            raise typer.Exit(code=1)
        else:
            console.print(f"[bold yellow]No compose file specified. Using {compose_file}[/bold yellow]")

    with console.status("[bold green]Resolving Docker Compose file...[/bold green]"):
        result = subprocess.run(
            ["docker", "compose", "-f", str(compose_file), "convert"],
            capture_output=True,
            text=True,
        )

    if result.returncode != 0:
        console.print(f"[bold red]Error running 'docker compose convert': {result.stderr}[/bold red]")
        raise typer.Exit(code=1)

    try:
        import yaml
        compose_data = yaml.safe_load(result.stdout)
    except yaml.YAMLError as e:
        console.print(f"[bold red]Error parsing YAML: {e}[/bold red]")
        raise typer.Exit(code=1)

    services = compose_data.get("services", {})
    images = [service.get("image") for service in services.values() if "image" in service]

    if not images:
        console.print("[bold yellow]No images found in the Compose file.[/bold yellow]")
        raise typer.Exit()

    with output_file.open("w") as file:
        file.write("\n".join(images))

    console.print(f"[bold green]Image names extracted to {output_file}[/bold green]")


if __name__ == "__main__":
    app()
