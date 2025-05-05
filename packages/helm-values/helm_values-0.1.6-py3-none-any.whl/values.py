import yaml
import os
import git
import tempfile
import re
from typing import Dict, Any, Tuple
import json


def deep_merge(source: Dict[str, Any], destination: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries
    """
    for key, value in source.items():
        if (
            isinstance(value, dict)
            and key in destination
            and isinstance(destination[key], dict)
        ):
            # If both values are dictionaries, recursively merge them
            destination[key] = deep_merge(value, destination[key])
        else:
            # Otherwise, source value overrides destination
            destination[key] = value
    return destination


def load_helm_values(
    chart_name: str,
    cluster_name: str,
    common_values_path: str,
    cluster_values_path: str,
    *additional_files: str,
) -> Dict[str, Any]:
    """
    Load and merge Helm values files, later files are more important
    """
    paths = [
        # The default values of the Helm Chart
        os.path.join("charts", chart_name, "values.yaml"),
        # Common values for all clusters
        os.path.join(common_values_path, "common.yaml"),
        # Chart values for all Cluster
        os.path.join(common_values_path, f"{chart_name}.yaml"),
        # Common values for this Cluster
        os.path.join(cluster_values_path, cluster_name, "common.yaml"),
        # Chart values for this Cluster
        os.path.join(cluster_values_path, cluster_name, f"{chart_name}.yaml"),
        *additional_files,
    ]

    result: Dict[str, Any] = {}

    for path in paths:
        if os.path.exists(path):
            with open(path, "r") as f:
                values = yaml.safe_load(f) or {}
                result = deep_merge(values, result)

    return result


# def parse_git_url(url: str) -> tuple[str, str]:
#     """
#     Parse a Git URL in the format https://git.domain.com/username/repo.git/path
#     and return the repo URL and path within the repo
#     """
#     # Pattern to match a Git URL with an optional path
#     pattern = r"(https?://[^/]+/[^/]+/[^/]+\.git)(?:/(.*))?$"
#     match = re.match(pattern, url)

#     if not match:
#         raise ValueError(f"Invalid Git URL format: {url}")

#     repo_url = match.group(1)
#     path_in_repo = match.group(2) or ""

#     return repo_url, path_in_repo


# def load_helm_values_git(
#     git_repo: str,
#     git_ref: str = "HEAD",
#     file_paths: list[str] = None,
# ) -> dict[str, any]:
#     """
#     Load and merge Helm values files from a Git repository

#     Args:
#         git_repo: Git repository URL ending with .git
#         git_ref: Git reference (branch, tag, commit) to use
#         file_paths: Paths to files within the repo, in order of increasing precedence
#                    (later files override values from earlier files)

#     Returns:
#         Merged dictionary of values from all existing files
#     """
#     if not git_repo.endswith(".git"):
#         raise ValueError(f"Git repository URL must end with .git: {git_repo}")

#     with tempfile.TemporaryDirectory() as temp_dir:
#         # Clone the repository
#         repo = git.Repo.clone_from(git_repo, temp_dir)
#         repo.git.checkout(git_ref)

#         result = {}

#         # Process files in order, so later files take precedence
#         for file_path in file_paths:
#             # Handle full Git URLs by extracting the path
#             if file_path.startswith(("http://", "https://")):
#                 _, path_in_repo = parse_git_url(file_path)
#                 full_path = os.path.join(temp_dir, path_in_repo)
#             else:
#                 full_path = os.path.join(temp_dir, file_path)

#             if os.path.exists(full_path):
#                 with open(full_path, "r") as f:
#                     values = yaml.safe_load(f) or {}
#                     # We merge the previous result INTO the current values
#                     # This ensures later files take precedence
#                     values = deep_merge(result, values)
#                     result = values

#         return result


def load_git_values(
    git_repo: str,
    git_ref: str = "HEAD",
    file_paths: list[str] = None,
) -> dict[str, any]:
    """
    Load and merge Helm values files from a Git repository

    Args:
        git_repo: Git repository URL ending with .git
        git_ref: Git reference (branch, tag, commit) to use
        file_paths: Paths to files within the repo, in order of increasing precedence

    Returns:
        Merged dictionary of values from all existing files
    """
    if not git_repo.endswith(".git"):
        raise ValueError(f"Git repository URL must end with .git: {git_repo}")

    with tempfile.TemporaryDirectory() as temp_dir:
        repo = git.Repo.clone_from(git_repo, temp_dir)
        repo.git.checkout(git_ref)

        result = {}

        for file_path in file_paths:
            full_path = os.path.join(temp_dir, file_path)
            if os.path.exists(full_path):
                with open(full_path, "r") as f:
                    values = yaml.safe_load(f) or {}
                    # We merge the previous result INTO the current values
                    # This ensures later files take precedence
                    values = deep_merge(result, values)
                    result = values

        return result


def load_values_from_parameters(
    global_values_repo: str = os.environ["ARGOCD_ENV_GLOBAL_VALUES_REPO"],
    infra_values_repo: str = os.environ["ARGOCD_ENV_INFRA_VALUES_REPO"],
    default_values_path: str = None,
):

    parameters = json.loads(os.environ["ARGOCD_APP_PARAMETERS"])

    # Extract array for "global-values-files"
    global_values_files = next(
        (item["array"] for item in parameters if item["name"] == "global-values-files"),
        [],
    )

    # Extract array for "infra-values-files"
    infra_values_files = next(
        (item["array"] for item in parameters if item["name"] == "infra-values-files"),
        [],
    )

    # Load the global values from Git
    global_values = load_git_values(
        git_repo=global_values_repo, file_paths=global_values_files
    )

    # Load the infra values from Git
    infra_values = infra_values_repo = load_git_values(
        git_repo=infra_values_repo, file_paths=infra_values_files
    )

    # Merge global_values and infra_values,
    # the last file is more important the the first and can override some values
    values = deep_merge(global_values, infra_values)

    # If default_values_path is passed, merge this with the other values
    # The other values are more important
    if default_values_path:
        with open(default_values_path, "r") as f:
            default_values = yaml.safe_load(f) or {}

        values = deep_merge(default_values, values)

    return values
