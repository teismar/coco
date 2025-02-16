# coco/utils.py

import random
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

def display_logo():
    """
    Display the CLI logo.
    If the logo file is empty or missing, log an error message.
    """
    logo_path = Path(__file__).parent.parent / "assets" / "logo.txt"
    try:
        with open(logo_path, "r") as file:
            logo = file.read().strip()
            if logo:
                console.print(logo)
            else:
                console.print("[bold red]Logo file is empty![/bold red]")
    except FileNotFoundError:
        console.print("[bold red]Logo file not found![/bold red]")

def load_fun_facts():
    """
    Load fun facts from assets/funfacts.txt.
    Returns a list of fun facts if the file exists; otherwise, logs an error.
    """
    facts_path = Path(__file__).parent.parent / "assets" / "funfacts.txt"
    try:
        with open(facts_path, "r") as file:
            facts = [line.strip() for line in file if line.strip()]
        return facts
    except FileNotFoundError:
        console.print("[bold red]Fun facts file not found![/bold red]")
        return []

def display_random_fun_fact(facts):
    """
    Display a random fun fact in a panel.
    """
    if facts:
        fact = random.choice(facts)
        panel = Panel(
            Text(fact, justify="center", style="italic cyan"),
            title="Did You Know?",
            border_style="cyan"
        )
        console.print(panel)
