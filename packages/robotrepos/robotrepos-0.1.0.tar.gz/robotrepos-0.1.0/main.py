import hashlib
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List

import git
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

mcp = FastMCP("robotrepos")


def clone_repo(repo_url: str) -> str:
    """Clone a repository and return the path. If repository is already cloned in temp directory, reuse it."""
    # Create a deterministic directory name based on repo URL
    repo_hash = hashlib.sha256(repo_url.encode()).hexdigest()[:12]
    temp_dir = os.path.join(tempfile.gettempdir(), f"github_tools_{repo_hash}")

    # If directory exists and is a valid git repo, return it
    if os.path.exists(temp_dir):
        try:
            repo = git.Repo(temp_dir)
            if not repo.bare and repo.remote().url == repo_url:
                return temp_dir
        except:
            # If there's any error with existing repo, clean it up
            shutil.rmtree(temp_dir, ignore_errors=True)

    # Create directory and clone repository
    os.makedirs(temp_dir, exist_ok=True)
    try:
        git.Repo.clone_from(repo_url, temp_dir)
        return temp_dir
    except Exception as e:
        # Clean up on error
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise Exception(f"Failed to clone repository: {str(e)}")


def get_directory_tree(path: str, prefix: str = "") -> str:
    """Generate a tree-like directory structure string"""
    output = ""
    entries = os.listdir(path)
    entries.sort()

    for i, entry in enumerate(entries):
        if entry.startswith(".git"):
            continue

        is_last = i == len(entries) - 1
        current_prefix = "└── " if is_last else "├── "
        next_prefix = "    " if is_last else "│   "

        entry_path = os.path.join(path, entry)
        output += prefix + current_prefix + entry + "\n"

        if os.path.isdir(entry_path):
            output += get_directory_tree(entry_path, prefix + next_prefix)

    return output


@mcp.tool()
def git_directory_structure(repo_url: str) -> str:
    """
    Clone a Git repository and return its directory structure in a tree format.

    Args:
        repo_url: The URL of the Git repository

    Returns:
        A string representation of the repository's directory structure
    """
    try:
        # Clone the repository
        repo_path = clone_repo(repo_url)

        # Generate the directory tree
        tree = get_directory_tree(repo_path)
        return tree

    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def git_read_important_files(repo_url: str, file_paths: List[str]) -> dict[str, str]:
    """
    Read the contents of specified files in a given git repository.

    Args:
        repo_url: The URL of the Git repository
        file_paths: List of file paths to read (relative to repository root)

    Returns:
        A dictionary mapping file paths to their contents
    """
    try:
        # Clone the repository
        repo_path = clone_repo(repo_url)
        results = {}

        for file_path in file_paths:
            full_path = os.path.join(repo_path, file_path)

            # Check if file exists
            if not os.path.isfile(full_path):
                results[file_path] = f"Error: File not found"
                continue

            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    results[file_path] = f.read()
            except Exception as e:
                results[file_path] = f"Error reading file: {str(e)}"

        return results

    except Exception as e:
        return {"error": f"Failed to process repository: {str(e)}"}


# @mcp.tool()
# def list_repos_in_config_file(config_file: str) -> List[str]:
#     """
#     List all GitHub repository URLs in a given configuration file.

#     Args:
#         config_file: Path to the configuration file that contains repository URLs
#     Returns:
#         A list of repository URLs found in the configuration file
#     """
#     try:
#         with open(config_file, 'r', encoding='utf-8') as f:
#             lines = f.readlines()

#         # Extract URLs (assuming they start with "http" or "https")
#         urls = [line.strip() for line in lines if line.strip().startswith(("http://", "https://"))]
#         return urls

#     except Exception as e:
#         return [f"Error reading config file: {str(e)}"]


def main():
    """Entry point for the robotrepos MCP server when run via uvx."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
