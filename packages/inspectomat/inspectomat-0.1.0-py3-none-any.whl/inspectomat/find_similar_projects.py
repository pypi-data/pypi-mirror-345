import os
import sys
from collections import defaultdict
from difflib import SequenceMatcher

BOLD = '\033[1m'
CYAN = '\033[36m'
RESET = '\033[0m'

# Heuristic: treat as 'project' if folder contains e.g. setup.py, package.json, main.py, .git, or >N files/subdirs
PROJECT_HINTS = [
    'setup.py', 'pyproject.toml', 'package.json', 'main.py', 'README.md', '.git', 'requirements.txt',
    'index.html', 'Makefile', 'pom.xml', 'build.gradle', 'Cargo.toml', 'composer.json', 'Gemfile', 'go.mod'
]
MIN_ITEMS = 3  # minimal number of files/subdirs to treat as a possible project


def is_project_folder(path):
    try:
        items = os.listdir(path)
    except Exception:
        return False
    if len(items) >= MIN_ITEMS:
        for hint in PROJECT_HINTS:
            if hint in items:
                return True
    return False

def collect_projects(root, max_depth=2):
    projects = []
    for dirpath, dirs, files in os.walk(root):
        rel = os.path.relpath(dirpath, root)
        if rel == ".":
            cur_depth = 0
        else:
            cur_depth = rel.count(os.sep) + 1
        if cur_depth > max_depth:
            dirs[:] = []
            continue
        if is_project_folder(dirpath):
            projects.append(dirpath)
            dirs[:] = []
    return projects

def folder_signature(path):
    """Return a sorted tuple of (relative) file and subdir names for structure comparison."""
    try:
        items = os.listdir(path)
    except Exception:
        return tuple()
    return tuple(sorted(items))

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def group_similar_projects(projects, threshold=0.7):
    """Group projects by similar structure (file/dir names)."""
    sig_map = {p: folder_signature(p) for p in projects}
    groups = []
    used = set()
    for p1 in projects:
        if p1 in used:
            continue
        group = [p1]
        used.add(p1)
        for p2 in projects:
            if p2 in used or p1 == p2:
                continue
            sim = similarity(str(sig_map[p1]), str(sig_map[p2]))
            if sim >= threshold:
                group.append(p2)
                used.add(p2)
        if len(group) > 1:
            groups.append(group)
    return groups

def folder_stats(path):
    total_files = 0
    total_size = 0
    for root, dirs, files in os.walk(path):
        total_files += len(files)
        for f in files:
            try:
                total_size += os.path.getsize(os.path.join(root, f))
            except Exception:
                pass
    return total_files, total_size

def format_size(num):
    for unit in ['B','KB','MB','GB','TB']:
        if num < 1024.0:
            return f"{num:.1f} {unit}"
        num /= 1024.0
    return f"{num:.1f} PB"

def main():
    print(f"{BOLD}Find similar projects by structure{RESET}")
    path = input("Enter root path to search for projects: ").strip()
    if not path or not os.path.isdir(path):
        print("Invalid path.")
        sys.exit(1)
    try:
        max_depth = int(input("How deep should be scanned? (default 2): ").strip() or 2)
    except ValueError:
        max_depth = 2
    print(f"Scanning for candidate project folders in {CYAN}{path}{RESET} up to level {max_depth} ...")
    projects = collect_projects(path, max_depth)
    print(f"Found {len(projects)} candidate projects.")
    print("Grouping by similar structure...")
    groups = group_similar_projects(projects)
    if not groups:
        print("No similar project groups found.")
        return
    print(f"\n{BOLD}Groups of similar projects:{RESET}")
    for idx, group in enumerate(groups, 1):
        print(f"\n{BOLD}Group {idx}:{RESET}")
        for p in group:
            nfiles, nbytes = folder_stats(p)
            print(f"  {CYAN}{p}{RESET}   files: {nfiles:5d}   size: {format_size(nbytes)}")
    print(f"\nYou can use the above paths as input to resolve_folder_differences.py for comparison.")

if __name__ == "__main__":
    main()
