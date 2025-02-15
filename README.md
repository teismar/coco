# CoCo: Your Container Companion

CoCo is a simple, open-source CLI tool that helps you manage Docker Compose tasks with ease. Whether you need to extract Docker image names from a Compose file or pull Docker images concurrently while viewing live status updates, CoCo has you covered.

## Features

- **Extract Images:**  
  Parse a Docker Compose file (YAML) to extract the Docker image names from your services and save them to a file.

- **Concurrent Image Pulls:**  
  Pull Docker images concurrently with a live, updating overview.

## Installation

### PyPI

```bash
pip install coco-cli
```

### From Source

**Prerequisites:**
- Python 3.12 or higher
- Poetry

```bash
git clone https://github.com/teismar/coco
cd coco
```

Install the dependencies:

```bash
poetry install
```

Install the package:

```bash
poetry build
pipx install dist/coco_cli-0.1.0-py3-none-any.whl
```

## Usage

### Extract Images
The `extract-images` command extracts Docker image names from a Docker Compose file and saves them to a file. This also supports nested Compose files, so using the `include` directive is no problem.
```bash
coco extract docker-compose.yml images.txt
```

### Pull Images
The `pull-images` command pulls Docker images concurrently and displays a live status overview. The images to pull are read from a file, which can be generated using the `extract-images` command.
```bash
coco pull-images images.txt
```

## Contributing
Contributions are welcome! Please feel free to open issues or pull requests if you have suggestions or improvements.