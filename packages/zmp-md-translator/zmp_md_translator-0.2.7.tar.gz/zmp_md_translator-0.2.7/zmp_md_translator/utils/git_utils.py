"""Git utilities for managing repositories."""

import os
from git import Repo


def clone_or_update_repo(repo_url: str, local_path: str, branch: str = "main"):
    """Clone or update a git repository.

    Args:
        repo_url: URL of the git repository
        local_path: Local path to clone to
        branch: Branch to checkout (default: main)
    """
    if os.path.exists(local_path):
        repo = Repo(local_path)
        origin = repo.remotes.origin
        origin.pull()
        if repo.active_branch.name != branch:
            repo.git.checkout(branch)
    else:
        Repo.clone_from(repo_url, local_path, branch=branch)


def find_markdown_files(root_dir: str):
    """Find all markdown files in the given directory recursively.

    Args:
        root_dir: Root directory to search for markdown files

    Returns:
        List of paths to markdown files
    """
    md_files = []
    for dirpath, _, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith((".md", ".mdx")):
                md_files.append(os.path.join(dirpath, file))
    return md_files


def commit_and_push_changes(local_path: str, target_language: str):
    """Commit and push translated files to remote repository.

    Args:
        local_path: Local repository path
        target_language: Target language for commit message
    """
    repo = Repo(local_path)
    repo.git.add(A=True)
    commit_message = f"Translated markdown files to {target_language}"
    repo.index.commit(commit_message)
    repo.remotes.origin.push()
