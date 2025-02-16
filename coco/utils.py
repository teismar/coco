# coco/utils.py

import random
from importlib import resources
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def find_compose_file() -> Path | None:
    """
    Search for a standard Docker Compose file in the current directory.

    Returns:
        Path: The path to the first found Docker Compose file, or None if not found.
    """
    standard_files = [
        "compose.yaml",
        "compose.yml",
        "docker-compose.yaml",
        "docker-compose.yml",
    ]
    for filename in standard_files:
        potential_path = Path(filename)
        if potential_path.exists():
            return potential_path
    return None


def load_logo() -> str:
    return resources.read_text("coco.assets", "logo.txt")


def display_logo():
    """
    Display the CLI logo.
    If the logo file is empty or missing, log an error message.
    """
    console.print(load_logo())


def load_fun_facts() -> list[str]:
    content = resources.read_text("coco.assets", "funfacts.txt")
    return [line.strip() for line in content.splitlines() if line.strip()]


def display_random_fun_fact(facts):
    """
    Display a random fun fact in a panel.
    """
    if facts:
        fact = random.choice(facts)  # noqa: S311
        panel = Panel(
            Text(fact, justify="center", style="italic cyan"),
            title="Did You Know?",
            border_style="cyan",
        )
        console.print(panel)
