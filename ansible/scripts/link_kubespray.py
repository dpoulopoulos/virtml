#!/usr/bin/env python3

# Create symlinks for Kubespray inventory `group_vars` files to the project's
# inventory directory. This script is intended to be run from the project's
# Ansible directory and assumes the Kubespray repository is cloned in the
# `kubespray` directory at the same level as the project's Ansible directory.
#
# The script should be run every time the Kubespray version is upgraded to
# ensure the project's inventory directory is up-to-date with the latest
# `group_vars` files from Kubespray.

import os
from pathlib import Path


# Define the base source directory and destination directory
script_path = Path(__file__)
repo_dir = script_path.parent.parent.parent  # Go up from scripts directory
inventory_dir = repo_dir / "ansible" / "inventory"
kubespray_dir = repo_dir / "ansible" / "kubespray"
base_source_dir = kubespray_dir / "inventory" / "sample" / "group_vars"
dest_dir = inventory_dir / "group_vars"


def create_symlink(source_path: Path, dest_path: Path, filename: str) -> None:
    """ Create a symlink for the given file in the destination directory.

    Args:
        source_path (str): The full path to the source file.
        dest_path (str): The full path to the destination directory.
        filename (str): The name of the file to create a symlink for.
    
    Returns:
        None
    """
    # If the filename is `all.yml` and the source directory is `all`,
    # rename the symlink to `kubespray.yaml` to avoid conflicts with the
    # `all.yaml` file in the project's inventory `group_vars`.
    # The name `kubespray` is directly linked to the project's inventory
    # group with the same name.
    if filename == 'all.yml' and os.path.basename(os.path.dirname(source_path)) == 'all':
        symlink_name = 'kubespray.yml'
    else:
        symlink_name = filename
    
    dest_symlink = os.path.join(dest_path, symlink_name)
    
    if os.path.exists(dest_symlink) or os.path.islink(dest_symlink):
        os.remove(dest_symlink)
    
    os.symlink(source_path, dest_symlink)

    print(f"Created symlink: {dest_symlink} -> {source_path}")


os.makedirs(dest_dir, exist_ok=True)

# Handle files in the base directory separately
for filename in os.listdir(base_source_dir):
    source_file = base_source_dir / filename
    if os.path.isfile(source_file):
        create_symlink(source_file, dest_dir, filename)

for dirpath, dirnames, filenames in os.walk(base_source_dir):
    if dirpath == base_source_dir:
        continue

    # Determine a subdirectory name for symlinks to maintain structure
    subdir_name = os.path.basename(dirpath)
    if subdir_name == "all":
        subdir_name = "kubespray"
    subdir_dest = dest_dir / subdir_name
    os.makedirs(subdir_dest, exist_ok=True)

    # Create symlinks for files in this directory
    for filename in filenames:
        source_file = Path(dirpath) / filename
        create_symlink(source_file, subdir_dest, filename)

print("Symlinks creation process completed.")
