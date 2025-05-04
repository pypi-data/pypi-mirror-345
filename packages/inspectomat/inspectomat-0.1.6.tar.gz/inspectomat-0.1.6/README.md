# Inspectomat Toolbox

A comprehensive set of utilities for cleaning up files and directories, comparing folders, managing projects, and more. Inspectomat helps you organize and maintain your file system efficiently.

## Quick Start

We provide easy-to-use launcher scripts that automatically set up a virtual environment and install the latest version of Inspectomat:

### Linux/macOS:
```bash
# Make the script executable (first time only)
chmod +x run.sh

# Run Inspectomat
./run.sh
```

### Windows (Command Prompt):
```
run.bat
```

### Windows (PowerShell):
```powershell
.\run.ps1
```

These scripts will:
1. Check if Python is installed
2. Create a virtual environment if needed
3. Install or update Inspectomat to the latest version
4. Launch the tool with any arguments you provide

## Manual Installation

If you prefer to install manually:

```bash
# Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install from PyPI
pip install inspectomat

# Or install in development mode from source
pip install -e .
```

## Usage

After installation, you can use the inspectomat tool in three ways:

### Interactive Shell

Simply run the `inspectomat` command without arguments to start the interactive shell:

```bash
inspectomat
# or explicitly
inspectomat -i
```

This will show a prompt where you can type commands. Use `list` to see all available commands:

```
inspectomat> list
```

### Direct Command Execution

You can run specific commands directly:

```bash
inspectomat cleanemptydirs
inspectomat findbigfiles
inspectomat comparefolders
# etc.
```

Use `inspectomat -l` or `inspectomat --list` to see all available commands.

### Scriptable Shell Interface

You can also use the scriptable shell interface to call specific functions with parameters:

```bash
# List all available commands
inspectomat -l

# Call a specific function in a module
inspectomat cleanemptydirs -f find_empty_dirs -p /path/to/directory

# Call with named parameters
inspectomat findbigfiles -f find_big_files -p min_size=1000000 dir_path=/home/user/Documents
```

Command line arguments:
- `-f, --function`: Function to call within the module
- `-p, --params`: Parameters for the function (space-separated, use key=value format for named parameters)
- `-i, --interactive`: Start interactive shell
- `-l, --list`: List available commands
- `-y, --yes`: Automatically answer yes to all prompts
- `--repair`: Check and repair dependencies

## Dependency Management and Self-Repair

The inspectomat package includes a self-repair mechanism that can automatically detect and install missing dependencies. If a command fails due to a missing dependency, the system will offer to install it for you.

To manually check and install dependencies:

```bash
# Interactive mode (will ask for confirmation)
inspectomat repair

# Non-interactive mode (automatically installs dependencies)
inspectomat repair -y
```

In the interactive shell, you can use the `repair` command:

```
inspectomat> repair
```

The system will automatically detect the following types of dependencies:
- Core dependencies required for basic functionality
- Optional dependencies required for specific modules

If you want to install all optional dependencies at once:

```bash
pip install -e .[full]
```

## Tools Overview

Inspectomat includes the following tools:

- **clean_empty_dirs** – Remove empty directories recursively.
- **find_big_files** – Find and list the largest files in a directory tree.
- **compare_folders** – Compare contents of two folders and show differences.
- **compare_equal_folders** – Compare contents of folders up to a chosen depth, log equal folders, and show progress.
- **batch_compare_folders** – Batch compare multiple folders and show results.
- **move_batch_duplicates** – Move detected duplicate folders/files in batch mode.
- **move_duplicate_folders** – Interactively move duplicate folders to a specified location.
- **move_nonidentical_files** – Identify and move files that are not identical across folders.
- **resolve_folder_differences** – Powerful, interactive N-way folder comparison and resolution tool.
- **git_projects_audit** – Audit local git projects, check remote existence and equality, log results.
- **find_similar_projects** – Find groups of project folders with similar structure for comparison.
- **media_deduplicate** – Find and manage duplicate media files based on content.

## resolve_folder_differences

An interactive script for comparing subfolders (to a chosen depth) across multiple base directories. Quickly detect and resolve differences in project structures, even for large sets.

### Key features:
- **Compare N folders at once** – Enter any number of directory paths to compare.
- **In-depth analysis** – Compares all files in subfolders (to chosen depth), detects missing and differing files.
- **Difference table** – Clear, wide table with full folder paths and file modification dates (oldest/newest highlighted). Only shows files that differ.
- **Interactive menu** – For each group of differing subfolders you can: delete a selected folder, move a selected folder to a `different` subfolder in another and delete the original, skip, or exit.
- **Support for .ignore** – An `.ignore` file (created automatically) allows excluding directories and files from comparisons (e.g., `.git`, `.idea`, `venv`).
- **Colorful, readable interface** – Colors for headers, dates, menu, progress bar.
- **Progress bar** – Shows scanning and comparison progress.
- **No differences notification** – Clear message if no differences are found.
- **Adjustable scanning depth** – Choose the depth at startup (default is 2).

### Quick Start

1. **Add directories to compare:**
   ```bash
   python resolve_folder_differences.py
   ```
   Enter the paths to the directories, followed by an empty line. You will be asked for the scanning depth.

2. **Customize exclusions:**
   Edit the `.ignore` file in the toolbox directory to exclude irrelevant directories/files.

3. **Proceed with the menu:**
   The script will display differences and ask for action for each group of subfolders.

### Example Exclusion

`.ignore` file (automatically created with `.git` entry):
```
.git
.idea
venv
*.log
```

## find_similar_projects

This script helps you automatically find similar projects in a large directory structure. It simplifies preparing a list of paths for further comparison.

### Features:
- You specify the starting path and scanning depth (default is 2).
- The script finds folders that look like projects (e.g., contain `setup.py`, `.git`, `package.json`, etc.).
- It groups projects with very similar file and folder structures.
- For each path, it shows the number of files (recursive) and total folder size.
- The result is groups of paths that you can provide to `resolve_folder_differences.py` for comparison.

### Example Usage
```
python find_similar_projects.py
Enter root path to search for projects: /home/tom/Projects
How deep should be scanned? (default 2): 2

Groups of similar projects:

Group 1:
  /home/tom/Projects/app1   files:   123   size: 12.3 MB
  /home/tom/Projects/app2   files:   121   size: 12.2 MB

You can use the above paths as input to resolve_folder_differences.py for comparison.
```

### Tips
- The deeper the scan, the more potential projects will be found (but slower).
- You can edit the `.ignore` file to exclude directories like `.git`, `.idea`, `node_modules`, etc.

## Development

### Project Structure

```
inspectomat/
├── inspectomat/             # Package directory
│   ├── __init__.py          # Package initialization
│   ├── _version.py          # Version information
│   ├── cli.py               # Command-line interface
│   ├── clean_empty_dirs.py  # Utility modules
│   ├── ...
├── tests/                   # Test directory
│   ├── __init__.py
│   ├── test_cli.py          # Tests for CLI
│   ├── ...
├── setup.py                 # Package setup file
├── pyproject.toml           # Modern Python packaging configuration
├── run.sh                   # Linux/macOS launcher script
├── run.bat                  # Windows CMD launcher script
├── run.ps1                  # Windows PowerShell launcher script
├── README.md                # This documentation
└── LICENSE                  # License file
```

### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## Version History

See the [CHANGELOG.md](CHANGELOG.md) file for details on version history and changes.
