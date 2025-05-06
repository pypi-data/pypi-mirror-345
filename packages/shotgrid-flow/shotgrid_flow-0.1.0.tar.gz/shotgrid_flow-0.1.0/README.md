# ShotGrid Flow

A simple Python package to establish connections to ShotGrid, whether from within a DCC (Digital Content Creation) application or standalone.

## Installation

```bash
pip install flow
```

Or to install from the source directory:

```bash
pip install -e .
```

## Usage

### Basic Usage

```python
from flow import Flow

# Connect using the current desktop user
flow = Flow.connect(user=True)

# Use the Shotgrid API
projects = flow.api.find("Project", [], ["name"])
print(projects)
```

### Connect With Script Key

```python
from flow import Flow

# Connect using a script key (environment variable SCRIPT_KEY_NUKE must be set)
flow = Flow.connect(script_key="NUKE")

# Use the Shotgrid API
projects = flow.api.find("Project", [], ["name"])
print(projects)
```

### Using with .env file
Create a .env file in your project root:

```
SHOTGUN_HOST=https://your-studio.shotgunstudio.com
SCRIPT_KEY_NUKE=your-api-key-here
```
The package will automatically find and load this file when you call Flow.connect().
You can also specify a different path to your .env file:

```
flow = Flow.connect(script_key="NUKE", dotenv_path="/path/to/your/.env")
```

```
### Connect From a Path

```python
from flow import Flow

# Connect using a path inside a project
flow = Flow.connect(user=True, path="/path/to/project")

# Use the toolkit
current_context = flow.tk.context_from_path(path)
print(current_context)
```

## Requirements

- Python 3.6+
- Shotgrid Toolkit (sgtk)

## License

MIT License
